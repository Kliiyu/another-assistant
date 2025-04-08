def run(args: dict) -> str:
    location = args.get("location", "unknown")
    return f"The weather in {location} is sunny and 24°C."
