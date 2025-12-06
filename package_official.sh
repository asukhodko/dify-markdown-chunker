#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
FILE="$PLUGIN_DIR/manifest.yaml"

if [ ! -f "$FILE" ]; then
  echo "❌ manifest.yaml not found at $FILE"
  exit 1
fi

MAIN_VERSION=$(awk '/^version:/ {print $2; exit}' "$FILE")
META_VERSION=$(awk '/^  version:/ {print $2; exit}' "$FILE")

if [ -z "$MAIN_VERSION" ] || [ -z "$META_VERSION" ]; then
  echo "❌ Failed to extract version or meta.version from manifest.yaml"
  exit 1
fi

if [ "$MAIN_VERSION" != "$META_VERSION" ]; then
    echo "❌ version ($MAIN_VERSION) != meta.version ($META_VERSION) in manifest.yaml"
    exit 1
fi

PLUGIN_VERSION="$MAIN_VERSION"

PLUGIN_DIRNAME="$(basename "$PLUGIN_DIR")"
PLUGIN_NAME="markdown-chunker"
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
