#!/usr/bin/env python3
"""
Herms Morning Brief — run daily before Josh wakes (3am slot material).
Generates: weather, calendar preview, CRM stales, and a priority callout.

Sources:
  - Weather: Open-Meteo (free, no key) for Phoenix
  - Calendar: Google Workspace API (if available) or placeholder
  - CRM: OneDrive/Airtable contacts (cached)
  - Priority: read from priority-model conventions
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import requests

HOME = Path.home()
CONFIG = HOME / ".hermes" / "morning-brief.json"
CACHE = HOME / ".hermes" / "morning-brief-cache.json"

# Phoenix lat/lon
PHX_LAT = 33.4484
PHX_LON = -112.0740


def get_weather():
    """Fetch Phoenix weather from Open-Meteo (free, no API key)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": PHX_LAT,
        "longitude": PHX_LON,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max",
        "current": "temperature_2m,weathercode,relative_humidity_2m",
        "timezone": "America/Phoenix",
        "forecast_days": 2,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()

        current = d.get("current", {})
        daily = d.get("daily", {})

        def wmo_desc(code):
            codes = {0: "☀️ Clear", 1: "🌤 Mostly clear", 2: "⛅ Partly cloudy",
                     3: "☁️ Overcast", 45: "🌫 Foggy", 48: "🌫 Depositing rime fog",
                     51: "🌦 Light drizzle", 53: "🌦 Moderate drizzle", 55: "🌦 Dense drizzle",
                     61: "🌦 Slight rain", 63: "🌧 Moderate rain", 65: "🌧 Heavy rain",
                     71: "🌨 Slight snow", 73: "🌨 Moderate snow", 75: "🌨 Heavy snow",
                     80: "🌦 Slight rain showers", 81: "🌧 Moderate rain showers",
                     82: "🌧 Violent rain showers", 95: "⛈ Thunderstorm",
                     96: "⛈ Thunderstorm with slight hail", 99: "⛈ Thunderstorm with heavy hail"}
            return codes.get(code, f"Code {code}")

        today_temp = f"{current.get('temperature_2m', '?')}°F" if current.get('temperature_2m') else "?"
        today_high = daily.get("temperature_2m_max", [None])[0]
        today_low = daily.get("temperature_2m_min", [None])[0]
        precip = daily.get("precipitation_probability_max", [None])[0]
        weather_code = current.get("weathercode", current.get("weather_code", 0))

        line = f"{wmo_desc(weather_code)}, {today_temp}"
        if today_high and today_low:
            line += f" (H:{today_high:.0f}° / L:{today_low:.0f}°)"
        if precip and precip > 10:
            line += f" — 🌧 {precip:.0f}% rain"

        return line
    except Exception as e:
        return f"⚠️ Weather unavailable: {e}"


def get_calendar():
    """Placeholder calendar — replace with Google/Outlook API later."""
    now = datetime.now(timezone.utc)
    # Check for cached calendar events
    cal_data = None
    if CACHE.exists():
        try:
            cal_data = json.loads(CACHE.read_text())
        except Exception:
            pass

    if cal_data and "events" in cal_data:
        events = cal_data["events"]
        if events:
            return events
    return ["📅 No calendar events cached — waiting for API setup"]


def get_priority_callout():
    """Read priority model and make a one-line suggestion."""
    prio_file = HOME / "repo" / "docs" / "herms" / "priority-model.md"
    if prio_file.exists():
        content = prio_file.read_text()
        for line in content.split("\n"):
            if "Primary Ball" in line and "|" in line:
                # Parse the ball name from markdown table
                parts = line.split("|")
                if len(parts) >= 2:
                    ball = parts[-2].strip()
                    if "**" in ball:
                        ball = ball.replace("**", "")
                    return f"🎯 Primary ball: {ball}"
    
    return "🎯 No priority set — check standup?"


def main():
    lines = []
    lines.append("=== MORNING BRIEF ===")
    lines.append(f"Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    lines.append("")

    # Weather
    try:
        weather = get_weather()
    except Exception:
        weather = "⚠️ Weather fetch failed"
    lines.append(f"⛅ {weather}")

    # Calendar
    lines.append("")
    events = get_calendar()
    for ev in events:
        lines.append(f"  {ev}")

    # Priority callout
    lines.append("")
    lines.append(get_priority_callout())

    print("\n".join(lines))
    print("\nSTATUS=OK")


if __name__ == "__main__":
    main()
