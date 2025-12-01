# D&D 5e Rules Markdown Renderer

A lightweight, production-ready package for converting D&D 5e rules from 5etools JSON format to Markdown files with extracted metadata for RAG systems, knowledge graphs, and vector databases.

## Overview

This package provides a Python wrapper around the 5etools renderer to convert structured JSON entries into clean Markdown, while simultaneously extracting tags and references for creating graph representations.

**Ready for use as a git submodule in your Agentic DM or RAG project!**

### Key Features

- **Dual Output**: Clean markdown for embeddings + structured metadata for graphs
- **Rich Metadata**: Extracts inline tags, cross-references, and type-specific fields
- **Production Ready**: 2,804 entries tested, 0 errors
- **Python Integration**: Easy-to-use wrapper with smart Node.js detection
- **Complete Dataset**: Full 5etools D&D rules (106 MB)
- **Minimal Footprint**: Only essential files (9 JS + utils-config)

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

The renderer generates **two files per entry**: a clean Markdown file for embeddings and a structured metadata JSON file for knowledge graphs.

### Markdown Files

Each entry is rendered to a separate markdown file named `{entry_name}_{source}.md`:

**Location:** `output/{entry_type}/{name}_{source}.md`

**Example:** `output/action/attack_XPHB.md`
```markdown
### Attack

When you take the Attack action, you can make one attack roll with a weapon or an Unarmed Strike.

***Equipping and Unequipping Weapons.*** You can either equip or unequip one weapon when you make an attack...

***Moving Between Attacks.*** If you move on your turn and have a feature, such as Extra Attack...
```

**Features:**
- Clean, readable text ideal for semantic search
- Formatted with proper headings, lists, and tables
- Inline tags converted to plain text (e.g., `{@spell fireball}` → "Fireball")
- No metadata clutter - pure content

### Metadata Files

Each entry generates a structured metadata JSON file for filtering and graph construction:

**Location:** `output/metadata/{entry_type}/{name}_{source}.json`

**Example:** `output/metadata/action/attack_XPHB.json`
```json
{
  "type": "action",
  "name": "Attack",
  "source": "XPHB",
  "tags": [],
  "references": [
    {
      "tagType": "variantrule",
      "content": "Unarmed Strike|XPHB",
      "referenceType": "inline_tag"
    },
    {
      "tagType": "action",
      "content": "Two-Weapon Fighting|XPHB",
      "referenceType": "seeAlsoAction"
    }
  ],
  "time": [
    {
      "number": 1,
      "unit": "action"
    }
  ]
}
```

**Metadata Fields:**

1. **Core Fields** (always present):
   - `type`: Entry type (action, spell, item, etc.)
   - `name`: Entry name
   - `source`: Source book abbreviation (PHB, XPHB, XGE, etc.)
   - `tags`: Array of tags (currently unused, reserved for future)
   - `references`: Array of all extracted references

2. **Reference Types** (in `references` array):
   - **`inline_tag`**: Tags embedded in text like `{@spell fireball}`, `{@damage 8d6}`, `{@creature goblin}`
   - **`seeAlsoAction`**: Cross-references to related actions
   - **`seeAlsoFeature`**: Cross-references to related features
   - **`seeAlsoDeck`**: Cross-references to decks (for items)
   - **`seeAlsoVehicle`**: Cross-references to vehicles (for items)
   - **`seeAlsoSpell`**: Cross-references to spells
   - **`seeAlsoItem`**: Cross-references to items
   - **`fromVariant`**: Source variant rule for optional content

3. **Type-Specific Fields** (when applicable):
   - **Actions**: `time` (action, bonus, reaction, free)
   - **Spells**: `level`, `school`, `time`
   - **Items**: `rarity`, `tier`, `itemType`

**Reference Structure:**
```json
{
  "tagType": "spell",              // Type of referenced entity
  "content": "Fireball|PHB",       // Reference content (name|source)
  "referenceType": "inline_tag"   // How the reference was found
}
```

## Use Cases for Agentic DM

The dual output format (markdown + metadata) enables powerful RAG implementations:

### 1. Vector Database Embedding

Use the clean markdown for semantic search:

```python
from pathlib import Path
import json

# Embed all actions
for md_file in Path("output/action").glob("*.md"):
    # Read clean markdown content
    markdown_content = md_file.read_text()

    # Load corresponding metadata
    meta_file = Path("output/metadata/action") / md_file.name.replace(".md", ".json")
    metadata = json.loads(meta_file.read_text())

    # Create embedding with metadata
    embedding = embed_model.encode(markdown_content)
    vector_db.insert(
        embedding=embedding,
        document=markdown_content,
        metadata={
            "name": metadata["name"],
            "type": metadata["type"],
            "source": metadata["source"],
            "action_time": metadata.get("time", [])
        }
    )
```

### 2. Knowledge Graph Construction

Build a graph from the extracted references:

```python
import json
from pathlib import Path

# Build complete knowledge graph
graph = nx.DiGraph()

for meta_file in Path("output/metadata").rglob("*.json"):
    metadata = json.loads(meta_file.read_text())

    # Add node for this entry
    node_id = f"{metadata['name']}|{metadata['source']}"
    graph.add_node(node_id, **metadata)

    # Add edges for all references
    for ref in metadata.get("references", []):
        target_id = ref["content"]
        edge_type = f"{ref['referenceType']}_{ref['tagType']}"

        graph.add_edge(node_id, target_id, type=edge_type)

# Query examples:
# - "What actions reference Unarmed Strike?"
# - "What are all the bonus actions available?"
# - "Show me everything related to concentration"
```

### 3. Filtered Retrieval

Use metadata for precise filtering:

