"""
Main layout for TUI.

Defines the overall screen layout structure.
"""

from textual.containers import Horizontal, Vertical
from textual.layout import Layout


class MainLayout:
    """Main layout structure for MemoBase TUI."""
    
    @staticmethod
    def create_layout() -> Layout:
        """Create the main application layout.
        
        Returns:
            Textual Layout instance
        """
        # Layout structure:
        # +---------------------------+
        # |         Header            |
        # +--------+-------------+------+
        # | File   |   Main       |     |
        # | Tree   |   Panel      |     |
        # |        |              |     |
        # +--------+-------------+------+
        # |      Command Bar        |
        # +---------------------------+
        # |       Status Bar          |
        # +---------------------------+
        
        # Note: In Textual, this is typically defined in CSS
        # This class provides a programmatic way to reference the layout
        
        return Layout()
    
    @staticmethod
    def get_css() -> str:
        """Get the CSS for the main layout.
        
        Returns:
            CSS string defining the layout
        """
        return """
        Screen {
            layout: grid;
            grid-size: 1;
            grid-rows: auto 1fr auto;
        }
        
        #header {
            height: 3;
            dock: top;
        }
        
        #main-container {
            layout: grid;
            grid-size: 2;
            grid-columns: 25% 1fr;
            height: 1fr;
        }
        
        #file-tree {
            width: 100%;
            height: 100%;
            border: solid $primary;
        }
        
        #main-panel {
            width: 100%;
            height: 100%;
            border: solid $primary;
        }
        
        #command-bar {
            height: 1;
            dock: bottom;
        }
        
        #status-bar {
            height: 1;
            dock: bottom;
        }
        """


class ResponsiveLayout(MainLayout):
    """Responsive layout that adapts to screen size."""
    
    @staticmethod
    def get_css(screen_width: int = 80) -> str:
        """Get responsive CSS based on screen width.
        
        Args:
            screen_width: Screen width in characters
            
        Returns:
            CSS string for the layout
        """
        # Adjust layout based on screen width
        if screen_width < 60:
            # Compact layout - hide file tree by default
            return """
            Screen {
                layout: grid;
                grid-size: 1;
                grid-rows: auto 1fr auto;
            }
            
            #header {
                height: 2;
                dock: top;
            }
            
            #main-container {
                layout: vertical;
                height: 1fr;
            }
            
            #file-tree {
                width: 100%;
                height: 20%;
                display: none;
            }
            
            #main-panel {
                width: 100%;
                height: 100%;
            }
            
            #command-bar {
                height: 1;
                dock: bottom;
            }
            
            #status-bar {
                height: 1;
                dock: bottom;
            }
            """
        elif screen_width < 100:
            # Medium layout - smaller file tree
            return """
            Screen {
                layout: grid;
                grid-size: 1;
                grid-rows: auto 1fr auto;
            }
            
            #header {
                height: 3;
                dock: top;
            }
            
            #main-container {
                layout: grid;
                grid-size: 2;
                grid-columns: 20% 1fr;
                height: 1fr;
            }
            
            #file-tree {
                width: 100%;
                height: 100%;
            }
            
            #main-panel {
                width: 100%;
                height: 100%;
            }
            
            #command-bar {
                height: 1;
                dock: bottom;
            }
            
            #status-bar {
                height: 1;
                dock: bottom;
            }
            """
        else:
            # Full layout - use default
            return MainLayout.get_css()
