import streamlit as st
import pandas as pd
import time
import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Workforce MailSync Pro", layout="wide")

# ==========================================
# NEW CYBER-NEON DESIGN (NO SQUARES)
# ==========================================
st.markdown(
    """
    <style>
    .stApp { background-color: #030405; color: #e2e8f0; font-family: 'Outfit', sans-serif; }
    
    /* Neon Circular Metric Blobs */
    .metric-blob {
        background: linear-gradient(145deg, #1e1b4b, #0f172a);
        border: 2px solid #6366f1;
        border-radius: 50% 20% / 10% 40%;
        padding: 40px;
        text-align: center;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.3);
        transition: 0.5s;
    }
    .metric-blob:hover { transform: scale(1.05); border-color: #f472b6; }
    
    .blob-value { font-size: 32px; font-weight: 800; color: #ffffff; }
    .blob-label { font-size: 10px; color: #a5b4fc; text-transform: uppercase; letter-spacing: 2px; }

    /* Modern Glass Input & Buttons */
    .stButton>button {
        background: #6366f1 !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 10px 30px !important;
        font-weight: bold !important;
    }
    
    /* Feed Cards */
    .feed-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 8px solid #6366f1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# LOGIC: GMAIL LEAVE FETCHING
# ==========================================
def fetch_and_reply_leave_gmail(email_user, email_pass, target_inbox):
    processed_logs = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_user, email_pass)
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK': return []
        for num in messages[0].split():
            res, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, _ = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes): subject = subject.decode("utf-8", errors="ignore")
                    from_whom = msg.get("From")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                    
                    body_lower = body.lower()
                    
                    # Logic
                    sick_keys = ["sick", "fever", "ill", "unwell"]
                    personal_keys = ["personal", "chutti", "leave", "absent"]
                    
                    if any(w in body_lower for w in sick_keys) or any(w in body_lower for w in personal_keys):
                        # Send Reply
                        smtp = smtplib.SMTP('smtp.gmail.com', 587)
                        smtp.starttls()
                        smtp.login(email_user, email_pass)
                        msg_reply = MIMEMultipart()
                        msg_reply['From'] = email_user
                        msg_reply['To'] = from_whom
                        msg_reply['Subject'] = f"Re: {subject}"
                        msg_reply.attach(MIMEText("HR Automation: Received your request. Processing...", 'plain'))
                        smtp.sendmail(email_user, from_whom, msg_reply.as_string())
                        smtp.quit()
                        processed_logs.append({"title": subject, "from": from_whom, "action": "Replied"})
        mail.logout()
        return processed_logs
    except:
        return []

# ==========================================
# LAYOUT
# ==========================================
st.title("🌌 Workforce MailSync AI")

with st.sidebar:
    st.subheader("🔑 Connectivity")
    user = st.text_input("Gmail")
    pwd = st.text_input("App Password", type="password")
    if st.button("Connect System"):
        st.session_state.connected = True
        st.balloons()

# Dashboard Blobs (NO SQUARES)
col1, col2, col3 = st.columns(3)
with col1: st.markdown('<div class="metric-blob"><div class="blob-value">--</div><div class="blob-label">Scanned</div></div>', unsafe_allow_html=True)
with col2: st.markdown('<div class="metric-blob"><div class="blob-value" style="color:#f472b6;">--</div><div class="blob-label">Dispatched</div></div>', unsafe_allow_html=True)
with col3: st.markdown('<div class="metric-blob"><div class="blob-value">100%</div><div class="blob-label">Context</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

if st.button("RUN SMART SCANNER"):
    results = fetch_and_reply_leave_gmail(user, pwd, user)
    for r in results:
        st.markdown(f'<div class="feed-card"><b>{r["title"]}</b><br><small>{r["from"]}</small></div>', unsafe_allow_html=True)
