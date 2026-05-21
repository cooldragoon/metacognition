#!/bin/bash
# MetaCognition setup: install dependencies + download embedding model
# Run once after cloning the repo

set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo ""
echo "=== Downloading embedding model (8MB params, ~60MB disk) ==="
MODEL_DIR="$(dirname "$0")/models/potion-base-8M"

if [ -d "$MODEL_DIR" ] && [ -f "$MODEL_DIR/model.safetensors" ]; then
    echo "Model already downloaded: $MODEL_DIR"
else
    mkdir -p "$MODEL_DIR"
    # Try mirror first (faster in China), fall back to HuggingFace
    if huggingface-cli download minishlab/potion-base-8M --local-dir "$MODEL_DIR" --hf-endpoint https://hf-mirror.com 2>/dev/null; then
        echo "Downloaded via hf-mirror.com"
    else
        echo "Mirror failed, trying HuggingFace directly..."
        huggingface-cli download minishlab/potion-base-8M --local-dir "$MODEL_DIR"
    fi
fi

echo ""
echo "=== Setup complete ==="
echo "Model: $(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1)"
echo "Run: python eval_search.py   # to test search quality"
