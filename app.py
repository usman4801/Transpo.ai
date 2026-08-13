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
# MODERN PURPLE + WHITE + DEEP THEME
# ==========================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #090514 0%, #17102b 50%, #291b4e 100%);
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #ffffff;
    }
    
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
    }
    
    .dash-title {
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .dash-subtitle {
        color: #cbd5e1;
        font-size: 15px;
        font-weight: 400;
        margin-bottom: 35px;
    }

    .organic-pill-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(192, 132, 252, 0.25);
        border-radius: 20px; 
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .organic-pill-card:hover {
        transform: translateY(-4px);
        border-color: rgba(192, 132, 252, 0.6);
        box-shadow: 0 25px 50px rgba(147, 51, 234, 0.2);
    }
    .metric-value { font-size: 38px; font-weight: 900; color: #ffffff; text-shadow: 0 0 20px rgba(192, 132, 252, 0.5); }
    .metric-label { font-size: 11px; color: #cbd5e1; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px; margin-top: 6px; }

    .stButton>button {
        background: linear-gradient(135deg, #a855f7 0%, #7e22ce 100%) !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 20px !important;
        width: 100%;
        box-shadow: 0 10px 25px rgba(147, 51, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 15px 35px rgba(168, 85, 247, 0.6) !important;
        transform: scale(1.02);
        background: linear-gradient(135deg, #c084fc 0%, #9333ea 100%) !important;
    }

    .glass-email-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px 24px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-left: 5px solid #c084fc;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease;
    }
    .glass-email-card:hover {
        transform: translateX(4px);
        background: rgba(255, 255, 255, 0.08);
    }

    .email-details h4 { margin: 0; color: #ffffff; font-size: 17px; font-weight: 700; }
    .email-details p { margin: 5px 0 0 0; color: #cbd5e1; font-size: 13px; }
    
    .neon-badge {
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        background: rgba(192, 132, 252, 0.15);
        color: #e9d5ff;
        border: 1px solid rgba(192, 132, 252, 0.4);
    }
    
    [data-testid="stSidebar"] {
        background: #0f081d;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# GMAIL SMART LEAVE AUTO-REPLY LOGIC
# ==========================================
def fetch_and_reply_leave_gmail(email_user, email_pass, target_inbox):
    if 'processed_emails' not in st.session_state:
        st.session_state.processed_emails = set()
        
    processed_logs = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            return []

        ignore_senders = ["babypips", "instagram", "google", "facebook", "twitter", "linkedin", "newsletter", "no-reply", "noreply", "support@"]

        for num in messages[0].split():
            res, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    
                    if subject.lower().startswith("re:"):
                        continue
                    
                    msg_id = msg.get("Message-ID")
                    if msg_id in st.session_state.processed_emails:
                        continue
                    
                    from_whom = msg.get("From", "").lower()
                    
                    if any(bad in from_whom for bad in ignore_senders):
                        continue

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    body_lower = body.lower()
                    sick_keywords = ["sick", "fever", "ill", "unwell", "doctor", "hospital", "medical"]
                    personal_keywords = ["personal reason", "family issue", "emergency", "urgent work", "cant come", "can't come", "not coming", "chutti", "leave", "absent"]

                    category = ""
                    reply_text = ""

                    if any(word in body_lower for word in sick_keywords):
                        category = "Sick Leave"
                        reply_text = f"Dear Employee,\n\nYour sick leave request has been received and noted. Rest well and take care of your health.\n\nBest Regards,\nHR Team"
                    elif any(word in body_lower for word in personal_keywords):
                        category = "Personal / Annual Leave"
                        reply_text = f"Dear Employee,\n\nYour leave request has been received and noted. Thank you for informing us in time.\n\nBest Regards,\nHR Team"
                    else:
                        continue 

                    try:
                        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
                        smtp_server.starttls()
                        smtp_server.login(email_user, email_pass)
                        
                        msg_reply = MIMEMultipart()
                        msg_reply['From'] = email_user
                        msg_reply['To'] = from_whom
                        msg_reply['Subject'] = f"Re: {subject}"
                        msg_reply.attach(MIMEText(reply_text, 'plain'))
                        
                        smtp_server.sendmail(email_user, from_whom, msg_reply.as_string())
                        smtp_server.quit()
                        
                        if msg_id:
                            st.session_state.processed_emails.add(msg_id)
                        status_action = "Auto-Replied ✅"
                    except Exception:
                        status_action = "Failed to Reply ❌"

                    processed_logs.append({
                        "title": subject[:40],
                        "from": from_whom,
                        "summary": body[:90] + "...",
                        "category": category,
                        "action": status_action
                    })

        mail.logout()
        return processed_logs
    except Exception as e:
        raise e

# ==========================================
# SIDEBAR CONTROLS & SIGN-IN
# ==========================================
if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False

with st.sidebar:
    st.markdown("<h3 style='color:#ffffff; font-weight:800; margin-bottom:20px;'>⚙️ Gmail Gateway</h3>", unsafe_allow_html=True)
    gmail_email = st.text_input("HR Inbox Email", value="yarayaseen@gmail.com")
    gmail_pass = st.text_input("Gmail App Password", type="password", placeholder="Enter 16-digit app password...")
    
    if st.button("Sign In ➔"):
        if not gmail_pass:
            st.warning("Please enter your App Password!")
        else:
            try:
                test_mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
                test_mail.login(gmail_email, gmail_pass)
                test_mail.logout()
                st.session_state.is_connected = True
                st.success("Signed In Successfully!")
            except Exception as e:
                st.session_state.is_connected = False
                st.error("Authentication Failed! Use Google 'App Password'.")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    
    if st.session_state.is_connected:
        st.markdown("<p style='color:#4ade80; font-size:13px; font-weight:600;'>System Status: 🟢 Connected</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#f87171; font-size:13px; font-weight:600;'>System Status: 🔴 Not Connected</p>", unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD HEADER
# ==========================================
st.markdown('<div class="dash-title">Workforce MailSync AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Next-Gen Intelligent Same-Day Leave & Annual Response System</div>', unsafe_allow_html=True)

# Cards Row
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="organic-pill-card"><div class="metric-value">--</div><div class="metric-label">Today Scanned</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="organic-pill-card"><div class="metric-value" style="color:#e879f9;">--</div><div class="metric-label">Replies Dispatched</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="organic-pill-card"><div class="metric-value" style="color:#c084fc;">100%</div><div class="metric-label">Context Match</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# LIVE SCANNER SECTION
# ==========================================
if 'leave_results' not in st.session_state:
    st.session_state.leave_results = None

action_col, text_col = st.columns([3, 7])

with action_col:
    st.markdown("<h3 style='color:#ffffff; font-weight:700;'>🤖 Live Mail Sync</h3>", unsafe_allow_html=True)
    st.write("Scan unread inbox mail and trigger context-aware smart auto-replies instantly.")
    
    if st.button("Fetch & Smart Auto-Reply ➔"):
        if not st.session_state.is_connected:
            st.warning("Please sign in with your App Password from the sidebar first!")
        else:
            try:
                with st.spinner("Analyzing leave requests securely..."):
                    results = fetch_and_reply_leave_gmail(gmail_email, gmail_pass, gmail_email)
                    st.session_state.leave_results = results
                st.success(f"Done! Processed {len(results)} requests.")
            except Exception as ex:
                st.error(f"Error: {ex}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Clear Feed 🗑️"):
        st.session_state.leave_results = None
        st.rerun()

with text_col:
    st.markdown("<h3 style='color:#ffffff; font-weight:700;'>📥 Processed Leave Feed</h3>", unsafe_allow_html=True)
    
    if st.session_state.leave_results is None:
        st.info("Awaiting manual trigger. Click the left button to begin scanning.")
    elif len(st.session_state.leave_results) == 0:
        st.warning("No new matching leave requests found in the inbox.")
    else:
        for item in st.session_state.leave_results:
            card_html = f"""
            <div class="glass-email-card">
                <div class="email-details">
                    <h4>{item['title']}</h4>
                    <p><b>From:</b> {item['from']}</p>
                    <p style="color:#e2e8f0;"><i>{item['summary']}</i></p>
                </div>
                <div style="text-align: right;">
                    <span class="neon-badge">{item['category']}</span><br>
                    <p style="margin-top:8px; font-size:12px; color:#e879f9;"><b>{item['action']}</b></p>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
