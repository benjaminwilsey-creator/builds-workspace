"""pytest conftest — add v1.4 root to sys.path so modules resolve correctly."""
import sys
from pathlib import Path

# Ensure the v1.4 root is on sys.path so `import capital`, `import strategy`,
# `from agents.base import ...`, etc. all resolve without installing the package.
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
