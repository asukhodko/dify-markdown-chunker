# Troubleshooting Guide

Common issues and solutions.

## Import Errors

**Problem**: `ModuleNotFoundError: No module named 'markdown_chunker'`

**Solution**: 
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Configuration Issues

**Problem**: Configuration not working

**Solution**:
- Use ChunkConfig class: `from markdown_chunker import ChunkConfig`
- Check configuration values are valid

## Plugin Issues

**Problem**: Plugin not showing in Dify

**Solution**:
- Verify plugin is installed: Settings → Plugins
- Check plugin status is "Active"
- Restart Dify if needed

For more help, see [Developer Guide](developer-guide.md).
