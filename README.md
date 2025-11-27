# D&D 5e Rules Preprocessing Pipeline

This project converts D&D 5e rules from the 5etools JSON format to Markdown files with extracted metadata for embedding in graph/vector databases.

## Overview

The pipeline uses the 5etools renderer to convert structured JSON entries into clean Markdown, while simultaneously extracting tags and references for creating graph representations.

## Project Structure

```
.
├── 5etools-src/              # 5etools source code (cloned from GitHub)
│   ├── data/                 # JSON data files for spells, items, classes, etc.
│   ├── js/                   # Renderer and utility modules
│   └── render-to-markdown.js # Main batch rendering script
├── output/                   # Generated markdown and metadata
│   ├── spell/               # Rendered spell markdown files
│   ├── action/              # Rendered action markdown files
│   ├── metadata/            # Extracted metadata JSON files
│   └── ...                  # Other entry types
└── README.md                # This file
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
   - See [renderdemo.json](5etools-src/data/renderdemo.json:1-870) for comprehensive examples

3. **Markdown Rendering**: The `RendererMarkdown` class extends the base HTML renderer to output clean markdown with proper heading levels, lists, tables, and formatting.

## Usage

### Install Dependencies

```bash
cd 5etools-src
npm install
```

### List Available Data Files

```bash
node render-to-markdown.js --list
```

### Render a Single File

```bash
node render-to-markdown.js --input data/spells/spells-phb.json --output-dir ../output
```

### Render All Data Files

```bash
node render-to-markdown.js --all --output-dir ../output
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

### Example: Process All Core Rules

```bash
# Render core player content
node render-to-markdown.js --input data/spells/spells-phb.json --output-dir ../output
node render-to-markdown.js --input data/items.json --output-dir ../output
node render-to-markdown.js --input data/classes.json --output-dir ../output
node render-to-markdown.js --input data/races.json --output-dir ../output
node render-to-markdown.js --input data/feats.json --output-dir ../output
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

## Cleanup Recommendations

After confirming the pipeline works for your needs, you can remove:
- Web UI files: `*.html`, `css/`, `img/`
- Client-only JS: `service-worker.js`, browser-specific utilities
- Development tools: `test/`, `.github/`
- Documentation: Original docs, changelogs (keep your own README)

Keep:
- `data/` - Source JSON files
- `js/` - Renderer and parser modules (required)
- `node/` - Node.js utilities (may be useful)
- `render-to-markdown.js` - Your pipeline script

## Resources

- [5etools GitHub](https://github.com/5etools-mirror-3/5etools-src)
- [Entry Schema](https://raw.githubusercontent.com/TheGiddyLimit/5etools-utils/master/schema/site/entry.json)
- [Render Demo](5etools-src/data/renderdemo.json:1-870) - Comprehensive examples of all entry types

## License

This project uses the 5etools codebase which is MIT licensed. Refer to the D&D 5e System Reference Document (SRD) for content licensing.
