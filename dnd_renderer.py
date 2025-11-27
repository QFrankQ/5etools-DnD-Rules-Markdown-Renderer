"""
D&D 5e Renderer - Python wrapper for the Node.js rendering pipeline

This module provides a Python interface to render D&D 5e content from 5etools JSON
to Markdown format, along with metadata extraction for graph/vector databases.
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def find_node() -> str:
    """Find node executable in PATH or common locations."""
    # First try PATH
    node_path = shutil.which('node')
    if node_path:
        return node_path

    # Try common locations on macOS/Linux
    common_paths = [
        '/usr/local/bin/node',
        '/usr/bin/node',
        '/opt/homebrew/bin/node'
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    raise FileNotFoundError(
        "Node.js not found. Please install Node.js or add it to your PATH"
    )


NODE_PATH = find_node()


class DnDRenderer:
    """
    Python interface to the D&D 5e markdown renderer.

    Example:
        >>> renderer = DnDRenderer()
        >>> renderer.render_file("data/spells/spells-phb.json", "./output")
        >>> markdown = renderer.get_rendered("spell", "Fireball", "PHB")
    """

    def __init__(self, renderer_path: Optional[str] = None):
        """
        Initialize the renderer.

        Args:
            renderer_path: Path to the renderer directory containing render-to-markdown.js.
                          Defaults to current directory (where this file is located).
        """
        if renderer_path is None:
            renderer_path = Path(__file__).parent

        self.renderer_path = Path(renderer_path).resolve()
        self.script = self.renderer_path / "render-to-markdown.js"
        self.node_path = NODE_PATH

        if not self.script.exists():
            raise FileNotFoundError(
                f"Renderer script not found at {self.script}. "
                f"Make sure the 5etools-src directory is properly set up."
            )

        logger.info(f"Using node: {self.node_path}")

    def list_data_files(self) -> List[str]:
        """List available D&D data files."""
        result = subprocess.run(
            [self.node_path, str(self.script), "--list"],
            cwd=str(self.renderer_path),
            capture_output=True,
            text=True,
            check=True
        )

        lines = result.stdout.strip().split('\n')
        files = [line.strip().replace('- ', '') for line in lines if line.strip().startswith('-')]
        return files

    def render_file(self, input_file: str, output_dir: str, verbose: bool = True) -> Dict[str, Any]:
        """Render a single D&D JSON file to markdown."""
        input_path = self._resolve_path(input_file)
        output_path = Path(output_dir).resolve()

        logger.info(f"Rendering {input_path} to {output_path}")

        result = subprocess.run(
            [self.node_path, str(self.script), "--input", str(input_path), "--output-dir", str(output_path)],
            cwd=str(self.renderer_path),
            capture_output=True,
            text=True,
            check=True
        )

        if verbose:
            print(result.stdout)

        stats = self._parse_output(result.stdout)
        stats['output_dir'] = str(output_path)
        return stats

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to renderer_path or as absolute."""
        path_obj = Path(path)
        return path_obj if path_obj.is_absolute() else (self.renderer_path / path).resolve()

    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse renderer output for statistics."""
        stats = {'success_count': 0, 'error_count': 0}
        for line in output.split('\n'):
            if 'Completed:' in line:
                try:
                    parts = line.split()
                    stats['success_count'] = int(parts[1])
                    stats['error_count'] = int(parts[3])
                except (IndexError, ValueError):
                    pass
        return stats


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    renderer = DnDRenderer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        print("Available data files:")
        for file in renderer.list_data_files():
            print(f"  - {file}")
    else:
        print("Rendering spells...")
        stats = renderer.render_file("data/actions.json", "./output/test")
        print(f"Stats: {stats}")
