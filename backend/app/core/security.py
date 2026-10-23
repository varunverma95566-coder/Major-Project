import hmac
import hashlib
import os
import json
import base64
import time
from typing import Optional, Dict, Any
from app.core.config import settings

def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, key_hex = hashed_password.split("$")
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(key.hex(), key_hex)
    except Exception:
        return False

def create_access_token(data: dict, expires_in_minutes: Optional[int] = None) -> str:
    payload = data.copy()
    expire_time = int(time.time()) + (expires_in_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    payload["exp"] = expire_time
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_data = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signature_data, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify signature
        signature_data = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), signature_data, hashlib.sha256).digest()
        
        # Re-pad signature b64 for decoding
        rem = len(sig_b64) % 4
        sig_padded = sig_b64 + ("=" * (4 - rem) if rem else "")
        provided_sig = base64.urlsafe_b64decode(sig_padded)
        
        if not hmac.compare_digest(expected_sig, provided_sig):
            return None
            
        rem_p = len(payload_b64) % 4
        payload_padded = payload_b64 + ("=" * (4 - rem_p) if rem_p else "")
        payload = json.loads(base64.urlsafe_b64decode(payload_padded).decode())
        
        if payload.get("exp", 0) < int(time.time()):
            return None  # Expired
            
        return payload
    except Exception:
        return None
