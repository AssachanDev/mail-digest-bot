def build_system_prompt() -> str:
    return (
        "You are an email digest assistant. "
        "For each email, output EXACTLY this format and nothing else:\n\n"
        "<Subject line>\n"
        "• <action item or urgent issue, max 15 words>\n"
        "• <second point only if needed, max 15 words>\n\n"
        "Rules:\n"
        "- Prioritize: action items > deadlines > urgent issues > general info\n"
        "- If 'action required' or a deadline exists, it MUST appear in the bullets\n"
        "- Never exceed 2 bullet points per email\n"
        "- No intro, no closing, no commentary, no follow-up questions\n"
        "- English only"
    )


def build_user_prompt(emails: list[dict]) -> str:
    lines = []
    for i, e in enumerate(emails, 1):
        lines.append(f"[EMAIL {i}]")
        lines.append(f"From: {e['from']}")
        lines.append(f"Subject: {e['subject']}")
        lines.append(f"Body: \"{e['snippet']}\"")
        lines.append("")
    return "\n".join(lines)
