"""Small deterministic helpers. Hashes identify stored evidence, not its truth."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from .config import PUBLISHERS, DISCOVERY_HOSTS


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_time(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timezone required')
    return dt.astimezone(timezone.utc)


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    # Same-directory rename prevents a truncated output after an interrupted refresh.
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8')
    tmp.replace(path)


def official_url(url):
    try:
        p = urlparse(url)
        return p.scheme == 'https' and p.hostname in PUBLISHERS and not p.username and not p.password and p.port in (None, 443)
    except (ValueError, TypeError, AttributeError):
        return False


def allowed_url(url, discovery=False):
    try:
        p = urlparse(url)
        return official_url(url) or (discovery and p.scheme == 'https' and p.hostname in DISCOVERY_HOSTS and not p.username and not p.password and p.port in (None, 443))
    except (ValueError, TypeError, AttributeError):
        return False
