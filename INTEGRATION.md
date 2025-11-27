# Integration Guide

This guide helps you integrate the D&D rendering pipeline into your Agentic DM project.

## Current State After Cleanup

**Before**: 381MB
**After**: 368MB
**Status**: ✅ Pipeline verified working

### What Was Removed
- ✅ 52 HTML files (web UI)
- ✅ CSS/SCSS (styling)
- ✅ Images and fonts (web assets)
- ✅ Client libraries (browser-only code)
- ✅ Test files and dev tools
- ✅ Search indexes

### What Remains (Essential)
- **data/** - JSON source files (~250MB)
- **js/** - Renderer and parser modules (~10MB)
- **node_modules/** - Dependencies (~40MB)
- **node/** - Node.js utilities (~2MB)
- **render-to-markdown.js** - Your pipeline script

## Integration Options

### Option 1: Keep Separate (Current Setup)
**Pros**: Clean separation, easy to update 5etools data
**Cons**: Need to switch directories

```bash
# Your workflow
cd /path/to/DnD-rules_preprocessing/5etools-src
node render-to-markdown.js --all --output-dir /path/to/agentic-dm/data
```

### Option 2: Git Submodule (Recommended)
Keep this as a submodule in your Agentic DM project:

```bash
cd /path/to/agentic-dm
git submodule add /Users/frankchiu/Documents/Agentic\ RAG/DnD-rules_preprocessing dnd-preprocessing
```

Then reference it:
```python
# In your Agentic DM code
import subprocess
subprocess.run([
    "node",
    "dnd-preprocessing/5etools-src/render-to-markdown.js",
    "--input", "dnd-preprocessing/5etools-src/data/spells/spells-phb.json",
    "--output-dir", "./processed_data"
])
```

### Option 3: Standalone Package
Create a minimal npm package you can install anywhere.

## Recommended: Create Standalone Package

Let me create a standalone version that's easier to integrate:

### Structure
```
dnd-renderer-package/
├── package.json          # Dependencies only
├── render.js             # Your script
├── lib/                  # 5etools modules
│   ├── parser.js
│   ├── utils.js
│   ├── render.js
│   └── render-markdown.js
└── data/                 # Symlink or copy
```

### Usage in Your Project
```javascript
// In your Agentic DM project
const DnDRenderer = require('./dnd-renderer');

const markdown = DnDRenderer.render({
  type: 'spell',
  data: spellData
});
```

## Creating the Standalone Package

I'll create a minimal, portable version for you. Would you like:

### A. Minimal Script Package (~50MB)
- Just the renderer code and your script
- Data files stay separate (symlinked or copied)
- Smallest footprint

### B. Complete Package (~300MB)
- Everything needed to run
- Self-contained, easier to move
- Larger footprint

### C. Python Integration Package
- Python wrapper around the Node.js renderer
- Easy to call from your Python-based Agentic DM
- Can be imported as a module

## Quick Python Integration Example

Here's how to use the renderer from Python:

```python
import subprocess
import json
from pathlib import Path

class DnDRenderer:
    def __init__(self, renderer_path):
        self.renderer_path = Path(renderer_path)
        self.script = self.renderer_path / "render-to-markdown.js"

    def render_file(self, input_file, output_dir):
        """Render a D&D JSON file to markdown"""
        subprocess.run([
            "node",
            str(self.script),
            "--input", str(input_file),
            "--output-dir", str(output_dir)
        ], check=True)

    def render_all(self, output_dir):
        """Render all D&D data files"""
        subprocess.run([
            "node",
            str(self.script),
            "--all",
            "--output-dir", str(output_dir)
        ], check=True)

    def get_rendered_markdown(self, entry_type, name, source):
        """Get specific rendered markdown"""
        filename = f"{name.lower().replace(' ', '_')}_{source.lower()}.md"
        path = Path(output_dir) / entry_type / filename
        return path.read_text() if path.exists() else None

# Usage
renderer = DnDRenderer("/path/to/5etools-src")
renderer.render_file("data/spells/spells-phb.json", "./output")

# Get specific spell
fireball = renderer.get_rendered_markdown("spell", "Fireball", "PHB")
```

## Directory Structure for Integration

Recommended setup in your Agentic DM project:

```
your-agentic-dm/
├── src/
│   ├── dm_agent.py
│   ├── rag_system.py
│   └── dnd_renderer.py      # ← Wrapper class
├── data/
│   ├── rendered/            # ← Output from renderer
│   │   ├── spell/
│   │   ├── item/
│   │   └── metadata/
│   └── embeddings/          # ← Your embeddings
├── preprocessing/           # ← This project (as submodule or copy)
│   └── 5etools-src/
│       ├── render-to-markdown.js
│       ├── js/
│       └── data/
└── requirements.txt
```

## Next Steps

1. **Choose integration method** (submodule recommended)
2. **Create Python wrapper** for easy calling
3. **Set up data pipeline** in your project
4. **Automate rendering** as needed

Let me know which integration option you prefer, and I'll help set it up!
