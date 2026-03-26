# CLI Usage Documentation

Command-line interface for MemoBase.

## Global Options

All commands support these global flags:

```bash
-v, --verbose      Enable verbose output
-q, --quiet        Suppress non-error output
--json             Output in JSON format
--no-color         Disable colored output
-c, --config PATH  Configuration file path
--profile          Enable performance profiling
--debug            Enable debug mode
```

## Commands

### init

Initialize MemoBase in a repository.

```bash
memobase init [REPO_PATH] [options]
```

**Arguments:**
- `REPO_PATH`: Path to repository (default: current directory)

**Options:**
- `-f, --force`: Force initialization even if directory exists

**Examples:**
```bash
memobase init ./my-project
memobase init /path/to/repo --force
```

**Output:**
```
Initializing MemoBase in ./my-project
✓ MemoBase initialized successfully
Storage directory: .memobase
```

### build

Build the memory index for a repository.

```bash
memobase build [REPO_PATH] [options]
```

**Arguments:**
- `REPO_PATH`: Path to repository (default: current directory)

**Options:**
- `-p, --parallel N`: Number of parallel workers
- `-f, --force`: Force rebuild

**Examples:**
```bash
memobase build
memobase build ./my-project --parallel 8
memobase build --force
```

**Output:**
```
Building memory index for ./my-project
✓ Build completed successfully
Files processed: 150
Memory units: 450
Relationships: 890
Build time: 2.34s
```

### ask

Ask a question about your codebase.

```bash
memobase ask QUESTION [options]
```

**Arguments:**
- `QUESTION`: Question to ask

**Options:**
- `-r, --repo PATH`: Repository path
- `-l, --limit N`: Maximum number of results (default: 10)
- `--json`: Output in JSON format

**Examples:**
```bash
memobase ask "How does authentication work?"
memobase ask "Find all API endpoints" --limit 20
memobase ask "Show me the database models" --json
```

**Output:**
```
Query: How does authentication work?
Found 5 results

1. authenticate() (function) at auth.py:15
2. AuthMiddleware (class) at middleware.py:42
3. login() (method) at views.py:28
4. TokenValidator (class) at utils.py:156
5. require_auth() (decorator) at decorators.py:12

Execution time: 125.50ms
```

### query

Execute a search query.

```bash
memobase query QUERY [options]
```

**Arguments:**
- `QUERY`: Query string

**Options:**
- `-r, --repo PATH`: Repository path
- `-l, --limit N`: Maximum results (default: 10)
- `-o, --offset N`: Result offset
- `-f, --filter FILTERS`: Query filters (format: key:value,key2:value2)
- `--json`: Output in JSON format

**Examples:**
```bash
memobase query "function login"
memobase query "class User" --limit 5
memobase query "def" --filter file_type:python
memobase query "api" --filter "lang:python,type:function"
```

**Output:**
```
Query: function login
Found 3 results

1. login() (function) at views.py:15
2. login_user() (function) at auth.py:42
3. handle_login() (method) at handlers.py:28
```

### graph

Analyze code relationships.

```bash
memobase graph [options]
```

**Options:**
- `-r, --repo PATH`: Repository path
- `-s, --symbol SYMBOL`: Symbol to analyze
- `-d, --depth N`: Graph traversal depth (default: 3)
- `-o, --output PATH`: Output file
- `-f, --format TYPE`: Output format (text, dot, json)

**Examples:**
```bash
memobase graph
memobase graph --symbol "UserController" --depth 5
memobase graph --output graph.dot --format dot
memobase graph --symbol "authenticate" --format json
```

**Output:**
```
Analyzing code relationships...
✓ Graph analysis saved to graph.txt

Dependencies for UserController:
  → BaseController (inherits)
  → UserModel (uses)
  → AuthService (uses)
  → UserValidator (uses)
```

### analyze

Analyze code quality and security.

```bash
memobase analyze [options]
```

**Options:**
- `-r, --repo PATH`: Repository path
- `-t, --type TYPE`: Analysis type (all, security, quality, performance)
- `-o, --output PATH`: Output file
- `--json`: Output in JSON format

