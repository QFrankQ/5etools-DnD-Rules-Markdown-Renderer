"""
Python Client for 5etools Rendering Service
Provides a Pythonic interface to render D&D rules to Markdown
"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RenderedEntry:
    """Represents a rendered D&D entry"""
    name: str
    source: str
    markdown: str
    metadata: Dict[str, Any]


class RenderingClient:
    """Python client for the Node.js rendering service"""

    def __init__(self, service_path: Optional[Path] = None):
        """
        Initialize the rendering client

        Args:
            service_path: Path to renderer-service.mjs (defaults to same directory as this file)
        """
        if service_path is None:
            service_path = Path(__file__).parent / "renderer-service.mjs"

        self.service_path = service_path

        if not self.service_path.exists():
            raise FileNotFoundError(f"Renderer service not found at {self.service_path}")

    def _call_service(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the Node.js rendering service

        Args:
            request: Request dictionary with action and parameters

        Returns:
            Response dictionary from the service
        """
        try:
            # Convert request to JSON
            request_json = json.dumps(request)

            # Call Node.js service
            # Try to find node in common locations
            node_path = 'node'
            import shutil
            node_binary = shutil.which('node')
            if node_binary:
                node_path = node_binary
            elif os.path.exists('/usr/local/bin/node'):
                node_path = '/usr/local/bin/node'

            result = subprocess.run(
                [node_path, str(self.service_path), '--stdin'],
                input=request_json,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise RuntimeError(f"Service error: {result.stderr}")

            # Parse response
            if not result.stdout.strip():
                raise RuntimeError(f"Service returned empty output. stderr: {result.stderr}")

            # Debug: print what we got (uncomment for debugging)
            # print(f"DEBUG stdout: {result.stdout[:500] if result.stdout else 'NONE'}")
            # print(f"DEBUG stderr: {result.stderr if result.stderr else 'NONE'}")

            response = json.loads(result.stdout)

            if not response.get('success', False):
                raise RuntimeError(f"Service returned error: {response.get('error', 'Unknown error')}")

            return response.get('data', {})

        except subprocess.TimeoutExpired:
            raise RuntimeError("Service call timed out")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse service response: {e}")

    def get_data_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summary of available data

        Returns:
            Dictionary mapping entity types to their metadata
        """
        request = {'action': 'summary'}
        return self._call_service(request)

    def render_type(
        self,
        entity_type: str,
        limit: Optional[int] = None,
        save_to_file: bool = True
    ) -> List[RenderedEntry]:
        """
        Render all entries of a specific type

        Args:
            entity_type: Type of entity (spell, item, monster, etc.)
            limit: Maximum number of entries to render (None for all)
            save_to_file: Whether to save results to markdown files

        Returns:
            List of RenderedEntry objects
        """
        request = {
            'action': 'render',
            'type': entity_type,
            'limit': limit,
            'saveToFile': save_to_file
        }

        results = self._call_service(request)

        return [
            RenderedEntry(
                name=entry['name'],
                source=entry['source'],
                markdown=entry['markdown'],
                metadata=entry['metadata']
            )
            for entry in results
        ]

    def render_multiple_types(
        self,
        entity_types: List[str],
        limit: Optional[int] = None,
        save_to_file: bool = True
    ) -> Dict[str, List[RenderedEntry]]:
        """
        Render multiple entity types at once

        Args:
            entity_types: List of entity types to render
            limit: Maximum number of entries per type (None for all)
            save_to_file: Whether to save results to markdown files

        Returns:
            Dictionary mapping entity types to lists of RenderedEntry objects
        """
        request = {
            'action': 'render_multiple',
            'types': entity_types,
            'limit': limit,
            'saveToFile': save_to_file
        }

        results = self._call_service(request)

        return {
            entity_type: [
                RenderedEntry(
                    name=entry['name'],
                    source=entry['source'],
                    markdown=entry['markdown'],
                    metadata=entry['metadata']
                )
                for entry in entries
            ]
            for entity_type, entries in results.items()
        }

    def render_from_file(
        self,
        file_path: str,
        limit: Optional[int] = None,
        save_to_file: bool = True
    ) -> Dict[str, Any]:
        """
        Render entries from a specific JSON file (e.g., curated rules)

        Args:
            file_path: Path to the JSON file
            limit: Maximum number of entries to render (None for all)
            save_to_file: Whether to save results to markdown files

        Returns:
            Dictionary with 'entityType' and 'results' (list of RenderedEntry objects)
        """
        request = {
            'action': 'render_file',
            'filePath': file_path,
            'limit': limit,
            'saveToFile': save_to_file
        }

        result = self._call_service(request)

        entity_type = result.get('entityType')
        entries = result.get('results', [])

        return {
            'entityType': entity_type,
            'results': [
                RenderedEntry(
                    name=entry['name'],
                    source=entry['source'],
                    markdown=entry['markdown'],
                    metadata=entry['metadata']
                )
                for entry in entries
            ]
        }

    def get_available_types(self) -> List[str]:
        """
        Get list of all available entity types

        Returns:
            List of entity type names
        """
        summary = self.get_data_summary()
        return list(summary.keys())


def main():
    """Demo usage of the rendering client"""
    print("=== 5etools Python Rendering Client ===\n")

    # Initialize client
    client = RenderingClient()

    # Get data summary
    print("📊 Available Data:")
    summary = client.get_data_summary()
    for entity_type, info in sorted(summary.items()):
        print(f"  - {entity_type}: {info['count']} entries")

    print("\n🔨 Rendering Sample Entries...\n")

    # Render a few spells
    print("Rendering 3 spells...")
    spells = client.render_type('spell', limit=3, save_to_file=True)

    for spell in spells:
        print(f"\n{'='*60}")
        print(f"Name: {spell.name}")
        print(f"Source: {spell.source}")
        print(f"Type: {spell.metadata['type']}")
        print(f"\nMarkdown Preview (first 200 chars):")
        print(spell.markdown[:200] + "...")

    print("\n" + "="*60)

    # Render multiple types at once
    print("\n🚀 Rendering multiple types...")
    results = client.render_multiple_types(
        entity_types=['action', 'item', 'monster'],
        limit=2,
        save_to_file=True
    )

    for entity_type, entries in results.items():
        print(f"\n✓ Rendered {len(entries)} {entity_type}(s)")
        for entry in entries:
            print(f"  - {entry.name} ({entry.source})")

    print("\n✅ Done! Check the markdown-output/ directory for results.")


if __name__ == "__main__":
    main()
