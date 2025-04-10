import requests
from dotenv import load_dotenv
import os

load_dotenv()

def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius."""
    return kelvin - 273.15


def run(args: dict) -> str:
    location = args.get("location", "unknown")
    res = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={os.getenv('OPENWEATHERMAP')}"
    )
    return f"The weather in {location} is something and {kelvin_to_celsius(res["main"]["temp"])}°C."