**Examples:**
```bash
memobase analyze
memobase analyze --type security
memobase analyze --type quality --output analysis.txt
memobase analyze --json
```

**Output:**
```
Running all analysis...
✓ Analysis completed

Summary:
Total findings: 15
CRITICAL: 0
HIGH: 2
MEDIUM: 5
LOW: 8
```

### update

Update memory index with changes.

```bash
memobase update [REPO_PATH] [options]
```

**Arguments:**
- `REPO_PATH`: Path to repository (default: current directory)

**Options:**
- `-f, --force`: Force full rebuild

**Examples:**
```bash
memobase update
memobase update ./my-project
memobase update --force
```

**Output:**
```
Updating memory index for ./my-project
✓ Update completed successfully
Files added: 3
Files modified: 12
Files deleted: 1
Update time: 0.85s
```

### tui

Launch the Terminal User Interface.

```bash
memobase tui [options]
```

**Options:**
- `-r, --repo PATH`: Repository path

**Examples:**
```bash
memobase tui
memobase tui --repo ./my-project
```

**Keybindings:**
- `j/k`: Move up/down
- `g`: Go to graph view
- `m`: Go to memory view
- `a`: Go to analysis view
- `/`: Enter query mode
- `:`: Enter command mode
- `v`: Toggle verbose
- `r`: Refresh
- `?`: Show help
- `q`: Quit

### doctor

Check system health and diagnose issues.

```bash
memobase doctor [REPO_PATH] [options]
```

**Arguments:**
- `REPO_PATH`: Path to repository (default: current directory)

**Options:**
- `-f, --fix`: Attempt to fix issues

**Examples:**
```bash
memobase doctor
memobase doctor --fix
memobase doctor ./my-project --fix
```

**Output:**
```
Running system diagnostics...
✓ Diagnostics complete

System Health Report
Overall Status: HEALTHY

✓ No issues found

Recommendations:
  • Consider increasing cache_size_mb for large repositories
```

### help

Get help for MemoBase commands.

```bash
memobase help [COMMAND]
```

**Arguments:**
- `COMMAND`: Command to get help for (optional)

**Examples:**
```bash
memobase help
memobase help build
memobase help query
```

## Query Language

### Search Syntax

Basic search:
```bash
memobase query "function name"
```

With filters:
```bash
memobase query "class" --filter type:class
memobase query "api" --filter file_type:python
memobase query "test" --filter "lang:python,size:>100"
```

Exact match:
```bash
memobase query "find:UserController"
```

Regular expressions (advanced):
```bash
memobase query "/def .*_.*/"
```

### Filter Reference

| Filter | Description | Example |
|--------|-------------|---------|
| `type` | Symbol type | `type:function` |
| `file_type` | File extension | `file_type:python` |
| `lang` | Language | `lang:python` |
| `path` | File path | `path:src/` |
| `size` | File size | `size:>1000` |
| `date` | Modified date | `date:>2024-01-01` |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMOBASE_CONFIG` | Config file path | `.memobase/config.json` |
| `MEMOBASE_STORAGE` | Storage path | `.memobase` |
| `MEMOBASE_VERBOSITY` | Verbosity level | `1` |
| `MEMOBASE_WORKERS` | Parallel workers | `4` |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Configuration error |
| `4` | Build error |
| `5` | Query error |

## Examples

### Workflow 1: Initial Setup

```bash
# Initialize and build
cd my-project
memobase init
memobase build

# Ask questions
memobase ask "How does the auth system work?"
memobase query "class User" --limit 5
```

### Workflow 2: Daily Development

```bash
# After code changes
memobase update

# Check for issues
memobase analyze --type security

# Navigate relationships
memobase graph --symbol "UserService" --depth 3
```

### Workflow 3: Code Review

```bash
# Full analysis
memobase analyze --output review.md

# Check specific patterns
memobase query "TODO" --filter "type:comment"
memobase query "FIXME" --filter "type:comment"
```
