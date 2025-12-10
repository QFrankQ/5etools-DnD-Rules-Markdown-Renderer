#!/usr/bin/env python3
"""
Render all 5etools entries to markdown files
Saves each entry as an individual file for RAG/embedding purposes
"""

import time
from pathlib import Path
from renderer_client import RenderingClient


def render_all_entries(output_dir='rendered-entries'):
    """Render all entries and save to individual files"""

    client = RenderingClient()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Get available entity types
    summary = client.get_data_summary()

    print('=' * 60)
    print('5etools Markdown Renderer - Render All Entries')
    print('=' * 60)
    print(f'\n📊 Total entries: {sum(info["count"] for info in summary.values())}\n')

    total_start = time.time()
    total_rendered = 0

    for entity_type, info in sorted(summary.items()):
        count = info['count']
        print(f'📝 Rendering {entity_type:20} ({count:4} entries)...', end=' ', flush=True)

        # Create subdirectory for this type
        type_dir = output_path / entity_type
        type_dir.mkdir(exist_ok=True)

        start = time.time()
        try:
            # Render all entries of this type
            entries = client.render_type(entity_type, limit=None, save_to_file=False)

            # Save each entry to a file
            for entry in entries:
                # Create safe filename
                filename = f"{entry.name.replace(' ', '_').replace('/', '_')}_{entry.source}.md"
                filepath = type_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f'---\n')
                    f.write(f'name: {entry.name}\n')
                    f.write(f'source: {entry.source}\n')
                    f.write(f'type: {entry.metadata["type"]}\n')
                    if 'page' in entry.metadata:
                        f.write(f'page: {entry.metadata["page"]}\n')
                    f.write(f'---\n\n')
                    f.write(entry.markdown)

            elapsed = time.time() - start
            total_rendered += len(entries)
            print(f'✅ {elapsed:.2f}s ({len(entries)/elapsed:.0f} entries/s)')

        except Exception as e:
            print(f'❌ Error: {e}')

    total_elapsed = time.time() - total_start

    print('\n' + '=' * 60)
    print(f'✅ Complete! Rendered {total_rendered} entries in {total_elapsed:.1f}s')
    print(f'   Average: {total_rendered/total_elapsed:.0f} entries/second')
    print(f'   Output directory: {output_path.absolute()}')
    print('=' * 60)


if __name__ == '__main__':
    render_all_entries()
