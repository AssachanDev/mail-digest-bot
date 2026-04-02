def build_summary_prompt(emails: list[dict]) -> str:
    lines = [
        "You are an email digest assistant.",
        "For each email below, output EXACTLY this format and nothing else:",
        "",
        "<Subject line>",
        "• <action item or urgent issue, max 15 words>",
        "• <second point only if needed, max 15 words>",
        "",
        "Rules:",
        "- Prioritize: action items > deadlines > urgent issues > general info",
        "- If 'action required' or a deadline exists, it MUST appear in the bullets",
        "- Never exceed 2 bullet points per email",
        "- No intro, no closing, no commentary, no follow-up questions",
        "- English only",
        "---",
    ]
    for i, e in enumerate(emails, 1):
        lines.append(f"\n[EMAIL {i}]")
        lines.append(f"From: {e['from']}")
        lines.append(f"Subject: {e['subject']}")
        lines.append(f"Snippet: \"{e['snippet']}\"")
    lines.append("\n---\nSummary:")
    return "\n".join(lines)
