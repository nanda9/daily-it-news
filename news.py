import os
import feedparser
import smtplib
from email.mime.text import MIMEText

EMAIL = os.environ["EMAIL"]
APP_PASSWORD = os.environ["APP_PASSWORD"]

feeds = open("feeds.txt").read().splitlines()

news = []

for feed in feeds:
    data = feedparser.parse(feed)

    for entry in data.entries[:3]:
        news.append(
            f"- {entry.title}\n  {entry.link}\n"
        )

body = "\n".join(news[:20])

msg = MIMEText(body)
msg["Subject"] = "Daily IT News Digest"
msg["From"] = EMAIL
msg["To"] = EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL, APP_PASSWORD)
    smtp.send_message(msg)

print("Email sent")