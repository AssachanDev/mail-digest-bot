def build_summary_prompt(emails: list[dict]) -> str:
    lines = [
        "Below are unread emails. Summarize each in 1-2 bullet points.",
        "Be concise. Highlight key action items or important info.",
        "Respond in English.",
        "---",
    ]
    for i, e in enumerate(emails, 1):
        lines.append(f"\n[EMAIL {i}]")
        lines.append(f"From: {e['from']}")
        lines.append(f"Subject: {e['subject']}")
        lines.append(f"Snippet: \"{e['snippet']}\"")
    lines.append("\n---\nSummary:")
    return "\n".join(lines)
