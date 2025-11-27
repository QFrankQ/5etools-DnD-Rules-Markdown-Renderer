# D&D 5e Rules Markdown Renderer

A lightweight, production-ready package for converting D&D 5e rules from 5etools JSON format to Markdown files with extracted metadata for RAG systems, knowledge graphs, and vector databases.

## Overview

This package provides a Python wrapper around the 5etools renderer to convert structured JSON entries into clean Markdown, while simultaneously extracting tags and references for creating graph representations.

**Ready for use as a git submodule in your Agentic DM or RAG project!**

## Project Structure

```
.
├── dnd_renderer.py           # Python wrapper for Node.js renderer
├── render_my_rules.py        # Batch script for curated rules
├── example_usage.py          # Usage examples
├── curated_rules/            # Your filtered D&D rules (9 JSON files)
├── data/                     # Full 5etools dataset (~106 MB)
├── js/                       # Core renderer modules (9 files + utils-config/)
├── render-to-markdown.js     # Main batch rendering script
├── node_modules/             # NPM dependencies
└── output/                   # Generated markdown and metadata
    ├── spell/               # Rendered spell markdown files
    ├── action/              # Rendered action markdown files
    └── metadata/            # Extracted metadata JSON files
```

## How the Renderer Works

The 5etools renderer is a sophisticated system that converts structured JSON entries into formatted output:

1. **Entry Types**: The JSON uses a rich type system including:
   - `"entries"` - hierarchical content blocks with headers
   - `"list"` - bulleted or numbered lists
   - `"table"` - formatted tables
   - `"quote"` - blockquotes with attribution
   - `"inset"` - sidebar content
   - And many more specialized types

2. **Inline Tags**: Content uses special tags like:
   - `{@spell fireball}` - links to spells
   - `{@damage 8d6}` - damage dice
   - `{@dice 1d20}` - dice rolls
   - `{@creature goblin}` - creature references
   - `{@item longsword}` - item references
   - See [renderdemo.json](data/renderdemo.json) for comprehensive examples

3. **Markdown Rendering**: The `RendererMarkdown` class extends the base HTML renderer to output clean markdown with proper heading levels, lists, tables, and formatting.

## Usage

### Install Dependencies

```bash
npm install
```

### Python Usage (Recommended)

```python
from dnd_renderer import DnDRenderer

# Initialize renderer
renderer = DnDRenderer()

# Render a single file
stats = renderer.render_file("data/spells/spells-phb.json", "./output")
print(f"Rendered {stats['success_count']} spells")

# Or render your curated rules
# python3 render_my_rules.py
```

### Node.js CLI Usage

```bash
# List available data files
node render-to-markdown.js --list

# Render a single file
node render-to-markdown.js --input data/spells/spells-phb.json --output-dir ./output

# Render all data files
node render-to-markdown.js --all --output-dir ./output
```

## Output Format

### Markdown Files

Each entry is rendered to a separate markdown file named `{entry_name}_{source}.md`:

Example: [fireball_phb.md](output/test/spell/fireball_phb.md:1-6)
```markdown
### Fireball

A bright streak flashes from your pointing finger to a point you choose...
```

### Metadata Files

Each entry also generates a metadata JSON file for graph/vector database integration:

Example: `fireball_phb.json`
```json
{
  "type": "spell",
  "name": "Fireball",
  "source": "PHB",
  "references": [
    {
      "tagType": "damage",
      "content": "8d6"
    }
  ]
}
```

The metadata captures:
- **type**: Entry type (spell, item, class, etc.)
- **name**: Entry name
- **source**: Source book abbreviation
- **references**: All inline tag references for building a knowledge graph

## Use Cases for Agentic DM

### 1. Vector Database Embedding

The clean markdown output is perfect for chunking and embedding:

```python
# Example: Embed spell descriptions
for spell_file in glob("output/spell/*.md"):
    text = read_file(spell_file)
    embedding = embed_model.encode(text)
    vector_db.insert(embedding, metadata_file)
```

