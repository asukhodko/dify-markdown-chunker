#!/bin/bash
# Package plugin using official dify-plugin CLI

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIRNAME="$(basename "$PLUGIN_DIR")"
PLUGIN_NAME="markdown-chunker"
PLUGIN_VERSION=$(grep '^version:' "$PLUGIN_DIR/manifest.yaml" | head -1 | sed 's/version: *//' | tr -d '"' | tr -d "'")
PARENT_DIR="$(dirname "$PLUGIN_DIR")"

if [ -z "$PLUGIN_VERSION" ]; then
    echo "❌ Failed to extract version from manifest.yaml"
    exit 1
fi

cd "$PARENT_DIR" || exit 1

echo "📦 Packaging plugin with official dify-plugin CLI..."
echo "   Plugin: $PLUGIN_NAME"
echo "   Version: $PLUGIN_VERSION"
echo "   Working from: $PARENT_DIR/$PLUGIN_DIRNAME"
echo ""

dify-plugin plugin package "$PLUGIN_DIRNAME"

if [ $? -eq 0 ]; then
    # Move and rename package
    if [ -f "$PLUGIN_DIRNAME.difypkg" ]; then
        # TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        # SUFFIX="${TIMESTAMP}"
        SUFFIX="${PLUGIN_VERSION}"
        NEW_NAME="$PLUGIN_DIR/$PLUGIN_NAME-${SUFFIX}.difypkg"
        mv "$PLUGIN_DIRNAME.difypkg" "$NEW_NAME"
        
        echo ""
        echo "✅ Package created successfully!"
        echo ""
        ls -lh "$NEW_NAME"
    else
        echo ""
        echo "⚠️  Package created but file not found in expected location"
        ls -lh "$PLUGIN_DIRNAME"*.difypkg 2>/dev/null | tail -1
    fi
else
    echo ""
    echo "❌ Packaging failed!"
    exit 1
fi
