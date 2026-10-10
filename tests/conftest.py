import sys
import os
from pathlib import Path

if os.environ.get("ONEPIECE_TEST_INSTALLED") != "1":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
