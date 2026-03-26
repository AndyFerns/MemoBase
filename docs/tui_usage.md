# TUI Usage Documentation

Terminal User Interface for MemoBase.

## Launching TUI

```bash
memobase tui
memobase tui --repo /path/to/project
```

## Interface Layout

```
╔══════════════════════════════════════════╗
║ MemoBase          Files: 150 | Mode: MEM ║  <- Header
╠═══════════════════╦══════════════════════╣
║ 📁 src/           ║ Memory View           ║
║   📄 main.py      ║                       ║  <- File Tree | Main Panel
║   📄 utils.py     ║ function hello()      ║
║ 📁 tests/         ║   at src/main.py:15   ║
║   📄 test.py      ║                       ║
╠═══════════════════╩══════════════════════╣
║ /query                                      ║  <- Command Bar
╠══════════════════════════════════════════╣
║ [MEMORY] V:N | Ready                      ║  <- Status Bar
╚══════════════════════════════════════════╝
```

## Views

### Memory View (Default)

Shows memory unit information for selected file.

**Displayed:**
- Symbol information (name, type, signature)
- Documentation
- Relationships
- Content preview
- Metadata

### Graph View

Shows code relationships for selected file.

**Displayed:**
- Connected nodes
- Relationship types
- Depth-limited traversal
- Edge weights

### Analysis View

Shows code analysis findings.

**Displayed:**
- Security issues
- Quality issues
- Performance issues
- Severity levels

### Query View

Shows query results.

**Displayed:**
- Search results
- Ranked by relevance
- File locations
- Content previews

## Keybindings

### Navigation

| Key | Action |
|-----|--------|
| `j` | Move down |
| `k` | Move up |
| `h` | Move left (collapse) |
| `l` | Move right (expand) |
| `g` | Go to top |
| `G` | Go to bottom |
| `Enter` | Select item |
| `Space` | Toggle expansion |

### View Switching

| Key | View |
|-----|------|
| `m` | Memory view |
| `g` | Graph view |
| `a` | Analysis view |
| `/` | Query mode |

### Query & Commands

| Key | Action |
|-----|--------|
| `/` | Enter query mode |
| `:` | Enter command mode |
| `Esc` | Cancel/Exit mode |
| `Return` | Submit query/command |

### Controls

| Key | Action |
|-----|--------|
| `v` | Toggle verbose (cycles: Q→N→V→D) |
| `r` | Refresh data |
| `R` | Full rebuild |
| `q` | Quit |
| `?` | Show help |

### Graph Controls

| Key | Action |
|-----|--------|
| `+` | Expand graph depth |
| `-` | Collapse graph depth |
| `d` | Set graph depth (prompt) |
| `n` | Next node |
| `p` | Previous node |

## Commands

Type `:` to enter command mode.

### Navigation Commands

```
:memory    Switch to memory view
:graph     Switch to graph view
:analysis  Switch to analysis view
:query     Switch to query view
```

### Configuration Commands

```
:verbose N    Set verbosity (0-3)
:depth N      Set graph depth (1-10)
:refresh      Refresh data
:rebuild      Full rebuild
```

### Action Commands

```
:find SYMBOL      Find symbol
:deps FILE        Show dependencies
:callers FUNC      Show callers
:implementations  Show implementations
```

### System Commands

```
:quit     Exit TUI
:help     Show help
:version  Show version
:status   Show status
```

## Modes

### Query Mode

Press `/` to enter query mode.

**Syntax:**
- `function name` - Search for function
- `class User` - Search for class
- `file:auth.py` - Filter by file
- `type:function` - Filter by type

**Examples:**
```
/login
class UserController
type:function file:auth.py
```

### Command Mode

Press `:` to enter command mode.

**Autocomplete:**
- Tab to complete commands
- Up/Down for history

## Status Bar

Shows current state:

```
[MEMORY] V:N | Ready
[GRAPH]  V:V | Depth: 3
[ANALYSIS] V:D | 15 findings
```

**Indicators:**
- Mode: MEMORY, GRAPH, ANALYSIS, QUERY
- Verbosity: Q (Quiet), N (Normal), V (Verbose), D (Debug)
- Status message

## File Tree

### Navigation
- `j/k` to move up/down
- `l` or `→` to expand directory
- `h` or `←` to collapse directory
- `Enter` to select file

### Features
- Lazy loading
- Virtual scrolling
- Expand/collapse
- Icons: 📁 (directory), 📄 (file)

## Query Results

### Display
1. Numbered list
2. Symbol name and type
3. File location
4. Preview

### Navigation
- `j/k` to navigate results
- `Enter` to open result
- `1-9` jump to result N

## Graph Display

### Layout
- Center: Selected node
- Outward: Connected nodes
- Depth-limited (configurable)

### Node Types
- 📦 Class
- 🔧 Function
- 📋 Method
- 🔗 Interface
- 📄 File

### Edge Types
- → calls
- ⇢ imports
- ⤁ inherits
- ⊃ contains

## Tips

### Performance
- Use `v` to reduce verbosity for speed
- Graph depth affects rendering (default: 3)
- Large repos use virtual scrolling

### Navigation
- `gg` to go to top
- `G` to go to bottom
- `Ctrl+f` page down
- `Ctrl+b` page up

### Search
- Use `/` for quick search
- Use filters for precise results
- Query history preserved

## Workflows

### Explore Codebase

1. Launch TUI: `memobase tui`
2. Navigate file tree with `j/k`
3. Select file with `Enter`
4. View memory with `m`
5. View graph with `g`
6. Search with `/`

### Find Dependencies

1. Select file in tree
2. Press `g` for graph view
3. Press `+` to expand depth
4. Navigate with `n/p`

### Code Analysis

1. Press `a` for analysis view
2. Review findings
3. Press numbers `1-9` to jump
4. Press `r` to refresh

## Troubleshooting

### Slow Performance
- Reduce verbosity: `:verbose 0`
- Decrease graph depth: `:depth 2`
- Use filters to narrow results

### Display Issues
- Resize terminal window
- Use `--no-color` if needed
- Check terminal compatibility

### Navigation Stuck
- Press `Esc` to reset
- Use `q` to quit and restart
- Check if process is running
