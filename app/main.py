from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
import os
from astra import Client
from otp_logic import generate_otp, verify_otp

app = FastAPI(title="WhatsApp OTP System")
templates = Jinja2Templates(directory="templates")

# Global Astra client (session persist hoga)
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")  # e.g. 919876543210
SESSION_ID = "otp_bot"

client = Client(session_id=SESSION_ID, phone=WHATSAPP_PHONE)

class OTPRequest(BaseModel):
    phone: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/send-otp")
async def send_otp(data: OTPRequest):
    """OTP generate karo aur WhatsApp pe bhejo"""
    phone = data.phone.strip()
    if not phone or len(phone) < 10:
        return {"success": False, "error": "Invalid number"}

    otp = generate_otp(phone)
    message = f"🔐 Aapka OTP: {otp}\n\n5 minute me expire hoga. Kisi ke saath share na karein."

    try:
        await client.send_message(phone, message)
        return {"success": True, "message": "OTP bhej diya"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/verify-otp")
async def verify(data: OTPRequest, otp: str = Form(...)):
    """OTP verify karo"""
    ok = verify_otp(data.phone, otp)
    return {"success": ok}

@app.get("/api/pair")
async def pair():
    """Phone pairing code generate karo (first time setup)"""
    try:
        code = await client.request_pairing_code(WHATSAPP_PHONE)
        return {"success": True, "pairing_code": code}
    except Exception as e:
        return {"success": False, "error": str(e)}
