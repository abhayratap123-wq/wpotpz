import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from astra import Client
from otp_logic import generate_otp, verify_otp

app = FastAPI(title="WhatsApp OTP System")
templates = Jinja2Templates(directory="templates")

# Global variables
client = None
SESSION_ID = "otp_bot_mobile"
is_logged_in = False

class ConnectRequest(BaseModel):
    phone: str

class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/connect")
async def connect_whatsapp(data: ConnectRequest):
    """WhatsApp ko link karne ke liye start karega"""
    global client, is_logged_in
    phone = data.phone.strip().replace("+", "").replace(" ", "")
    
    try:
        if client is None:
            client = Client(session_id=SESSION_ID, phone=phone)
            # Background me start karega taaki request timeout na ho
            asyncio.create_task(client.start())
        
        return {
            "success": True, 
            "message": "Connecting process start ho gaya! Terminal me code dekhein ya phone par notification check karein."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/send-otp")
async def send_otp(data: SendOTPRequest):
    """OTP send karne ki API"""
    global client
    phone = data.phone.strip().replace("+", "").replace(" ", "")
    
    if not client or not client.is_connected:
        return {"success": False, "error": "WhatsApp connected nahi hai. Pehle connect karein."}

    otp = generate_otp(phone)
    message = f"🔐 Aapka OTP hai: {otp}\n\nYeh OTP agle 5 minute tak valid hai."

    try:
        await client.send_message(f"{phone}@c.us", message)
        return {"success": True, "message": f"OTP successfully bhej diya: {otp}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/verify-otp")
async def verify(data: VerifyOTPRequest):
    """OTP verify karne ki API"""
    ok = verify_otp(data.phone.strip(), data.otp.strip())
    return {"success": ok}

@app.get("/api/status")
async def status():
    """Check karega bot connected hai ya nahi"""
    global client
    connected = False
    if client and client.is_connected:
        connected = True
    return {"connected": connected}
