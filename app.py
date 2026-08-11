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
        border-left: 6px solid #f59e0b;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .email-details h4 { margin: 0; color: #1e293b; font-size: 18px; font-weight: 700; }
    .email-details p { margin: 4px 0 0 0; color: #64748b; font-size: 14px; }
    
    .ai-badge {
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        background: #fef3c7; 
        color: #d97706;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# GMAIL SMART LEAVE AUTO-REPLY LOGIC
# ==========================================
def fetch_and_reply_leave_gmail(email_user, email_pass, target_inbox):
    processed_logs = []
    try:
        # 1. Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
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
                        body = part.get_payload(decode=True).decode(errors="ignore")

                    body_lower = body.lower()

                    # 2. Categorized Keywords (Sick vs Personal/Annual Leave)
                    sick_keywords = ["sick", "fever", "ill", "unwell", "doctor", "hospital", "medical"]
                    personal_keywords = ["personal reason", "family issue", "emergency", "urgent work", "cant come", "can't come", "not coming", "chutti", "leave", "absent"]

                    category = ""
                    reply_text = ""

                    if any(word in body_lower for word in sick_keywords):
                        category = "Sick Leave"
                        reply_text = f"Dear Employee,\n\nYour sick leave request for today has been received and noted by HR. Rest well and take care of your health.\n\nBest Regards,\nHR Team ({target_inbox})"
                    elif any(word in body_lower for word in personal_keywords):
                        category = "Personal / Annual Leave"
                        reply_text = f"Dear Employee,\n\nYour leave request for today has been received and noted by HR. Thank you for informing us in time.\n\nBest Regards,\nHR Team ({target_inbox})"
                    else:
                        continue 

                    # 3. Send Auto-Reply via Gmail SMTP
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
                        status_action = "Auto-Replied ✅"
                    except Exception as e:
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
# SIDEBAR SETTINGS & SIGN-IN
# ==========================================
if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2646/2646141.png", width=60)
    st.markdown("### ⚙️ Gmail Leave Sync")
    gmail_email = st.text_input("HR Inbox Email", value="erp.usman@gmail.com")
    gmail_pass = st.text_input("Gmail App Password", type="password", placeholder="Enter 16-digit app password...")
    
    # Sign In Button
    if st.button("Sign In ➔"):
        if not gmail_pass:
            st.warning("Please enter your App Password!")
        else:
            try:
                # Test connection immediately
                test_mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
                test_mail.login(gmail_email, gmail_pass)
                test_mail.logout()
                st.session_state.is_connected = True
                st.success("Signed In Successfully!")
            except Exception as e:
                st.session_state.is_connected = False
                st.error(f"Authentication Failed! Please use Google 'App Password', not normal password.")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.session_state.is_connected:
        st.markdown("<p style='color:green; font-size:13px;'>System Status: 🟢 <b>Connected</b></p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:gray; font-size:12px;'>System Status: 🔴 <b>Not Connected</b></p>", unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD HEADER
# ==========================================
st.markdown('<div class="dash-title">Workforce MailSync AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Smart Same-Day Leave & Annual Response System (Gmail Testing)</div>', unsafe_allow_html=True)

# Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="ai-metric-card"><div class="metric-value">--</div><div class="metric-label">Today Scanned</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#10b981;">--</div><div class="metric-label">Targeted Replies Sent</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="ai-metric-card"><div class="metric-value" style="color:#4f46e5;">100%</div><div class="metric-label">Context Match</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# LIVE SCANNER SECTION
# ==========================================
if 'leave_results' not in st.session_state:
    st.session_state.leave_results = None

action_col, text_col = st.columns([3, 7])

with action_col:
    st.markdown("### 🤖 Check Today's Leaves")
    st.write("Click below to scan unread emails in your Gmail inbox and auto-reply based on leave context (Sick vs Personal/Annual).")
    if st.button("Fetch & Smart Auto-Reply ➔"):
        if not st.session_state.is_connected:
            st.warning("Please sign in successfully using your App Password from the sidebar first!")
        else:
            try:
                with st.spinner("Scanning and analyzing leave reasons..."):
                    results = fetch_and_reply_leave_gmail(gmail_email, gmail_pass, gmail_email)
                    st.session_state.leave_results = results
                st.success(f"Done! Processed {len(results)} leave requests.")
            except Exception as ex:
                st.error(f"Error during fetch: {ex}")

with text_col:
    st.markdown("### 📥 Today's Processed Leave Emails")
    
    if st.session_state.leave_results is None:
        st.info("Click the button on the left to scan incoming unread emails.")
    elif len(st.session_state.leave_results) == 0:
        st.warning("No new leave requests found in the inbox.")
    else:
        for item in st.session_state.leave_results:
            card_html = f"""
            <div class="email-card">
                <div class="email-details">
                    <h4>{item['title']}</h4>
                    <p><b>From:</b> {item['from']}</p>
                    <p><i>Reason/Content: {item['summary']}</i></p>
                </div>
                <div style="text-align: right;">
                    <span class="ai-badge">{item['category']}</span><br>
                    <p style="margin-top:8px; font-size:12px; color:#64748b;">Action: <b>{item['action']}</b></p>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
