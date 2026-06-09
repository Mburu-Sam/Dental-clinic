import json
from pathlib import Path

SERVICE_FILE = Path(__file__).resolve().parent / 'data' / 'services.json'


def load_services():
    try:
        with SERVICE_FILE.open(encoding='utf-8') as fh:
            services = json.load(fh)
    except FileNotFoundError:
        return []
    if not isinstance(services, list):
        return []
    return sorted(
        [svc for svc in services if svc.get('is_active', True)],
        key=lambda item: item.get('order', 0)
    )
