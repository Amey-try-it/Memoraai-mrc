from pathlib import Path
import sys

# Ensure the backend package root is importable regardless of pytest invocation path.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
