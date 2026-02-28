from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="Jeeyars Appointment System")

# ── Data file for storing bookings ──
BOOKINGS_FILE = "bookings.json"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return []

def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── Models ──
class BookingRequest(BaseModel):
    name: str
    phone: str
    business: str
    goal: str = ""
    date: str       # e.g. "2024-12-25"
    time: str       # e.g. "8:00 PM"

# ── Serve frontend ──
@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

# ── Book Appointment ──
@app.post("/book")
async def book_appointment(booking: BookingRequest):
    bookings = load_bookings()

    # Check if slot is already taken
    for b in bookings:
        if b["date"] == booking.date and b["time"] == booking.time:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": f"Yeh slot ({booking.time} on {booking.date}) pehle se book hai. Koi aur time choose karein."
                }
            )

    # Save booking
    new_booking = {
        "id": len(bookings) + 1,
        "name": booking.name,
        "phone": booking.phone,
        "business": booking.business,
        "goal": booking.goal,
        "date": booking.date,
        "time": booking.time,
        "booked_at": datetime.now().isoformat(),
        "status": "confirmed"
    }
    bookings.append(new_booking)
    save_bookings(bookings)

    print(f"✅ New Booking: {booking.name} | {booking.date} {booking.time} | {booking.phone}")

    return JSONResponse(content={
        "success": True,
        "message": "Appointment confirmed!",
        "booking_id": new_booking["id"]
    })

# ── Get all bookings (admin) ──
@app.get("/admin/bookings")
async def get_bookings(secret: str = ""):
    if secret != "jeeyars2024":
        raise HTTPException(status_code=403, detail="Access denied")
    bookings = load_bookings()
    return {"total": len(bookings), "bookings": bookings}

# ── Get booked slots for a date ──
@app.get("/slots/{date}")
async def get_booked_slots(date: str):
    bookings = load_bookings()
    booked = [b["time"] for b in bookings if b["date"] == date]
    return {"date": date, "booked_slots": booked}

# ── Health check ──
@app.get("/health")
async def health():
    return {"status": "ok", "service": "Jeeyars Appointments"}


# ── Run ──
if __name__ == "__main__":
    import uvicorn
    print("🚀 Jeeyars Appointment Server starting...")
    print("📌 Visit: http://localhost:8000")
    print("📋 Admin: http://localhost:8000/admin/bookings?secret=jeeyars2024")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)