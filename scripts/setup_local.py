"""Create a local-only secret file without overwriting an existing one."""
from pathlib import Path
import secrets

from cryptography.fernet import Fernet

root = Path(__file__).resolve().parents[1]
env_file = root / ".env"
if env_file.exists():
    raise SystemExit(".env already exists; leaving it untouched.")
env_file.write_text(
    "\n".join([
        f'DJANGO_SECRET_KEY="{secrets.token_urlsafe(64)}"',
        f'DATA_ENCRYPTION_KEY="{Fernet.generate_key().decode("ascii")}"',
        "DEBUG=1",
        "ALLOWED_HOSTS=127.0.0.1,localhost",
        "",
    ]),
    encoding="utf-8",
)
print("Created ignored .env with unique local secrets. Back it up securely; losing the encryption key makes encrypted records unreadable.")
