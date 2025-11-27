#!/usr/bin/env python3
"""
Render all curated D&D rules from curated_rules directory

This script processes your filtered/combined rule files for the RAG system.
"""

from dnd_renderer import DnDRenderer
from pathlib import Path
import json

def main():
    print("=" * 60)
    print("Rendering Curated D&D Rules for RAG System")
    print("=" * 60)

    # Initialize renderer
    renderer = DnDRenderer()

    # Your curated rules directory
    rules_dir = Path(__file__).parent / "curated_rules"
    output_dir = Path(__file__).parent / "output" / "curated_rules"

    # Get all JSON files
    rule_files = sorted(rules_dir.glob("*.json"))

    print(f"\nFound {len(rule_files)} rule files to process:\n")

    total_entries = 0
    results = []

    for rule_file in rule_files:
        print(f"📄 Processing: {rule_file.name}")

        try:
            stats = renderer.render_file(
                str(rule_file),
                str(output_dir),
                verbose=False
            )

            total_entries += stats['success_count']

            results.append({
                'file': rule_file.name,
                'entries': stats['success_count'],
                'errors': stats['error_count'],
                'status': '✅' if stats['error_count'] == 0 else '⚠️'
            })

            print(f"   {stats['success_count']} entries rendered")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'file': rule_file.name,
                'entries': 0,
                'errors': 1,
                'status': '❌'
            })

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nTotal entries rendered: {total_entries}")
    print(f"Output directory: {output_dir}\n")

    print("Breakdown by file:")
    print(f"{'File':<40} {'Entries':<10} {'Status'}")
    print("-" * 60)
    for r in results:
        print(f"{r['file']:<40} {r['entries']:<10} {r['status']}")

    # Show output structure
    print("\n" + "=" * 60)
    print("OUTPUT STRUCTURE")
    print("=" * 60)

    # Count files by type
    type_counts = {}
    if output_dir.exists():
        for type_dir in output_dir.iterdir():
            if type_dir.is_dir() and type_dir.name != 'metadata':
                count = len(list(type_dir.glob('*.md')))
                type_counts[type_dir.name] = count

    print(f"\nMarkdown files by type:")
    for type_name, count in sorted(type_counts.items()):
        print(f"  {type_name + '/':<20} {count:>4} files")

    print(f"\nMetadata files:")
    metadata_dir = output_dir / 'metadata'
    if metadata_dir.exists():
        total_meta = sum(
            len(list(d.glob('*.json')))
            for d in metadata_dir.iterdir()
            if d.is_dir()
        )
        print(f"  metadata/            {total_meta:>4} files")

    print("\n" + "=" * 60)
    print("✅ All rules rendered successfully!")
    print("=" * 60)

    print(f"\nReady for RAG system:")
    print(f"  • Markdown files: {output_dir}/")
    print(f"  • Metadata files: {output_dir}/metadata/")
    print(f"\nNext steps:")
    print("  1. Chunk the markdown files for embedding")
    print("  2. Build knowledge graph from metadata references")
    print("  3. Create hybrid vector + graph RAG system")


if __name__ == "__main__":
    main()
