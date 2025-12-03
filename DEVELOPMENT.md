# Development Guide

Development and maintenance guide for the Advanced Markdown Chunker plugin for Dify.

---

## Requirements

- Python 3.12+
- dify-plugin CLI (for packaging)
- Git

---

## Development Setup

### 1. Clone the Repository

```bash
git clone <repository_url>
cd dify-markdown-chunker
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install dify-plugin CLI

```bash
# Linux/Mac
curl -L https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-linux-amd64 -o /tmp/dify-plugin
chmod +x /tmp/dify-plugin
sudo mv /tmp/dify-plugin /usr/local/bin/dify-plugin

# Verification
dify-plugin version
```

---

## Project Structure

```
dify-markdown-chunker/
├── manifest.yaml              # Plugin metadata
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── _assets/
│   └── icon.svg              # Plugin icon
├── provider/
│   ├── markdown_chunker.yaml # Provider configuration
│   └── markdown_chunker.py   # Provider class
├── tools/
│   ├── markdown_chunk_tool.yaml  # Tool configuration
│   └── markdown_chunk_tool.py    # Chunking logic
├── markdown_chunker/         # Chunking library
│   ├── api/
│   ├── chunker/
│   └── parser/
└── tests/                    # Tests
```

---

## Development

### Running Tests

```bash
# All tests
make test

# Quick tests
make test-quick

# Specific test
venv/bin/pytest tests/test_manifest.py -v
```

### Linting

```bash
make lint
```

### Validation

```bash
# Validate structure, syntax, YAML
make validate
```

---

## Packaging

### Create Package

```bash
make package
```

Creates: `dify-markdown-chunker-official-YYYYMMDD_HHMMSS.difypkg`

### Validate Package

```bash
make validate-package
```

### Full Release

```bash
make release
```

Executes: validate → test → lint → package → validate-package

---

## Important Rules

### 1. Icon Paths

**Always specify without path in YAML files:**
```yaml
icon: icon.svg  # ✅ Correct
icon: _assets/icon.svg  # ❌ Incorrect
```

**Physical file:**
```
_assets/icon.svg  # ✅ File must be here
```

### 2. Tags

**Use only standard tags:**
- `productivity`
- `business`
- `social`
- `search`
- `news`
- `weather`

**Custom tags do not pass CLI validation:**
```yaml
tags:
  - productivity  # ✅ Correct
  - business      # ✅ Correct
  - rag           # ❌ Will not pass validation
```

### 3. File Exclusion

**CLI uses `.gitignore` to exclude files from the package.**

Must exclude:
- `venv/`
- `__pycache__/`
- `tests/`
- `*.md` (except README.md)
- `*.difypkg`

### 4. Package Size

Maximum size: **50 MB** (uncompressed)

CLI automatically checks during packaging.

---

## Debugging

### Debug Mode

1. Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

2. Get debug key from Dify UI:
```
Settings → Plugins → Debug Mode
```

3. Update `.env`:
```env
INSTALL_METHOD=remote
REMOTE_INSTALL_HOST=https://debug.dify.ai
REMOTE_INSTALL_PORT=5003
REMOTE_INSTALL_KEY=your_debug_key_here
```

4. Run the plugin:
```bash
python main.py
```

**⚠️ Important:** Delete `.env` before packaging!

---

## Testing in Dify

### 1. Import Plugin

```
Dify UI → Settings → Plugins → Install Plugin
→ Upload .difypkg file
```

### 2. Using in Knowledge Base

```
Knowledge Base → Chunking Settings
→ Custom → Advanced Markdown Chunker
```

### 3. Using in Workflow

```
Workflow → Add Tool Node
→ Advanced Markdown Chunker
```

---

## Version Update

### 1. Update version in manifest.yaml

```yaml
version: 2.0.0-a3  # New version
meta:
  version: 2.0.0-a3  # Also update
```

### 2. Update CHANGELOG.md

```markdown
## [2.0.1] - YYYY-MM-DD

### Fixed
- Description of fix

### Added
- Description of new functionality
```

### 3. Create Package

```bash
make release
```

### 4. Test

```bash
# Import into Dify
# Verify functionality
```

---

## Troubleshooting

### Error: "tool icon not found"

**Cause:** Incorrect icon path in YAML

**Solution:**
```bash
# Check all YAML files
grep -r "icon:" *.yaml provider/*.yaml tools/*.yaml

# Should be everywhere: icon: icon.svg
```

### Error: "Plugin package size is too large"

**Cause:** venv/ included in package

**Solution:**
```bash
# Ensure venv/ is in .gitignore
echo "venv/" >> .gitignore
```

### Error: "failed to package plugin: ... tag"

**Cause:** Custom tags do not pass validation

**Solution:**
```yaml
# Use only standard tags
tags:
  - productivity
  - business
```

### Tests Failing

**Solution:**
```bash
# Verify venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Run tests with verbose output
venv/bin/pytest tests/ -v
```

---

## CI/CD

### GitHub Actions (пример)

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
      
      - name: Run tests
        run: make test
      
      - name: Run lint
        run: make lint
      
      - name: Validate
        run: make validate
```

---

## Useful Commands

```bash
# Show all commands
make help

# Clean temporary files
make clean

# Install dependencies
make install

# Validate structure
python validate_structure.py

# Validate syntax
python validate_syntax.py

# Validate YAML
python validate_yaml.py

# Validate package
python validate_package.py <package>.difypkg
```

---

## Resources

- **Official Dify Plugins:** `reference/dify-official-plugins/`
- **Dify Documentation:** https://docs.dify.ai/plugins
- **CLI Repository:** https://github.com/langgenius/dify-plugin-daemon
- **Dify GitHub:** https://github.com/langgenius/dify

---

## Contact

- **Issues:** [GitHub Issues]
- **Discord:** [Dify Community](https://discord.gg/FngNHpbcY7)
