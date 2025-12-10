# 5etools Rendering Service for RAG Systems

This rendering service converts D&D 5e JSON data into clean Markdown format, perfect for embedding in vector databases for RAG (Retrieval-Augmented Generation) systems.

## Overview

The service consists of two components:
1. **Node.js Rendering Service** (`renderer-service.mjs`) - Uses the official 5etools rendering engine
2. **Python Client** (`renderer_client.py`) - Pythonic interface for calling the service

## Quick Start

### Prerequisites

- Node.js (v18+)
- Python 3.7+

### Basic Usage

```python
from renderer_client import RenderingClient

# Initialize the client
client = RenderingClient()

# Get summary of available data
summary = client.get_data_summary()
print(f"Total spells: {summary['spell']['count']}")  # 456 spells

# Render spells to markdown
spells = client.render_type('spell', limit=10, save_to_file=True)

# Access the rendered markdown
for spell in spells:
    print(f"## {spell.name}")
    print(spell.markdown)
    print(f"Source: {spell.source}, Page: {spell.metadata['page']}")
```

## Supported Entity Types

| Entity Type | Count | Status | Notes |
|------------|-------|--------|-------|
| **spell** | 456 | ✅ Working | Fully supported |
| **item** | 2542 | ✅ Working | Fully supported |
| **monster** | 450 | ✅ Working | Fully supported with all abilities |
| **action** | 48 | ✅ Working | Fully supported |
| **feat** | 272 | ✅ Working | Fully supported |
| **condition** | 30 | ✅ Working | Basic support |
| **background** | 182 | ✅ Working | Basic support |
| **variantrule** | 239 | ✅ Working | Basic support |
| **race** | 158 | ⚠️ Partial | May have rendering issues |

## Python API

### RenderingClient

```python
from renderer_client import RenderingClient, RenderedEntry

client = RenderingClient()
```

#### Methods

**`get_data_summary() -> Dict[str, Dict[str, Any]]`**

Returns a summary of all available data:

```python
summary = client.get_data_summary()
# {
#   'spell': {'files': ['spells/spells-phb.json'], 'count': 456},
#   'action': {'files': ['actions.json'], 'count': 48},
#   ...
# }
```

**`render_type(entity_type: str, limit: int = None, save_to_file: bool = True) -> List[RenderedEntry]`**

Render entries of a specific type:

```python
# Render 10 spells
spells = client.render_type('spell', limit=10)

# Render all actions without saving
actions = client.render_type('action', save_to_file=False)
```

**`render_multiple_types(entity_types: List[str], limit: int = None, save_to_file: bool = True) -> Dict[str, List[RenderedEntry]]`**

Render multiple entity types at once:

```python
results = client.render_multiple_types(
    ['spell', 'action', 'feat'],
    limit=5
)

for entity_type, entries in results.items():
    print(f"{entity_type}: {len(entries)} entries")
```

**`get_available_types() -> List[str]`**

Get list of all available entity types:

```python
types = client.get_available_types()
# ['spell', 'action', 'item', 'monster', ...]
```

### RenderedEntry

Each rendered entry is returned as a `RenderedEntry` object:

```python
@dataclass
class RenderedEntry:
    name: str              # Entry name (e.g., "Fireball")
    source: str            # Source book (e.g., "PHB")
    markdown: str          # Rendered markdown content
    metadata: Dict[str, Any]  # Additional metadata (type, file, page)
```

## Output Format

The service generates markdown files with frontmatter metadata:

```markdown
---
name: Acid Splash
source: PHB
type: spell
page: 211
---

#### Acid Splash
*Conjuration cantrip*
___
- **Casting Time:** 1 action
- **Range:** 60 feet
- **Components:** V, S
- **Duration:** Instantaneous
---
You hurl a bubble of acid. Choose one creature you can see within range...
```

## Output Directory Structure

When `save_to_file=True`, files are saved to `markdown-output/`:

```
markdown-output/
├── spell/
│   ├── acid_splash_PHB.md
│   ├── fireball_PHB.md
│   └── _all_spells.md          # Combined file
├── action/
│   ├── attack_PHB.md
│   └── _all_actions.md
└── feat/
    ├── alert_PHB.md
    └── _all_feats.md
```

## Example: Embedding for RAG

```python
from renderer_client import RenderingClient
from sentence_transformers import SentenceTransformer

# Initialize
client = RenderingClient()
model = SentenceTransformer('all-MiniLM-L6-v2')

# Render all spells
spells = client.render_type('spell', save_to_file=False)

# Create embeddings
for spell in spells:
    # Combine name and markdown for context
    text = f"{spell.name}\n\n{spell.markdown}"

    # Generate embedding
    embedding = model.encode(text)

    # Store in your vector database
    # vector_db.add(
    #     id=f"{spell.source}_{spell.name}",
    #     embedding=embedding,
    #     metadata={
    #         'name': spell.name,
    #         'source': spell.source,
    #         'type': 'spell',
    #         'page': spell.metadata['page']
    #     },
    #     text=text
    # )
```

## Running the Node.js Service Directly

You can also run the service directly for testing:

```bash
# Run with demo output
node renderer-service.mjs

# Use via stdin (for Python integration)
echo '{"action":"summary"}' | node renderer-service.mjs
echo '{"action":"render","type":"spell","limit":5}' | node renderer-service.mjs
```

## Troubleshooting

### Module Loading Errors

If you see `Parser is not defined` or similar errors, ensure all browser globals are mocked correctly in `renderer-service.mjs`.

### Item/Monster Rendering (FIXED)

Items and monsters now render successfully! The following mocks were implemented:
- jQuery (`$`) - with proper method chaining support using `arguments.length`
- `UiUtil` - with `intToBonus()` and `strToInt()` functions
- `PrereleaseUtil` and `BrewUtil2` - for homebrew content
- Meta object initialization - with `_typeStack` array for rendering context

All major entity types (spells, items, monsters, actions, feats) now work correctly.

### Python Timeout

If rendering takes too long, increase the timeout in `renderer_client.py`:

```python
result = subprocess.run(
    ...,
    timeout=120  # Increase from 60 to 120 seconds
)
```

## Data Sources

All data comes from the `data/` directory:
- Spells: `data/spells/spells-phb.json`, `data/spells/spells-xge.json`
- Actions: `data/actions.json`
- Feats: `data/feats.json`
- And many more...

## Architecture

```
┌─────────────────┐
│  Python Client  │
│ (renderer_      │
│  client.py)     │
└────────┬────────┘
         │ JSON over stdin/stdout
         ▼
┌─────────────────┐
│  Node.js Service│
│ (renderer-      │
│  service.mjs)   │
└────────┬────────┘
         │ imports
         ▼
┌─────────────────┐
│  5etools Engine │
│ ├── render.js   │
│ ├── render-     │
│ │   markdown.js │
│ ├── parser.js   │
│ └── utils.js    │
└─────────────────┘
```

## License

This rendering service wraps the 5etools project. Please respect the original 5etools license and terms of use.

## Contributing

To add support for more entity types:
1. Add appropriate mocks to `renderer-service.mjs`
2. Test with small samples first
3. Update this README with status

## Future Improvements

- [ ] Complete jQuery and UiUtil mocks for items/monsters
- [ ] Add batch processing for large datasets
- [ ] Add caching for faster repeated renders
- [ ] Support for custom output formats (JSON, HTML)
- [ ] Progress bars for long-running renders
