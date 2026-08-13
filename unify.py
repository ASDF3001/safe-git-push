import re
from pathlib import Path

UNIFIED_URL = """import os
if os.name == 'nt':
    SELF_UPDATE_RAW_URL = "https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/safe_git_push.py"
else:
    SELF_UPDATE_RAW_URL = "https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/linux/safe_git_push.py"
"""

for target in ["linux/safe_git_push.py", "windows/safe_git_push.py"]:
    text = Path(target).read_text(encoding="utf-8")
    text = re.sub(r'SELF_UPDATE_RAW_URL\s*=\s*".*?"\n', UNIFIED_URL, text, count=1)
    Path(target).write_text(text, encoding="utf-8")
    
# Copy to root!
Path("safe_git_push.py").write_text(Path("linux/safe_git_push.py").read_text(encoding="utf-8"), encoding="utf-8")
