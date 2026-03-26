"""
File tree widget for TUI.

MUST: lazy load nodes, virtual scrolling
NEVER: preload entire repo
"""

from textual.reactive import reactive
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from memobase.tui.controller import TUIController
from memobase.tui.state import TUIState


class FileTree(Tree):
    """File tree widget with lazy loading."""
    
    DEFAULT_CSS = """
    FileTree {
        width: 100%;
        height: 100%;
        border: solid $primary;
        background: $surface-darken-1;
    }
    
    FileTree .tree--cursor {
        background: $primary-darken-2;
    }
    
    FileTree .tree--highlight {
        background: $primary-darken-1;
    }
    """
    
    def __init__(self, state: TUIState, controller: TUIController, **kwargs) -> None:
        """Initialize file tree.
        
        Args:
            state: TUI state manager
            controller: TUI controller
        """
        super().__init__("📁 Project", **kwargs)
        self.state = state
        self.controller = controller
        self._loaded_nodes: set = set()
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Load root level only
        self._load_root()
        
        # Watch for file tree data changes
        self.watch(self.state, "file_tree_data", self._on_file_tree_changed)
    
    def _load_root(self) -> None:
        """Load root level directories."""
        # Clear existing
        self.root.remove_children()
        
        # Get file tree data from controller
        file_tree = self.controller.get_file_tree()
        
        # Group by directory
        directories: dict = {}
        files = []
        
        for item in file_tree:
            path = item["path"]
            parts = path.split("/")
            
            if len(parts) > 1:
                # In a subdirectory
                dir_name = parts[0]
                if dir_name not in directories:
                    directories[dir_name] = []
                directories[dir_name].append(item)
            else:
                # Root level file
                files.append(item)
        
        # Add directories as expandable nodes
        for dir_name, dir_files in sorted(directories.items()):
            dir_node = self.root.add(f"📁 {dir_name}", data={"type": "directory", "name": dir_name})
            dir_node.allow_expand = True
            
            # Store files for lazy loading
            dir_node.data["files"] = dir_files
        
        # Add root level files
        for file_item in sorted(files, key=lambda x: x["name"]):
            self.root.add(f"📄 {file_item['name']}", data={"type": "file", "path": file_item["path"]})
    
    def _on_file_tree_changed(self) -> None:
        """Handle file tree data changes."""
        self._load_root()
    
    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Handle node expansion - lazy load children."""
        node = event.node
        
        if node.data.get("type") == "directory":
            # Lazy load directory contents
            self._load_directory(node)
    
    def _load_directory(self, node: TreeNode) -> None:
        """Lazy load directory contents.
        
        Args:
            node: Directory tree node
        """
        node_id = id(node)
        
        # Check if already loaded
        if node_id in self._loaded_nodes:
            return
        
        # Mark as loaded
        self._loaded_nodes.add(node_id)
        
        # Get stored files
        files = node.data.get("files", [])
        
        # Add files as children
        for file_item in sorted(files, key=lambda x: x["name"]):
            node.add(f"📄 {file_item['name']}", data={"type": "file", "path": file_item["path"]})
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection."""
        node = event.node
        
        if node.data.get("type") == "file":
            file_path = node.data.get("path")
            if file_path:
                # Update state
                self.state.set_file(file_path)
                
                # Emit event
                from memobase.tui.event_bus import TypedEventBus
                if isinstance(self.state, TUIState):
                    # Access event bus through app
                    pass  # Event handling done through callbacks
    
    def on_key(self, event) -> None:
        """Handle key events for navigation."""
        if event.key == "enter":
            # Select current node
            if self.cursor_node:
                self.on_tree_node_selected(type("Event", (), {"node": self.cursor_node})())
        elif event.key == "space":
            # Toggle expansion
            if self.cursor_node:
                if self.cursor_node.allow_expand:
                    self.cursor_node.toggle()


class VirtualFileTree(Widget):
    """Virtual scrolling file tree for large repositories."""
    
    def __init__(self, state: TUIState, controller: TUIController, **kwargs) -> None:
        """Initialize virtual file tree.
        
        Args:
            state: TUI state manager
            controller: TUI controller
        """
        super().__init__(**kwargs)
        self.state = state
        self.controller = controller
        self._visible_range = (0, 20)  # Start and end of visible range
        self._item_height = 1
    
    def render(self) -> str:
        """Render visible portion of file tree."""
        file_tree = self.state.file_tree_data
        start, end = self._visible_range
        
        visible_items = file_tree[start:end]
        
        lines = []
        for item in visible_items:
            icon = "📁" if item.get("type") == "directory" else "📄"
            lines.append(f"{icon} {item['name']}")
        
        return "\n".join(lines)
    
    def scroll_up(self) -> None:
        """Scroll up."""
        start, end = self._visible_range
        if start > 0:
            self._visible_range = (start - 1, end - 1)
            self.refresh()
    
    def scroll_down(self) -> None:
        """Scroll down."""
        start, end = self._visible_range
        file_count = len(self.state.file_tree_data)
        
        if end < file_count:
            self._visible_range = (start + 1, end + 1)
            self.refresh()
