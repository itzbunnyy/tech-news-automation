import os
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── CONFIG ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
EMAIL_ADDRESS = "jabr.e.hijr@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SAVE_FOLDER   = r"D:\automation"
# ────────────────────────────────────────────────────────────────────────────


def create_folder():
    """Create D:\\automation if it doesn't exist."""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
        print(f"[+] Folder created: {SAVE_FOLDER}")
    else:
        print(f"[✓] Folder already exists: {SAVE_FOLDER}")


def fetch_news():
    """Fetch top 10 stories from Hacker News."""
    print("[*] Fetching tech news from Hacker News...")
    top_ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    ).json()[:10]

    articles = []
    for story_id in top_ids:
        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()
        title = story.get("title", "No Title")
        url   = story.get("url", "No URL")
        articles.append(f"- {title} ({url})")

    print(f"[✓] Fetched {len(articles)} articles.")
    return "\n".join(articles)


def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
"model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
    )
    print("Groq raw response:", response.json())  # <-- debug line
    return response.json()["choices"][0]["message"]["content"].strip()

def summarize_news(articles_text):
    print("[*] Summarizing with Groq AI...")
    prompt = (
        "Here are today's top tech news headlines with links:\n\n"
        f"{articles_text}\n\n"
        "Summarize these into exactly 5 clear, concise bullet points. "
        "At the end of each bullet point, include the source link in this format: (Link: URL). "
        "Use simple language."
    )
    summary = ask_groq(prompt)
    print("[✓] Summary generated.")
    return summary


def generate_subject(summary):
    """Use Groq to generate a catchy email subject line."""
    print("[*] Generating subject line...")
    prompt = (
        "Based on this tech news summary:\n\n"
        f"{summary}\n\n"
        "Write ONE short, catchy email subject line (max 10 words). "
        "No quotes, just the subject line."
    )
    subject = ask_groq(prompt)
    print(f"[✓] Subject: {subject}")
    return subject


def save_to_file(subject, summary):
    """Save the summary to a .txt file inside D:\\automation."""
    date_str  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename  = os.path.join(SAVE_FOLDER, f"tech_news_{date_str}.txt")

    content = (
        f"Date    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Subject : {subject}\n"
        f"{'─' * 50}\n\n"
        f"{summary}\n"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[✓] Saved to: {filename}")
    return filename

def send_email(subject, summary):
    """Send the summary email via Gmail SMTP."""
    print("[*] Sending email...")
    msg = MIMEMultipart()
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = EMAIL_ADDRESS
    msg["Subject"] = subject
 
    body = f"Hi,\n\nHere's your Daily Tech News Summary:\n\n{summary}\n\nPowered by Groq AI + LLaMA 3"
    msg.attach(MIMEText(body, "plain"))
 
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
 
    print("[✓] Email sent successfully!")


def main():
    print("\n===== Tech News Summarizer =====\n")
    create_folder()
    articles  = fetch_news()
    summary   = summarize_news(articles)
    subject   = generate_subject(summary)
    send_email(subject, summary)
    print("\n===== Done! =====\n")


if __name__ == "__main__":
    main()
