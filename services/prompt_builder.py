def build_summary_prompt(emails: list[dict]) -> str:
    lines = [
        "You are an email digest assistant. Summarize each email below.",
        "Rules:",
        "- First line: subject only (no prefix, no label)",
        "- Then 1-2 bullet points (•), each under 15 words",
        "- PRIORITY ORDER: action items > deadlines > urgent issues > general info",
        "- If the email has explicit action items, always include them",
        "- Skip background context and status info unless nothing more urgent exists",
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
