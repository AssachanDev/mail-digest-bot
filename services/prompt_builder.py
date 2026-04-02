def build_summary_prompt(emails: list[dict]) -> str:
    lines = [
        "You are an email digest assistant. Summarize each email below.",
        "Rules:",
        "- First line of each email: the subject only, no prefix",
        "- Follow with exactly 1-2 bullet points (•)",
        "- Each bullet point must be under 15 words",
        "- Total output must be under 30 words per email",
        "- No greetings, no sign-offs, no filler, no follow-up questions",
        "- Respond in English only",
        "- Output nothing except the summaries",
        "---",
    ]
    for i, e in enumerate(emails, 1):
        lines.append(f"\n[EMAIL {i}]")
        lines.append(f"From: {e['from']}")
        lines.append(f"Subject: {e['subject']}")
        lines.append(f"Snippet: \"{e['snippet']}\"")
    lines.append("\n---\nSummary:")
    return "\n".join(lines)
