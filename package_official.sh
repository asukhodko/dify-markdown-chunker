#!/bin/bash
# Package plugin using official dify-plugin CLI

cd "$(dirname "$0")/.." || exit 1

echo "📦 Packaging plugin with official dify-plugin CLI..."
echo ""

dify-plugin plugin package dify-markdown-chunker

if [ $? -eq 0 ]; then
    # Move and rename package
    if [ -f "dify-markdown-chunker.difypkg" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        NEW_NAME="dify-markdown-chunker/dify-markdown-chunker-official-${TIMESTAMP}.difypkg"
        mv dify-markdown-chunker.difypkg "$NEW_NAME"
        
        echo ""
        echo "✅ Package created successfully!"
        echo ""
        ls -lh "$NEW_NAME"
    else
        echo ""
        echo "⚠️  Package created but file not found in expected location"
        ls -lh dify-markdown-chunker*.difypkg 2>/dev/null | tail -1
    fi
else
    echo ""
    echo "❌ Packaging failed!"
    exit 1
fi
