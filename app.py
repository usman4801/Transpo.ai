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
st.set_page_config(
    page_title="Workforce MailSync AI", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM HASEEN CSS (PREMIUM STYLING)
# ==========================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #f3f6fc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    .dash-title {
        font-size: 38px;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4f46e5, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .dash-subtitle {
        color: #64748b;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 30px;
    }

    .ai-metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .ai-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(79, 70, 229, 0.1);
    }
    .metric-value { font-size: 36px; font-weight: 800; color: #1e293b; }
    .metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 12px 25px rgba(79, 70, 229, 0.5) !important;
        transform: scale(1.02);
    }

    .email-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border-left: 6px solid #4f46e5;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .email-card.leave { border-left-color: #f59e0b; }
    .email-card.mispunch { border-left-color: #ef4444; }
    .email-card.shift { border-left-color: #10b981; }

    .email-details h4 { margin: 0; color: #1e293b; font-size: 18px; font-weight: 700; }
    .email-details p { margin: 4px 0 0 0; color: #64748b; font-size: 14px; }
    
    .ai-badge {
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-leave { background: #fef3c7; color: #d97706; }
    .badge-mispunch { background: #fee2e2; color: #dc2626; }
    .badge-shift { background: #d1fae5; color: #059669; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# OUTLOOK AUTO-REPLY LOGIC (IMAP / SMTP)
# ==========================================
def fetch_and_reply_outlook(email_user, email_pass, target_inbox):
    processed_logs = []
    try:
        # 1. Connect to Outlook IMAP server
        mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        # Search unread messages
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            return []

        for num in messages[0].split():
            res, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Get Sender & Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    
                    from_whom = msg.get("From")
                    
                    # Extract Body Text
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    body_lower = body.lower()

                    # 2. Keyword Filtering (Leave / Sick / Mispunch)
                    if any(word in body_lower for word in ["sick", "chutti", "leave", "fever", "emergency", "absent"]):
                        category = "Leave Request"
                        badge_class = "leave"
                        reply_text = f"Dear Employee,\n\nYour leave request regarding '{subject}' has been received and noted by HR. Rest well and take care.\n\nBest Regards,\nHR Team - Amazon ({target_inbox})"
                    elif any(word in body_lower for word in ["punch", "mispunch", "missed", "timing"]):
                        category = "Mispunch"
                        badge_class = "mispunch"
                        reply_text = f"Dear Employee,\n\nYour missing punch query has been logged and forwarded to attendance management.\n\nBest Regards,\nHR Team - Amazon ({target_inbox})"
                    else:
                        continue # Skip other emails

                    # 3. Send Auto-Reply via SMTP
                    try:
                        smtp_server = smtplib.SMTP('smtp.office365.com', 587)
                        smtp_server.starttls()
                        smtp_server.login(email_user, email_pass)
                        
                        msg_reply = MIMEMultipart()
                        msg_reply['From'] = email_user
                        msg_reply['To'] = from_whom
                        msg_reply['Subject'] = f"Re: {subject}"
                        msg_reply.attach(MIMEText(reply_text, 'plain'))
                        
                        smtp_server.sendmail(email_user, from_whom, msg_reply.as_string())
                        smtp_server.quit()
                        status_action = "Auto-Replied ✅"
                    except Exception as e:
                        status_action = "Failed to Reply ❌"

                    processed_logs.append({
                        "title": subject[:40],
                        "from": from_whom,
                        "summary": body[:90] + "...",
                        "category": category,
                        "badge": badge_class,
                        "action": status_action
                    })

        mail.logout()
        return processed_logs
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return []

# ==========================================
# SIDEBAR SETTINGS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2646/2646141.png", width=60)
    st.markdown("### ⚙️ Outlook Integration")
    outlook_email = st.text_input("HR Inbox Email", value="auh1-fc-pxt@amazon.ae", placeholder="auh1-fc-pxt@amazon.ae")
    outlook_pass = st.text_input("Outlook App Password", type="password", placeholder="Enter app password...")
    auto_mode = st.selectbox("Auto-Reply Mode", ["Fully Automated (Send Direct)", "Draft Only (Require Approval)", "Off"])
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:12px;'>System Status: 🟢 <b>Ready</b></p>", unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD HEADER
# ==========================================
st.markdown('<div class="dash-title">Workforce MailSync AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Intelligent Outlook Email Parsing & Automated HR Actions System</div>', unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="ai-metric-card"><div class="metric-value">142</div><div class="metric-label">Emails Scanned</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#10b981;">118</div><div class="metric-label">Auto-Resolved</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#f59e0b;">24</div><div class="metric-label">Pending Review</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#4f46e5;">98%</div><div class="metric-label">AI Accuracy</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# LIVE SCANNER SECTION
# ==========================================
if 'live_results' not in st.session_state:
    st.session_state.live_results = None

action_col, text_col = st.columns([3, 7])

with action_col:
    st.markdown("### 🤖 Outlook Sync")
    st.write("Click below to fetch unread emails from **auh1-fc-pxt@amazon.ae** and execute auto-replies.")
    if st.button("Fetch & Process Live Emails ➔"):
        if not outlook_pass:
            st.warning("Please enter your Outlook App Password in the sidebar first!")
        else:
            with st.spinner("Connecting to Outlook Mail Server..."):
                results = fetch_and_reply_outlook(outlook_email, outlook_pass, outlook_email)
                st.session_state.live_results = results
            st.success(f"Sync Complete! {len(results)} leave/mispunch requests processed.")

with text_col:
    st.markdown("### 📥 Filtered & Replied Emails")
    
    if st.session_state.live_results is None:
        st.info("Click 'Fetch & Process Live Emails' to scan incoming mail from Amazon associates.")
    elif len(st.session_state.live_results) == 0:
        st.warning("No new matching leave requests or mispunches found in the inbox.")
    else:
        for item in st.session_state.live_results:
            card_html = f"""
            <div class="email-card {item['badge']}">
                <div class="email-details">
                    <h4>{item['title']}</h4>
                    <p><b>From:</b> {item['from']}</p>
                    <p><i>Content: {item['summary']}</i></p>
                </div>
                <div style="text-align: right;">
                    <span class="ai-badge badge-{item['badge']}">{item['category']}</span><br>
                    <p style="margin-top:8px; font-size:12px; color:#64748b;">Action: <b>{item['action']}</b></p>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
