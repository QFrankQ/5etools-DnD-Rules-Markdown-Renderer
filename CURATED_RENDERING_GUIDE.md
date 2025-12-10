# Curated Rules Rendering Guide

## Quick Start

Render all your curated D&D 5e rules with metadata extraction:

```bash
python3 render_curated.py
```

This will create two separate directories:
- **`curated-output/`** - Markdown files organized by type
- **`curated-metadata/`** - JSON metadata files for building knowledge graphs

## Output Structure

```
curated-output/
├── action/
│   ├── Attack_PHB.md
│   └── ...
├── feat/
│   ├── Agent_of_Order_SatO.md
│   └── ...
├── item/
│   ├── +1_All-Purpose_Tool_TCE.md
│   └── ...
└── ...

curated-metadata/
├── action/
│   ├── attack_PHB.json
│   └── ...
├── feat/
│   ├── agent_of_order_SatO.json
│   └── ...
└── ...
```

## Markdown File Format

Each markdown file has minimal frontmatter:

```markdown
---
name: Agent of Order
type: feat
---

## Agent of Order

Prerequisite: 4th level, scion of the outer planes (lawful outer plane)

[rest of content...]
```

**Note**: `source` and `page` are NOT in the frontmatter - they're only in the metadata JSON files.

## Metadata File Format

Each metadata JSON file contains graph-ready references:

```json
{
  "type": "feat",
  "name": "Agent of Order",
  "source": "SatO",
  "page": 10,
  "file": "filtered_feats.json",
  "references": [
    {
      "tagType": "damage",
      "content": "1d8",
      "referenceType": "inline_tag"
    }
  ]
}
```

### Metadata Fields

- **`type`** - Entity type (spell, item, feat, etc.)
- **`name`** - Entry name
- **`source`** - Source book abbreviation
- **`page`** - Page number in source book
- **`file`** - Original JSON filename
- **`references`** - Array of cross-references for knowledge graph

### Reference Types

The metadata extracts several types of references:

1. **Inline tags** - `{@spell fireball}`, `{@item longsword}`, etc.
2. **seeAlso fields** - `seeAlsoSpell`, `seeAlsoItem`, etc.
3. **Variant sources** - `fromVariant` field
4. **Type-specific fields** - level, school, rarity, etc.

## Performance

Your 2,134 curated entries render in approximately **~3-8 seconds** depending on system:

| File | Type | Count | Time |
|------|------|-------|------|
| filtered_actions.json | action | 20 | ~0.3s |
| filtered_conditions.json | condition | 15 | ~0.1s |
| filtered_feats.json | feat | 150 | ~0.3s |
| filtered_items.json | item | 1,681 | ~5s |
| filtered_objects.json | object | 27 | ~0.5s |
| filtered_optionalfeatures.json | optionalfeature | 127 | ~0.7s |
| filtered_variant_rules.json | variantrule | 114 | ~0.4s |

**Total**: ~2,134 entries in ~8 seconds (257 entries/second average)

## For RAG/Embedding

The markdown files are ready for:
- Vector database embedding
- LLM context injection
- Document retrieval

The metadata files enable:
- Knowledge graph construction
- Cross-reference navigation
- Semantic relationship mapping

## Customization

Edit `render_curated.py` to change:
- Output directories (default: `curated-output/` and `curated-metadata/`)
- Source directory (default: `curated_rules/`)
- File patterns (default: `filtered_*.json`)