### 2. Knowledge Graph Construction

The metadata files contain references that can be used to build a graph:

```python
# Example: Build spell->damage relationship
metadata = json.load("output/metadata/spell/fireball_phb.json")
for ref in metadata["references"]:
    if ref["tagType"] == "damage":
        graph.add_edge(metadata["name"], ref["content"], "deals_damage")
```

### 3. Hybrid RAG System

Combine both approaches:
1. Use vector similarity for semantic search
2. Use graph traversal for rule relationships
3. Provide comprehensive answers grounded in official rules

## Next Steps

### For Your Agentic DM Project

1. **Choose Entry Types**: Decide which data to process (spells, items, classes, monsters, etc.)
2. **Render Data**: Run the pipeline on selected files
3. **Chunk Strategy**: Determine optimal chunk size for embeddings (entire entries vs paragraphs)
4. **Graph Schema**: Design your graph schema based on reference types
5. **Implement RAG**: Build your retrieval system using the generated data

### Example: Process Core Rules with Python

```python
from dnd_renderer import DnDRenderer

renderer = DnDRenderer()

# Render core player content
core_files = [
    "data/spells/spells-phb.json",
    "data/items.json",
    "data/feats.json",
    "data/actions.json",
    "data/conditionsdiseases.json"
]

for file in core_files:
    stats = renderer.render_file(file, "./output")
    print(f"✓ {file}: {stats['success_count']} entries")
```

## Available Data Types

The 5etools dataset includes:
- **Player Content**: spells, classes, races, backgrounds, feats, items
- **Rules**: actions, conditions, variant rules, tables
- **DM Content**: monsters (in separate bestiary files), adventures, magic items
- **Setting Content**: deities, cults, vehicles, objects
- **Homebrew**: Support for custom content

## Technical Details

### Dependencies

The renderer requires these 5etools modules (imported in order):
1. `parser.js` - Parses abbreviations and formats
2. `utils.js` - Utility functions
3. `utils-ui.js` - UI helpers (some DOM-independent)
4. `utils-config.js` - Configuration (VetoolsConfig)
5. `render.js` - Base HTML renderer
6. `render-markdown.js` - Markdown renderer extension

### Isomorphic Code

The 5etools codebase is designed to work in both browser and Node.js environments, which makes server-side rendering possible without modification.

## Package Status

This package has been **optimized for production use**:

✅ **Cleaned up** - Removed 150+ unused files and 16 directories
✅ **Minimal footprint** - Only 9 essential JS files + utils-config/
✅ **Full dataset** - Complete 5etools data (106 MB)
✅ **Python integration** - Easy-to-use wrapper for Python projects
✅ **Verified** - Tested with 2,804 entries, 0 errors
✅ **Git ready** - Clean repository, ready for submodule use

**Size:** ~340 MB (184 MB node_modules + 106 MB data + 50 MB other)

## Installation as Submodule

Add to your project:
```bash
git submodule add https://github.com/QFrankQ/5etools-DnD-Rules-Markdown-Renderer.git preprocessing
cd preprocessing
npm install
```

Use in your code:
```python
from preprocessing.dnd_renderer import DnDRenderer
renderer = DnDRenderer()
```

## Resources

- [5etools GitHub](https://github.com/5etools-mirror-3/5etools-src)
- [Entry Schema](https://raw.githubusercontent.com/TheGiddyLimit/5etools-utils/master/schema/site/entry.json)
- [Render Demo](data/renderdemo.json) - Comprehensive examples of all entry types
- [This Package](https://github.com/QFrankQ/5etools-DnD-Rules-Markdown-Renderer)
- [SUMMARY.md](SUMMARY.md) - Complete project summary

## License

This project uses the 5etools codebase which is MIT licensed. Refer to the D&D 5e System Reference Document (SRD) for content licensing.
