from datetime import date

def format_plan(raw_text: str) -> str:
    # Split by newlines or commas
    lines = []
    for line in raw_text.splitlines():
        for part in line.split(","):
            cleaned = part.strip().capitalize()
            if cleaned:
                lines.append(cleaned)

    if not lines:
        return "⚠️ No plan recorded."

    tomorrow = date.today().strftime("%A, %B %d")

    formatted = f"📋 *Plan for {tomorrow}*\n\n"
    for i, item in enumerate(lines, start=1):
        formatted += f"{i}. {item}\n"

    return formatted.strip()

if __name__ == "__main__":
    test = "Wake up early\nExercise, Read 20 pages\nWork on project"
    print(format_plan(test))