# Tree-sitter Grammar Vendors

This directory contains Tree-sitter grammar repositories used for building language parsers.

## Required Setup

### Python Grammar

The Python grammar is required for parsing Python files. To set it up:

```bash
# Clone the tree-sitter-python repository
cd memobase/parser/vendor
git clone https://github.com/tree-sitter/tree-sitter-python.git

# After cloning, run the build script
python -m memobase.parser.build_languages
```

## Adding New Languages

To add support for a new language:

1. Clone the grammar repository to this directory
2. Update `memobase/parser/build_languages.py` to include the new language
3. Run the build script
4. Update the parser factory to register the new parser

Example for JavaScript:
```bash
cd memobase/parser/vendor
git clone https://github.com/tree-sitter/tree-sitter-javascript.git
```

## Grammar Repositories

- **tree-sitter-python**: https://github.com/tree-sitter/tree-sitter-python
- **tree-sitter-javascript**: https://github.com/tree-sitter/tree-sitter-javascript
- **tree-sitter-typescript**: https://github.com/tree-sitter/tree-sitter-typescript
- **tree-sitter-java**: https://github.com/tree-sitter/tree-sitter-java

## Notes

- Do not modify grammar files directly
- Keep grammars up to date with upstream repositories
- Each grammar should be in its own subdirectory
- The build script expects grammar directories to be named `tree-sitter-{language}`
