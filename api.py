from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from phish import analyse  # your existing detection code, unchanged

app = FastAPI(title="Phishing Message Checker API")

# Add your deployed frontend URL here once you have one
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Moved over from app.py so there is one source of truth
EXAMPLES = {
    "Parcel delivery text (scam)": (
        "EVRI: PARCEL COULD NOT BE DELIVERED ON 02 MARCH 2026 at 11:57 AM due to no one "
        "being home. Reschedule your missed delivery now at: https://evr.i275103uk.com"
    ),
    "Job offer text (scam)": (
        "Hello! This is TikTok HR. We'd like to invite you to be our online employee. "
        "With just a mobile phone and working in your spare time, you can earn 300-800 "
        "daily. Leave a message now and get a 8 bonus. Please contact us for details. "
        "WA: http://wa.me/44XXXXXXXXXX"
    ),
    "Email with sender details (scam)": (
        'From: "PayPal Support" <help@paypa1-secure.com>\n'
        "Reply-To: attacker@mailbox.ru\n"
        "Subject: Account suspended\n"
        "\n"
        "Dear customer, your account will be closed within 24 hours.\n"
        "Verify your account here: https://paypa1-secure.com/login"
    ),
    "Delivery text (genuine)": (
        "Evri: Your parcel from ASOS will be delivered tomorrow between 10:00 and 14:00. "
        "Track it at https://www.evri.com/track/ab12cd34"
    ),
    "Bank card alert (genuine)": (
        "Barclays: A payment of GBP 34.20 to TESCO STORES was made on your card ending "
        "1234. If this wasn't you, call the number on the back of your card."
    ),
}


class CheckRequest(BaseModel):
    message: str = Field(max_length=10000)


@app.get("/api/examples")
def examples():
    return EXAMPLES


@app.post("/api/check")
def check(req: CheckRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Please paste a message first.")
    try:
        return analyse(req.message)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while checking that message.",
        )
