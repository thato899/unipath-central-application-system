"""Encrypted model fields for data that is sensitive if a database copy leaks."""
import json
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

def _cipher():
    try:
        return Fernet(settings.DATA_ENCRYPTION_KEY.encode("ascii"))
    except (AttributeError, UnicodeEncodeError, ValueError) as exc:
        raise ImproperlyConfigured("DATA_ENCRYPTION_KEY must be a valid Fernet key.") from exc

class EncryptedTextField(models.TextField):
    """Fernet-encrypted text; ciphertext is stored in the database."""
    description = "Fernet-encrypted text"

    def get_prep_value(self, value):
        if value is None:
            return None
        return _cipher().encrypt(str(value).encode("utf-8")).decode("ascii")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            return _cipher().decrypt(value.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError) as exc:
            raise ImproperlyConfigured("Encrypted data could not be decrypted. Check the encryption key and backup.") from exc

class EncryptedJSONField(EncryptedTextField):
    """JSON-compatible Python values stored only as authenticated ciphertext."""
    description = "Fernet-encrypted JSON"

    def get_prep_value(self, value):
        if value is None:
            return None
        return super().get_prep_value(json.dumps(value, ensure_ascii=False, separators=(",", ":")))

    def from_db_value(self, value, expression, connection):
        decrypted = super().from_db_value(value, expression, connection)
        return json.loads(decrypted) if decrypted is not None else None

