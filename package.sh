#!/bin/bash
# Package Dify Plugin
#
# This script validates and packages the plugin for distribution.
# It runs all validation checks before creating the .difypkg file.

set -e  # Exit on error

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Validating plugin before packaging..."
echo ""

# Check if .env exists (should not be packaged)
if [ -f ".env" ]; then
    echo "❌ ERROR: .env file found!"
    echo "   The .env file should not be packaged."
    echo "   Please delete it before packaging:"
    echo "   rm .env"
    exit 1
fi

echo "✅ No .env file found (good)"
echo ""

# Run structure validation
echo "📋 Validating file structure..."
python validate_structure.py
if [ $? -ne 0 ]; then
    echo "❌ Structure validation failed!"
    exit 1
fi
echo ""

# Run Python syntax validation
echo "🐍 Validating Python syntax..."
python validate_syntax.py
if [ $? -ne 0 ]; then
    echo "❌ Python syntax validation failed!"
    exit 1
fi
echo ""

# Run YAML syntax validation
echo "📄 Validating YAML syntax..."
python validate_yaml.py
if [ $? -ne 0 ]; then
    echo "❌ YAML syntax validation failed!"
    exit 1
fi
echo ""

# Run tests
echo "🧪 Running tests..."
make test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed!"
    exit 1
fi
echo ""

# Run linter
echo "🔧 Running linter..."
make lint
if [ $? -ne 0 ]; then
    echo "❌ Linter failed!"
    exit 1
fi
echo ""

echo "✅ All validations passed!"
echo ""

# Create package using official dify-plugin CLI
echo "📦 Creating package with official dify-plugin CLI..."
echo ""

# Need to run from parent directory
cd ..
dify-plugin plugin package dify-markdown-chunker

if [ $? -ne 0 ]; then
    echo "❌ Packaging failed!"
    cd dify-markdown-chunker
    exit 1
fi

# Move package to plugin directory
if [ -f "dify-markdown-chunker.difypkg" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    PACKAGE_FILE="dify-markdown-chunker/dify-markdown-chunker-official-${TIMESTAMP}.difypkg"
    mv dify-markdown-chunker.difypkg "$PACKAGE_FILE"
    cd dify-markdown-chunker
    
    echo "✅ Package created: $(basename $PACKAGE_FILE)"
    
    # Validate the package
    echo ""
    echo "🔍 Validating package..."
    python validate_package.py "$(basename $PACKAGE_FILE)"
    
    if [ $? -ne 0 ]; then
        echo "❌ Package validation failed!"
        exit 1
    fi
else
    cd dify-markdown-chunker
    echo "❌ Package file not found!"
    exit 1
fi

echo ""
echo "🎉 Packaging complete!"
echo ""
echo "Next steps:"
echo "1. Test the package in a Dify instance"
echo "2. Verify all functionality works"
echo "3. Distribute the .difypkg file"
