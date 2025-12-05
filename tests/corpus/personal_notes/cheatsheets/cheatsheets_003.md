# Git Cheatsheet

## Basic Commands

| Command | Description |
|---------|-------------|
| `git init` | Initialize new repository |
| `git status` | Check current status |
| `git list` | List all items |
| `git show <id>` | Show details |

## Common Operations

### Creating Items

```bash
git create <name>
git add <file>
git commit -m "message"
```

### Viewing Items

- `git log` - view history
- `git diff` - show changes  
- `git show` - display content

### Modifying Items

```bash
git update <id>
git delete <id>
git rename <old> <new>
```

## Advanced Usage

### Configuration

```bash
git config --global user.name "Name"
git config --global user.email "email@example.com"
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Run with sudo |
| Not found | Check path |
| Conflict | Resolve manually |

## Tips & Tricks

1. Use aliases for common commands
2. Enable auto-completion
3. Read the manual: `man git`
4. Check version: `git --version`

## References

- Official docs: https://docs.example.com
- Community guide: https://guide.example.com
