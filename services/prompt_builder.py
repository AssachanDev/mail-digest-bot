def build_summary_prompt(emails: list[dict]) -> str:
    lines = [
        "You are an email digest assistant. Summarize each email below as exactly 1-2 bullet points.",
        "Rules:",
        "- Start each email with the subject in bold: **Subject**",
        "- Follow with 1-2 bullet points (•) covering the key info or action required",
        "- Be concise. No greetings, no sign-offs, no filler text",
        "- Do NOT ask follow-up questions or offer further help",
        "- Respond in English only",
        "- Output nothing except the formatted summaries",
        "---",
    ]
    for i, e in enumerate(emails, 1):
        lines.append(f"\n[EMAIL {i}]")
        lines.append(f"From: {e['from']}")
        lines.append(f"Subject: {e['subject']}")
        lines.append(f"Snippet: \"{e['snippet']}\"")
    lines.append("\n---\nSummary:")
    return "\n".join(lines)
