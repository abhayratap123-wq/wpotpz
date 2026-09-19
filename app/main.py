from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from astra import Client
from otp_logic import generate_otp, verify_otp

# Global Astra client (session persist hoga)
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")  # e.g. 919876543210
SESSION_ID = "otp_bot"

if not WHATSAPP_PHONE:
    raise RuntimeError(
        "Missing WHATSAPP_PHONE environment variable. Set it to your "
        "WhatsApp number — digits only, with country code, e.g. "
        "919876543210 — before starting this app."
    )

client = Client(session_id=SESSION_ID, phone=WHATSAPP_PHONE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pehli baar (no cached session) yahan ek 8-character pairing code
    # terminal me print hoga — WhatsApp > Linked Devices > Link a Device >
    # "Link with phone number instead" me daal dena.
    await client.start()
    yield
    await client.stop()


app = FastAPI(title="WhatsApp OTP System", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


class OTPSendRequest(BaseModel):
    phone: str


class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/send-otp")
async def send_otp(data: OTPSendRequest):
    """OTP generate karo aur WhatsApp pe bhejo"""
    phone = data.phone.strip()
    if not phone or len(phone) < 10:
        return {"success": False, "error": "Invalid number"}

    otp = generate_otp(phone)
    message = f"🔐 Aapka OTP: {otp}\n\n5 minute me expire hoga. Kisi ke saath share na karein."

    try:
        await client.send_message(f"{phone}@c.us", message)
        return {"success": True, "message": "OTP bhej diya"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/verify-otp")
async def verify(data: OTPVerifyRequest):
    """OTP verify karo"""
    ok = verify_otp(data.phone, data.otp)
    return {"success": ok}


@app.get("/api/status")
async def status():
    """Client abhi WhatsApp se connected hai ya nahi"""
    return {"connected": client.is_connected}
