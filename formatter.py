from datetime import date, timedelta

def format_plan(raw_text: str, target_date: str = None) -> str:
    # Split by newlines or commas
    lines = []
    for line in raw_text.splitlines():
        for part in line.split(","):
            cleaned = part.strip()
            if cleaned:
                lines.append(cleaned)

    if not lines:
        return "⚠️ No plan recorded."

    # Use provided date or fall back to tomorrow
    if target_date:
        display_date = date.fromisoformat(target_date).strftime("%A, %B %d")
    else:
        display_date = (date.today() + timedelta(days=1)).strftime("%A, %B %d")

    formatted = f"📋 *Plan for {display_date}*\n\n"
    for i, item in enumerate(lines, start=1):
        formatted += f"{i}. {item}\n"

    return formatted.strip()