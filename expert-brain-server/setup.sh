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
echo "=== Rebuilding index.md and log.md from insight files ==="
cd "$(dirname "$0")/.."
python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import DRAFT_DIR, LIVE_DIR, INDEX_PATH, LOG_PATH, _parse_metadata
import os

# Rebuild index.md
sections = {
    'draft':  ('Insights pending review before promotion to live.', 'Insight', DRAFT_DIR),
    'live':   ('Active, reviewed insights used for retrieval.', 'Insight', LIVE_DIR),
}
lines = ['# MetaCognition Insights Index', '']
for section, (desc, col, dir_path) in sections.items():
    lines.append(f'## {section}')
    if desc: lines.append(f'{desc}  ')
    lines.append(f'| {col} | Summary | Updated |')
    lines.append('|---------|---------|---------|')
    if os.path.isdir(dir_path):
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith('.md'): continue
            with open(os.path.join(dir_path, fname), 'r', encoding='utf-8') as f:
                meta = _parse_metadata(f.read())
            title = meta.get('title', fname[:-3])
            created = meta.get('created', '')
            # First 80 chars as summary from title
            summary = title[:80]
            lines.append(f'| [{title}]({section}/{fname}) | {summary} | {created} |')
    lines.append('')

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write('\\n'.join(lines))

# Rebuild log.md
log_lines = ['# Wiki Log', '',
    '<!-- Format: ## [YYYY-MM-DD] Action | Insight title. Cascading updates use - Updated: sub-items -->',
    '',
    '## [2026-05-20] scaffold | Wiki directory created',
    '']
for section, dir_path in [('draft', DRAFT_DIR), ('live', LIVE_DIR)]:
    if os.path.isdir(dir_path):
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith('.md'): continue
            with open(os.path.join(dir_path, fname), 'r', encoding='utf-8') as f:
                meta = _parse_metadata(f.read())
            title = meta.get('title', fname[:-3])
            created = meta.get('created', '')
            if title:
                log_lines.append(f\"## [{created}] ingest | {title}\")

with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('\\n'.join(log_lines))

print(f'  index.md: rebuilt from {len([f for f in os.listdir(DRAFT_DIR) if f.endswith(\".md\")]) if os.path.isdir(DRAFT_DIR) else 0} draft + {len([f for f in os.listdir(LIVE_DIR) if f.endswith(\".md\")]) if os.path.isdir(LIVE_DIR) else 0} live insights')
print(f'  log.md: rebuilt')
"

echo ""
echo "=== Generating vector embeddings from seed insights ==="
python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import DRAFT_DIR, LIVE_DIR, _embed, _parse_metadata, _extract_section
import os, numpy as np
count = 0
for dir_path in [DRAFT_DIR, LIVE_DIR]:
    if not os.path.isdir(dir_path): continue
    for fname in os.listdir(dir_path):
        if not fname.endswith('.md'): continue
        fpath = os.path.join(dir_path, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        meta = _parse_metadata(content)
        symptom = meta.get('title', '')
        variants_text = _extract_section(content, 'Query Variants')
        embed_text = symptom
        if variants_text:
            embed_text += '\n' + variants_text.replace('- ', '').replace('\n', ' ')
        emb = _embed(embed_text)
        if emb is not None:
            np.save(fpath.replace('.md', '.npy'), emb)
            count += 1
print(f'Generated {count} .npy embeddings')
"

echo ""
echo "=== Setup complete ==="
echo "Model: $(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1)"
echo "Insights: $(ls .cursor/insights/wiki/draft/*.md 2>/dev/null | wc -l) draft + $(ls .cursor/insights/wiki/live/*.md 2>/dev/null | wc -l) live"
echo ""
echo "Tests:"
echo "  python expert-brain-server/test_scenarios.py   # 46 scenario tests"
echo "  python expert-brain-server/eval_search.py      # search quality"
