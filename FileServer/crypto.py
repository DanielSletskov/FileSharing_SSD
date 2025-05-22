import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

def derive_key(password: str, salt: bytes) -> bytes:
    # PBKDF2-HMAC-SHA256
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000, dklen=32)

def encrypt_file(data: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce + ct

def decrypt_file(encrypted: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce, ct = encrypted[:12], encrypted[12:]
    return aesgcm.decrypt(nonce, ct, None)
