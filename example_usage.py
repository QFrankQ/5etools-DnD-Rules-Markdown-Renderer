"""
Example usage of the D&D Renderer Python wrapper

This demonstrates how to integrate the renderer into your Agentic DM project.
"""

from renderer_client import DnDRenderer
from pathlib import Path


def example_basic_usage():
    """Basic rendering example"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Rendering")
    print("=" * 60)

    renderer = DnDRenderer()

    # Render a single file
    stats = renderer.render_file(
        "data/actions.json",
        "./output/basic_example"
    )

    print(f"\nRendered {stats['success_count']} entries successfully")
    print(f"Errors: {stats['error_count']}")


def example_get_specific_entry():
    """Get specific rendered content"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Get Specific Entry")
    print("=" * 60)

    renderer = DnDRenderer()

    # First render if not already done
    renderer.render_file("data/spells/spells-phb.json", "./output/spells")

    # Get specific spell
    fireball_md = renderer.get_rendered("spell", "Fireball", "PHB", "./output/spells")
    fireball_meta = renderer.get_metadata("spell", "Fireball", "PHB", "./output/spells")

    if fireball_md:
        print("\n📜 Fireball Spell:")
        print(fireball_md)

    if fireball_meta:
        print("\n📊 Metadata:")
        print(f"  Type: {fireball_meta['type']}")
        print(f"  Source: {fireball_meta['source']}")
        print(f"  References: {len(fireball_meta['references'])} found")
        for ref in fireball_meta['references']:
            print(f"    - {ref['tagType']}: {ref['content']}")


def example_batch_processing():
    """Process all entries of a type"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Batch Processing for RAG")
    print("=" * 60)

    renderer = DnDRenderer()

    # Render all spells
    renderer.render_file("data/spells/spells-phb.json", "./output/rag_example")

    # Get all spell entries
    spells = renderer.get_all_entries("spell", "./output/rag_example")

    print(f"\n📚 Found {len(spells)} spells")

    # Example: Prepare for embedding
    for spell in spells[:3]:  # First 3 as example
        print(f"\n  {spell['name']} ({spell['source']})")
        print(f"    Markdown length: {len(spell['markdown'])} chars")

        if spell['metadata']:
            refs = spell['metadata'].get('references', [])
            print(f"    References: {len(refs)}")


def example_knowledge_graph():
    """Build knowledge graph from metadata"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Knowledge Graph Construction")
    print("=" * 60)

    renderer = DnDRenderer()

    # Render spells
    renderer.render_file("data/spells/spells-phb.json", "./output/graph_example")

    # Get all spells with metadata
    spells = renderer.get_all_entries("spell", "./output/graph_example")

    # Build graph relationships
    graph = []

    for spell in spells[:10]:  # First 10 as example
        if not spell['metadata']:
            continue

        spell_name = spell['metadata']['name']

        for ref in spell['metadata']['references']:
            # Create edges based on reference types
            if ref['tagType'] == 'damage':
                graph.append({
                    'source': spell_name,
                    'relationship': 'DEALS_DAMAGE',
                    'target': ref['content']
                })
            elif ref['tagType'] == 'condition':
                graph.append({
                    'source': spell_name,
                    'relationship': 'INFLICTS_CONDITION',
                    'target': ref['content']
                })
            elif ref['tagType'] == 'spell':
                graph.append({
                    'source': spell_name,
                    'relationship': 'REFERENCES_SPELL',
                    'target': ref['content']
                })

    print(f"\n🕸️  Created {len(graph)} graph relationships")
    print("\nSample relationships:")
    for edge in graph[:5]:
        print(f"  {edge['source']} --[{edge['relationship']}]-> {edge['target']}")


