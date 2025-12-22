from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from pysolar.solar import get_azimuth
import requests
import math

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

# ---------- PLACE SEARCH (CITY / STATE / COUNTRY ONLY) ----------
def geocode(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    headers = {"User-Agent": "shadeseat-app"}
    r = requests.get(url, params=params, headers=headers).json()

    if not r:
        return None

    addr = r[0].get("address", {})
    allowed = {"city", "town", "state", "country"}

    if not any(k in addr for k in allowed):
        return None

    return float(r[0]["lat"]), float(r[0]["lon"])

# ---------- BEARING ----------
def calc_bearing(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlon = lon2 - lon1

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

# ---------- MAIN API ----------
@app.route("/shade-seat")
def shade_seat():
    try:
        start = request.args.get("start")
        end = request.args.get("end")
        date = request.args.get("date")
        time = request.args.get("time")

        s = geocode(start)
        e = geocode(end)

        if not s or not e:
            return jsonify({"status": "error", "message": "Place not found"})

        dt = datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=timezone.utc)

        sun_azimuth = get_azimuth(s[0], s[1], dt)
        travel_bearing = calc_bearing(s, e)

        diff = (sun_azimuth - travel_bearing + 360) % 360

        if diff < 180:
            sun_side = "LEFT"
            seat = "RIGHT"
        else:
            sun_side = "RIGHT"
            seat = "LEFT"

        distance = math.dist(s, e) * 111  # km approx

        return jsonify({
            "status": "success",
            "start": s,
            "end": e,
            "sun_side": sun_side,
            "seat": seat,
            "distance": round(distance, 2)
        })

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)})

if __name__ == "__main__":
    app.run(debug=True)

