"""Test isolation for telegraphist.

``telegram_backup`` runs side effects at import time: it calls ``load_dotenv()``
(which would read the real ``.env``) and creates the ``output/`` tree. Patch both
out before the module is first imported so tests never touch real account data,
the network, or real config. No client is ever constructed.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Dummy credentials: import exits(1) when API_ID/API_HASH are unset.
os.environ["API_ID"] = "1"
os.environ["API_HASH"] = "test"

# Prevent the real .env from being read at import time.
import dotenv  # noqa: E402

dotenv.load_dotenv = lambda *args, **kwargs: None  # type: ignore[assignment]

# Suppress creation of output/ while the module is imported. sys.modules caches
# the result, so the test module's own ``import telegram_backup`` is a no-op.
_original_makedirs = os.makedirs
os.makedirs = lambda *args, **kwargs: None  # type: ignore[assignment]
try:
    import telegram_backup  # noqa: F401,E402
finally:
    os.makedirs = _original_makedirs
