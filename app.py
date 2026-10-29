import os
import sys
from pathlib import Path
import runpy

# Ensure ResponseAI directory is in sys.path
root_dir = Path(__file__).resolve().parent
sub_dir = root_dir / "ResponseAI"

if str(sub_dir) not in sys.path:
    sys.path.insert(0, str(sub_dir))

os.chdir(sub_dir)

# Execute ResponseAI/app.py
target_app = sub_dir / "app.py"
runpy.run_path(str(target_app), run_name="__main__")
