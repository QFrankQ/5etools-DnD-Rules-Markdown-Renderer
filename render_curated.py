#!/usr/bin/env python3
"""
Render curated D&D 5e rules with metadata extraction
Processes all filtered_*.json files in curated_rules/ directory
"""

import time
from pathlib import Path
from renderer_client import RenderingClient


def render_curated_rules(output_dir='curated-output', metadata_dir='curated-metadata'):
    """Render all curated rules files with metadata"""

    client = RenderingClient()
    curated_dir = Path('curated_rules')
    output_path = Path(output_dir)
    metadata_path = Path(metadata_dir)

    if not curated_dir.exists():
        print(f"❌ Directory not found: {curated_dir}")
        return

    curated_files = sorted(curated_dir.glob('filtered_*.json'))

    if not curated_files:
        print(f"❌ No filtered_*.json files found in {curated_dir}")
        return

    print('=' * 70)
    print('5etools Curated Rules Renderer - with Metadata Extraction')
    print('=' * 70)
    print(f'\n📁 Input directory: {curated_dir.absolute()}')
    print(f'📁 Markdown output: {output_path.absolute()}')
    print(f'📁 Metadata output: {metadata_path.absolute()}')
    print(f'📄 Found {len(curated_files)} curated files\n')

    total_start = time.time()
    total_entries = 0

    for curated_file in curated_files:
        print(f'📝 Processing {curated_file.name:35}', end=' ', flush=True)

        start = time.time()
        try:
            result = client.render_from_file(
                str(curated_file),
                save_to_file=False
            )

            entity_type = result['entityType']
            entries = result['results']

            if not entries:
                print('⚠️  No entries found')
                continue

            # Create output directory for this entity type
            type_dir = output_path / entity_type
            type_dir.mkdir(parents=True, exist_ok=True)

            # Save markdown files
            for entry in entries:
                # Create safe filename
                filename = f"{entry.name.replace(' ', '_').replace('/', '_')}_{entry.source}.md"
                filepath = type_dir / filename

                # Minimal frontmatter - just name and type
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f'---\n')
                    f.write(f'name: {entry.name}\n')
                    f.write(f'type: {entry.metadata["type"]}\n')
                    f.write(f'---\n\n')
                    f.write(entry.markdown)

            # Save metadata files to separate metadata directory
            metadata_type_dir = metadata_path / entity_type
            metadata_type_dir.mkdir(parents=True, exist_ok=True)

            import json
            for entry in entries:
                meta_filename = f"{entry.name.replace(' ', '_').replace('/', '_')}_{entry.source}.json"
                meta_path = metadata_type_dir / meta_filename

                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(entry.metadata, f, indent=2)

            elapsed = time.time() - start
            rate = len(entries) / elapsed if elapsed > 0 else 0
            total_entries += len(entries)

            print(f'✅ {len(entries):4} entries | {elapsed:.2f}s | {rate:.0f}/s')

        except Exception as e:
            print(f'❌ Error: {e}')

    total_elapsed = time.time() - total_start

    print('\n' + '=' * 70)
    print(f'✅ Complete! Rendered {total_entries} entries in {total_elapsed:.2f}s')
    print(f'   Average: {total_entries/total_elapsed:.0f} entries/second')
    print(f'   Markdown: {output_path.absolute()}')
    print(f'   Metadata: {metadata_path.absolute()}')
    print('=' * 70)

    # Show metadata summary
    print(f'\n📊 Metadata Summary:')
    if metadata_path.exists():
        for meta_type_dir in metadata_path.iterdir():
            if meta_type_dir.is_dir():
                meta_files = list(meta_type_dir.glob('*.json'))
                print(f'   {meta_type_dir.name:20} {len(meta_files):4} metadata files')


if __name__ == '__main__':
    render_curated_rules()