```python
import json
from pathlib import Path

def find_actions_by_time(action_type="bonus"):
    """Find all bonus actions, reactions, etc."""
    results = []

    for meta_file in Path("output/metadata/action").glob("*.json"):
        metadata = json.loads(meta_file.read_text())

        # Check if this action matches the time requirement
        for time in metadata.get("time", []):
            if isinstance(time, dict) and time.get("unit") == action_type:
                results.append(metadata["name"])

    return results

# Usage:
bonus_actions = find_actions_by_time("bonus")
print(f"Available bonus actions: {bonus_actions}")
# Output: ['Two-Weapon Fighting']

reactions = find_actions_by_time("reaction")
print(f"Available reactions: {reactions}")
# Output: ['Opportunity Attack', 'Identify a Spell']
```

### 4. Hybrid RAG System

Combine semantic search + graph traversal + metadata filtering:

```python
def answer_question(question: str, top_k: int = 3):
    """
    Hybrid RAG: Vector search + graph traversal + metadata filtering
    """
    # 1. Semantic search on markdown content
    query_embedding = embed_model.encode(question)
    candidates = vector_db.search(query_embedding, top_k=10)

    # 2. Filter by metadata (e.g., only show bonus actions)
    if "bonus action" in question.lower():
        candidates = [c for c in candidates if
                     any(t.get("unit") == "bonus"
                         for t in c.metadata.get("time", []))]

    # 3. Expand with graph neighbors
    expanded_results = []
    for candidate in candidates[:top_k]:
        node_id = f"{candidate.metadata['name']}|{candidate.metadata['source']}"

        # Get related entries from knowledge graph
        neighbors = graph.neighbors(node_id)
        related = [graph.nodes[n] for n in neighbors]

        expanded_results.append({
            "main": candidate,
            "related": related
        })

    return expanded_results

# Example usage:
results = answer_question("What bonus actions can I take after attacking?")
# Returns: Two-Weapon Fighting (main) + related Attack action + weapon references
```

### 5. Citation and Source Tracking

Always know where information comes from:

```python
def get_rule_with_citation(rule_name: str):
    """
    Retrieve rule with full citation information
    """
    # Find metadata file
    meta_files = list(Path("output/metadata").rglob(f"*{rule_name.lower()}*.json"))

    if not meta_files:
        return None

    metadata = json.loads(meta_files[0].read_text())

    # Get markdown content
    md_file = meta_files[0].parent.parent.parent / metadata["type"] / \
              f"{meta_files[0].stem}.md"
    content = md_file.read_text()

    return {
        "content": content,
        "citation": f"{metadata['name']} ({metadata['source']})",
        "type": metadata["type"],
        "references": metadata.get("references", [])
    }

# Usage:
rule = get_rule_with_citation("Opportunity Attack")
print(f"Rule: {rule['citation']}")
print(f"Content: {rule['content']}")
print(f"References: {[r['content'] for r in rule['references']]}")
```

## Common Tag Types and Patterns

The metadata extraction captures a rich set of reference types from the D&D rules. Here are the most common patterns:

### Action Economy Tags

```json
// D&D 5e action types
"time": [
  {"number": 1, "unit": "action"},     // Standard action
  {"number": 1, "unit": "bonus"},      // Bonus action
  {"number": 1, "unit": "reaction"},   // Reaction
  "Free",                              // No action required
  "Varies"                             // DM discretion
]
```

### Inline Tag Types

Common `tagType` values found in `inline_tag` references:

- **Combat**: `action`, `variantrule`, `condition`, `status`
- **Spells**: `spell`, `damage`, `dice`, `dc`
- **Items**: `item`, `itemEntry`
- **Creatures**: `creature`, `race`, `background`
- **Skills**: `skill`, `sense`
- **Other**: `vehicle`, `deck`, `table`, `class`, `feat`

### Cross-Reference Patterns

```python
# Pattern 1: Direct relationships (seeAlso*)
{
  "tagType": "action",
  "content": "Attack|XPHB",
  "referenceType": "seeAlsoAction"
}

# Pattern 2: Variant rules (optional content)
{
  "tagType": "variantrule",
  "content": "Spellcasting|XGE",
  "referenceType": "fromVariant"
}

# Pattern 3: Inline references (in descriptive text)
{
  "tagType": "spell",
  "content": "Fireball|PHB",
  "referenceType": "inline_tag"
}
```

### Building Relationship Types

Use the combination of `tagType` and `referenceType` to create meaningful graph edges:

```python
def get_relationship_type(ref):
    """
    Convert metadata reference into semantic relationship
    """
    mapping = {
        ("inline_tag", "spell"): "REFERENCES_SPELL",
        ("inline_tag", "condition"): "CAUSES_CONDITION",
        ("inline_tag", "damage"): "DEALS_DAMAGE",
        ("seeAlsoAction", "action"): "RELATED_TO",
        ("fromVariant", "variantrule"): "VARIANT_OF",
        ("inline_tag", "item"): "USES_ITEM",
    }

    key = (ref["referenceType"], ref["tagType"])
    return mapping.get(key, "REFERENCES")

# Usage:
for ref in metadata["references"]:
    rel_type = get_relationship_type(ref)
    graph.add_edge(source, target, type=rel_type)
```

## Next Steps

### For Your Agentic DM Project

1. **Choose Entry Types**: Decide which data to process (spells, items, classes, monsters, etc.)
2. **Render Data**: Run the pipeline on selected files
3. **Chunk Strategy**: Determine optimal chunk size for embeddings (entire entries vs paragraphs)
4. **Graph Schema**: Design your graph schema based on reference types (see patterns above)
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
