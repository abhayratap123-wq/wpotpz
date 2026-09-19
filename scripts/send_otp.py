"""
Sends a one-off WhatsApp test message using Astra Engine.
"""
import asyncio
import os
import sys

from astra import Client

# 🔥 MAIN FIX: Session ID change kar diya taaki purani corrupt cache use na ho
SESSION_ID = "otp_bot_fresh_v1"

async def main() -> None:
    whatsapp_phone = os.getenv("WHATSAPP_PHONE")
    otp_phone = os.getenv("OTP_PHONE")

    if not whatsapp_phone or not otp_phone:
        sys.exit(
            "❌ Missing Secrets: WHATSAPP_PHONE aur OTP_PHONE GitHub repo secrets me set nahi hain."
        )

    # Client initialize karna (Phone number dene se ye Pairing Code generate karega)
    client = Client(session_id=SESSION_ID, phone=whatsapp_phone)

    print("=====================================================")
    print("⏳ Astra Client NAYE SESSION ke sath Start ho raha hai...")
    print("🚨 DHYAN DEIN:")
    print("   Niche logs me ek 8-character ka PAIRING CODE aayega.")
    print("   Apne phone me WhatsApp open karein -> Linked Devices -> Link a Device")
    print("   -> 'Link with phone number instead' par click karein aur wo code daalein.")
    print("=====================================================\n")

    try:
        # Astra start hoga (yahan pairing code print hoga)
        await client.start()
        
        # Message bhejna
        recipient_jid = f"{otp_phone}@c.us"
        print(f"📩 Sending message to {otp_phone}...")
        await client.send_message(recipient_jid, "✅ WhatsApp OTP Bot Setup Successful! (123456)")
        print("🎉 OTP successfully bhej diya gaya!")
        
    except Exception as e:
        print(f"\n❌ SCRIPT FAIL HO GAYI: {str(e)}")
        print("👉 Agar Timeout error aaya hai, toh aapne code nahi daala.")
        sys.exit(1)
    finally:
        # Client stop karein
        if client.is_connected:
            await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
