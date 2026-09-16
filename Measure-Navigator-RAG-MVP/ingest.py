from __future__ import annotations

import json

from config import settings
from service import NavigatorService


if __name__ == "__main__":
    print(json.dumps(NavigatorService(settings).ingestion.build(), indent=2))