def example_integration_with_rag():
    """Example integration with a RAG system"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: RAG System Integration")
    print("=" * 60)

    renderer = DnDRenderer()

    # Render multiple content types
    content_types = [
        ("data/spells/spells-phb.json", "spells"),
        ("data/actions.json", "actions"),
        ("data/conditionsdiseases.json", "conditions")
    ]

    output_dir = "./output/rag_system"

    print("\n📦 Rendering D&D content for RAG system...")

    total_entries = 0
    for input_file, name in content_types:
        stats = renderer.render_file(input_file, output_dir, verbose=False)
        print(f"  ✓ {name}: {stats['success_count']} entries")
        total_entries += stats['success_count']

    print(f"\n✨ Total: {total_entries} entries ready for embedding")

    # Example: Organize for vector database
    print("\n🗂️  Organizing for vector database...")

    # Get all spell entries for embedding
    spells = renderer.get_all_entries("spell", output_dir)

    # Structure for vector DB insertion
    vector_db_entries = []
    for spell in spells[:5]:  # First 5 as example
        entry = {
            'id': f"{spell['source']}_{spell['name'].replace(' ', '_')}",
            'text': spell['markdown'],
            'metadata': {
                'type': spell['metadata']['type'] if spell['metadata'] else 'unknown',
                'name': spell['name'],
                'source': spell['source'],
                'references': spell['metadata']['references'] if spell['metadata'] else []
            }
        }
        vector_db_entries.append(entry)

    print(f"  Prepared {len(vector_db_entries)} entries for vector DB")
    print("\n  Sample entry structure:")
    sample = vector_db_entries[0]
    print(f"    ID: {sample['id']}")
    print(f"    Text length: {len(sample['text'])} chars")
    print(f"    Metadata: {list(sample['metadata'].keys())}")


def example_agentic_dm_workflow():
    """Complete workflow for Agentic DM project"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Complete Agentic DM Workflow")
    print("=" * 60)

    renderer = DnDRenderer()

    print("\n🎯 Step 1: Render all D&D content")
    # In production, you'd use render_all(), but for demo we'll do a subset
    stats = renderer.render_file("data/spells/spells-phb.json", "./output/agentic_dm")
    print(f"  ✓ Rendered {stats['success_count']} entries")

    print("\n🎯 Step 2: Extract for embeddings")
    spells = renderer.get_all_entries("spell", "./output/agentic_dm")
    print(f"  ✓ Extracted {len(spells)} spell entries")

    print("\n🎯 Step 3: Build knowledge graph")
    # Build spell -> damage relationships
    damage_graph = {}
    for spell in spells:
        if not spell['metadata']:
            continue

        spell_name = spell['metadata']['name']
        damages = [
            ref['content']
            for ref in spell['metadata']['references']
            if ref['tagType'] == 'damage'
        ]

        if damages:
            damage_graph[spell_name] = damages

    print(f"  ✓ Built graph with {len(damage_graph)} spell->damage relationships")

    print("\n🎯 Step 4: Query simulation")
    # Simulate a DM query
    query = "What spells deal fire damage?"

    # In a real system, you'd use vector search + graph traversal
    # For this example, we'll just demonstrate the data structure
    relevant_spells = [
        spell for spell in spells[:10]  # Limit for demo
        if 'fire' in spell['markdown'].lower()
    ]

    print(f"  Query: '{query}'")
    print(f"  ✓ Found {len(relevant_spells)} relevant spells (from sample)")

    if relevant_spells:
        print("\n  📋 Sample results:")
        for spell in relevant_spells[:3]:
            print(f"    - {spell['name']}: {spell['markdown'][:100]}...")


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("D&D RENDERER - INTEGRATION EXAMPLES")
    print("=" * 60)

    examples = {
        '1': ('Basic rendering', example_basic_usage),
        '2': ('Get specific entry', example_get_specific_entry),
        '3': ('Batch processing', example_batch_processing),
        '4': ('Knowledge graph', example_knowledge_graph),
        '5': ('RAG integration', example_integration_with_rag),
        '6': ('Agentic DM workflow', example_agentic_dm_workflow),
        'all': ('Run all examples', None)
    }

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\nAvailable examples:")
        for key, (name, _) in examples.items():
            if key != 'all':
                print(f"  {key}. {name}")
        print(f"  all. Run all examples")

        choice = input("\nSelect example (or 'all'): ").strip()

    if choice == 'all':
        for key, (name, func) in examples.items():
            if key != 'all' and func:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ Error in example {key}: {e}")
    elif choice in examples and examples[choice][1]:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print(f"\n❌ Invalid choice: {choice}")

    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)
