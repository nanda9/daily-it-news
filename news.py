import os
import feedparser
import yfinance as yf
from openai import OpenAI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -------------------------
# ENV VARIABLES
# -------------------------
EMAIL = os.environ["EMAIL"]
APP_PASSWORD = os.environ["APP_PASSWORD"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------
# FETCH RSS NEWS
# -------------------------
feeds = open("feeds.txt").read().splitlines()

headlines = []

for feed in feeds:
    data = feedparser.parse(feed)

    for entry in data.entries[:3]:
        headlines.append(f"{entry.title}")

raw_headlines = "\n".join(headlines[:15])

# -------------------------
# AI SUMMARY
# -------------------------
prompt = f"""
Summarize the following tech news into 8–10 bullet points.
Focus on AI, cloud, cybersecurity, DevOps.

News:
{raw_headlines}
"""

response = client.responses.create(
    model="gpt-5-mini",
    input=prompt
)

summary_text = response.output_text

# Convert bullets into HTML
summary_html = "<ul>"
for line in summary_text.split("\n"):
    if line.strip():
        summary_html += f"<li>{line}</li>"
summary_html += "</ul>"

# -------------------------
# STOCK DATA
# -------------------------
tickers = ["NVDA", "MSFT", "GOOGL", "AMZN", "META"]

stocks_html = "<ul>"

for t in tickers:
    stock = yf.Ticker(t)
    price = stock.fast_info.get("lastPrice", "N/A")
    stocks_html += f"<li>{t}: ${price}</li>"

stocks_html += "</ul>"

# -------------------------
# AWS + K8s SECTION (simple RSS reuse)
# -------------------------
aws_news = []
k8s_news = []

for feed in feeds:
    data = feedparser.parse(feed)

    for entry in data.entries[:2]:
        title = entry.title

        if "aws" in feed:
            aws_news.append(f"<li>{title}</li>")

        if "kubernetes" in feed:
            k8s_news.append(f"<li>{title}</li>")

aws_html = "<ul>" + "".join(aws_news) + "</ul>"
k8s_html = "<ul>" + "".join(k8s_news) + "</ul>"

# -------------------------
# DEVOPS TIP
# -------------------------
tip = "Use GitHub Actions to schedule daily automation workflows."

# -------------------------
# HTML EMAIL
# -------------------------
html = f"""
<html>
<body style="font-family: Arial">

<h1>🚀 Daily IT News Digest</h1>

<h2>🧠 AI Summary</h2>
{summary_html}

<h2>📈 Stocks</h2>
{stocks_html}

<h2>☁️ AWS Updates</h2>
{aws_html}

<h2>⚙️ Kubernetes</h2>
{k8s_html}

<h2>🎓 DevOps Tip</h2>
<p>{tip}</p>

</body>
</html>
"""

# -------------------------
# SEND EMAIL
# -------------------------
msg = MIMEMultipart("alternative")
msg["Subject"] = "Daily IT News Digest"
msg["From"] = EMAIL
msg["To"] = EMAIL

msg.attach(MIMEText(html, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL, APP_PASSWORD)
    smtp.send_message(msg)

print("Email sent successfully")