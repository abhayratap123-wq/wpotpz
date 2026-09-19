import random
import hashlib
import time
from typing import Optional

# In-memory store (production me Redis/MongoDB use karo)
otp_store = {}

def generate_otp(phone: str) -> str:
    """6-digit OTP generate karo"""
    otp = str(random.randint(100000, 999999))
    hashed = hashlib.sha256(otp.encode()).hexdigest()
    otp_store[phone] = {
        "hash": hashed,
        "expires": time.time() + 300,  # 5 minute
        "attempts": 0
    }
    return otp

def verify_otp(phone: str, user_input: str) -> bool:
    """OTP verify karo"""
    data = otp_store.get(phone)
    if not data:
        return False
    if time.time() > data["expires"]:
        del otp_store[phone]
        return False
    if data["attempts"] >= 5:
        del otp_store[phone]
        return False
    data["attempts"] += 1
    hashed = hashlib.sha256(user_input.encode()).hexdigest()
    if hashed == data["hash"]:
        del otp_store[phone]
        return True
    return False
