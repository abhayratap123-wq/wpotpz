"""
Sends a one-off WhatsApp test message using Astra Engine.
Called by .github/workflows/otp-sender.yml

Required environment variables (set as GitHub repo secrets — Settings >
Secrets and variables > Actions > New repository secret):

  WHATSAPP_PHONE   The WhatsApp number that RUNS the bot. International
                   format, digits only, no '+', no spaces.
                   Example: 919876543210

  OTP_PHONE        The number that should RECEIVE the test message.
                   Same format as above.
"""
import asyncio
import os
import sys

from astra import Client

SESSION_ID = "otp_bot"


async def main() -> None:
    whatsapp_phone = os.getenv("WHATSAPP_PHONE")
    otp_phone = os.getenv("OTP_PHONE")

    if not whatsapp_phone:
        sys.exit(
            "Missing WHATSAPP_PHONE secret. Add it under repo Settings > "
            "Secrets and variables > Actions, as digits only with country "
            "code (e.g. 919876543210) — no '+', no spaces."
        )
    if not otp_phone:
        sys.exit(
            "Missing OTP_PHONE secret. Add it the same way as "
            "WHATSAPP_PHONE — this is the number that should receive the "
            "test message."
        )

    client = Client(session_id=SESSION_ID, phone=whatsapp_phone)

    # On the very first run there is no cached session, so this call
    # prints an 8-character pairing code right here in the Actions log
    # and waits for you to enter it on your phone.
    await client.start()
    try:
        recipient_jid = f"{otp_phone}@c.us"
        await client.send_message(recipient_jid, "Test OTP: 123456")
        print("OTP sent!")
    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
