import streamlit as st
import pandas as pd
import time
import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import re

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Workforce MailSync AI", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM THEME (Orange Sidebar + Crystal Cards)
# ==========================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #2e1065 0%, #0f0728 60%, #030014 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* Hero Header Section - Clean White Background */
    .hero-box {
        background: #ffffff;
        border: 1px solid rgba(255, 140, 0, 0.4);
        border-radius: 24px;
        padding: 35px 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .hero-title {
        font-size: 38px;
        font-weight: 900;
        color: #0f0728;
        letter-spacing: -1px;
        margin: 0;
    }
    .hero-title span {
        background: linear-gradient(135deg, #ff922b 0%, #e8590c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        color: #475569;
        font-size: 14px;
        margin-top: 8px;
        font-weight: 500;
    }

    /* Shiny Crystal Mail Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 146, 43, 0.4);
        border-top: 2px solid rgba(255, 255, 255, 0.6);
        border-radius: 18px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 15px 35px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -50%;
        width: 200%;
        height: 50%;
        background: linear-gradient(to bottom, rgba(255, 255, 255, 0.08), transparent);
        pointer-events: none;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        border-color: rgba(255, 146, 43, 0.8);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.3), 0 20px 40px rgba(255, 146, 43, 0.15);
    }
    .stat-num { font-size: 32px; font-weight: 900; color: #ffffff; text-shadow: 0 0 15px rgba(255, 146, 43, 0.3); }
    .stat-lbl { font-size: 11px; color: #cbd5e1; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px; }

    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #ff922b 0%, #e8590c 100%) !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        box-shadow: 0 10px 25px rgba(232, 89, 12, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(255, 146, 43, 0.6) !important;
        background: linear-gradient(135deg, #ffa94d 0%, #f76707 100%) !important;
    }

    /* Email Feed Cards */
    .mail-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 5px solid #ff922b;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .mail-item h4 { margin: 0; color: #ffffff; font-size: 16px; font-weight: 700; }
    .mail-item p { margin: 4px 0 0 0; color: #cbd5e1; font-size: 13px; }
    
    .badge-tag {
        background: rgba(255, 146, 43, 0.15);
        border: 1px solid rgba(255, 146, 43, 0.4);
        color: #ffd8a8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }

    /* Sidebar Styling - Orange Shaded Gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #431407 0%, #7c2d12 50%, #9a3412 100%);
        border-right: 1px solid rgba(255, 140, 0, 0.2);
    }
    [data-testid="stSidebar"] .stTextInput label {
        color: #ffedd5 !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stCheckbox label {
        color: #ffedd5 !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'is_connected' not in st.session_state:
    st.session_state.is_connected = True
if 'saved_email' not in st.session_state:
    st.session_state.saved_email = "erp.usmanmkj@gmail.com"
if 'saved_pass' not in st.session_state:
    st.session_state.saved_pass = ""
if 'sent_history' not in st.session_state:
    st.session_state.sent_history = []
if 'today_scanned_count' not in st.session_state:
    st.session_state.today_scanned_count = 0
if 'lock_credentials' not in st.session_state:
    st.session_state.lock_credentials = True  # Default locked / read-only

# ==========================================
# HELPER: EXTRACT SENDER NAME
# ==========================================
def extract_sender_name(from_header):
    if '<' in from_header and '>' in from_header:
        name_part = from_header.split('<')[0].strip(' "\'')
        if name_part and '@' not in name_part:
            return name_part
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', from_header)
    if email_match:
        local_part = email_match.group(0).split('@')[0]
        cleaned = re.sub(r'[\._-', ' ', local_part).title()
        if cleaned.lower() not in ['hr', 'support', 'admin', 'no reply', 'noreply']:
            return cleaned
    return None

# ==========================================
# GMAIL LOGIC
# ==========================================
def fetch_leave_mails_only(email_user, email_pass):
    if 'processed_emails' not in st.session_state:
        st.session_state.processed_emails = set()
        
    fetched_logs = []
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
                    
                    from_whom_raw = msg.get("From", "")
                    from_whom_lower = from_whom_raw.lower()
                    
                    if any(bad in from_whom_lower for bad in ignore_senders):
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
                    
                    emp_name = extract_sender_name(from_whom_raw)
                    salutation = f"Dear {emp_name}," if emp_name else "Hello,"

                    if any(word in body_lower for word in sick_keywords):
                        category = "Sick Leave"
                        reply_text = (
                            f"{salutation}\n\n"
                            "Your sick leave request has been received and noted. Rest well. "
                            "Kindly bring the medical certificate once you resume work.\n\n"
                            "Regards,\n"
                            "Amazon PXT Team"
                        )
                    elif any(word in body_lower for word in personal_keywords):
                        category = "Personal / Annual Leave"
                        reply_text = (
                            f"{salutation}\n\n"
                            "Your leave request has been received and noted. Thank you for informing us in time.\n\n"
                            "Regards,\n"
                            "Amazon PXT Team"
                        )
                    else:
                        continue 

                    fetched_logs.append({
                        "msg_id": msg_id,
                        "title": subject[:40],
                        "from": from_whom_raw,
                        "summary": body[:90] + "...",
                        "category": category,
                        "reply_text": reply_text,
                        "action": "Pending Reply ⏳"
                    })

        mail.logout()
        st.session_state.today_scanned_count = len(fetched_logs)
        return fetched_logs
    except Exception as e:
        raise e

def dispatch_replies_gmail(email_user, email_pass, items):
    success_count = 0
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for item in items:
        if item["action"] == "Auto-Replied ✅":
            continue
        try:
            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()
            smtp_server.login(email_user, email_pass)
            
            msg_reply = MIMEMultipart()
            msg_reply['From'] = email_user
            msg_reply['To'] = item['from']
            msg_reply['Subject'] = f"Re: {item['title']}"
            msg_reply.attach(MIMEText(item['reply_text'], 'plain'))
            
            smtp_server.sendmail(email_user, item['from'], msg_reply.as_string())
            smtp_server.quit()
            
            if item['msg_id']:
                st.session_state.processed_emails.add(item['msg_id'])
            item['action'] = "Auto-Replied ✅"
            
            # Save to sent history box
            st.session_state.sent_history.append({
                "to": item['from'],
                "subject": item['title'],
                "category": item['category'],
                "body": item['reply_text'],
                "time": current_time
            })
            
            success_count += 1
        except Exception:
            item['action'] = "Failed to Reply ❌"
    return success_count

# ==========================================
# SIDEBAR SETUP (WITH LOCK/UNLOCK FEATURE)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#ffffff; font-weight:800; margin-bottom:20px;'>⚙️ Gmail Gateway</h3>", unsafe_allow_html=True)
    
    # Checkbox to lock/unlock inputs
    lock_state = st.checkbox("Lock Credentials (Read-Only)", value=st.session_state.lock_credentials)
    st.session_state.lock_credentials = lock_state
    
    input_email = st.text_input("Email", value=st.session_state.saved_email, disabled=lock_state)
    input_pass = st.text_input("Password", value=st.session_state.saved_pass, type="password", placeholder="Enter 16-digit password...", disabled=lock_state)
    
    if not lock_state:
        if st.button("Update / Save Credentials ➔"):
            if not input_pass:
                st.warning("Please enter your Password!")
            else:
                st.session_state.saved_email = input_email
                st.session_state.saved_pass = input_pass
                st.session_state.is_connected = True
                st.success("Credentials Updated!")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbf7d0; font-size:13px; font-weight:700;'>Status: 🟢 Always Connected</p>", unsafe_allow_html=True)

# ==========================================
# MAIN LAYOUT
# ==========================================
st.markdown("""
    <div class="hero-box">
        <div>
            <div class="hero-title">Workforce MailSync <span>AI</span></div>
            <div class="hero-subtitle">Automated Intelligent Leave Response & Workforce Inbox Monitoring Suite</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Metrics Grid (Crystal Cards) with Live Date & Counters
current_date_day = datetime.datetime.now().strftime("%d %b %Y (%A)")
total_scanned = st.session_state.today_scanned_count
total_dispatched = len(st.session_state.sent_history)

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{total_scanned}</div><div class="stat-lbl">Today Scanned</div><div style="font-size:10px; color:#ff922b; margin-top:4px; font-weight:600;">{current_date_day}</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#ff922b;">{total_dispatched}</div><div class="stat-lbl">Dispatched Replies</div></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown('<div class="stat-card"><div class="stat-num" style="color:#cbd5e1;">100%</div><div class="stat-lbl">AI Context Match</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Action Hub & Feed Layout
if 'leave_results' not in st.session_state:
    st.session_state.leave_results = None

control_col, feed_col = st.columns([4, 6])

with control_col:
    st.markdown("<h3 style='color:#ffffff; font-weight:700; font-size:23px; white-space:nowrap;'>📬 Auh1-fc-pxt@amazon.ae</h3>", unsafe_allow_html=True)
    st.write("Trigger inbox scanning to process incoming leave requests with AI parsing.")
    
    if st.button("Run Smart Sync ➔"):
        active_pass = st.session_state.saved_pass if st.session_state.lock_credentials else input_pass
        active_email = st.session_state.saved_email if st.session_state.lock_credentials else input_email
        
        if not active_pass:
            st.warning("Please configure your Password in the sidebar first!")
        else:
            try:
                with st.spinner("Scanning unread inbox messages..."):
                    results = fetch_leave_mails_only(active_email, active_pass)
                    st.session_state.leave_results = results
                st.success(f"Successfully synced {len(results)} items!")
                st.rerun()
            except Exception as ex:
                st.error(f"Error: {ex}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Reply Mail ➔"):
        active_pass = st.session_state.saved_pass if st.session_state.lock_credentials else input_pass
        active_email = st.session_state.saved_email if st.session_state.lock_credentials else input_email
        
        if not active_pass:
            st.warning("Please configure your Password in the sidebar first!")
        elif not st.session_state.leave_results:
            st.warning("No synced emails available to reply. Run Smart Sync first!")
        else:
            try:
                with st.spinner("Dispatching responses securely..."):
                    count = dispatch_replies_gmail(active_email, active_pass, st.session_state.leave_results)
                st.success(f"Successfully dispatched {count} replies!")
                st.rerun()
            except Exception as ex:
                st.error(f"Error: {ex}")

with feed_col:
    tab_choice = st.radio("View Mode", ["📥 Processed Feed", "📤 Sent Box History"], horizontal=True, label_visibility="collapsed")
    
    if tab_choice == "📥 Processed Feed":
        feed_head_col1, feed_head_col2 = st.columns([7, 3])
        with feed_head_col1:
            st.markdown("<h3 style='color:#ffffff; font-weight:700; margin-top:0;'>📥 Processed Feed</h3>", unsafe_allow_html=True)
        with feed_head_col2:
            if st.button("Clear Feed 🗑️", key="clear_feed_btn"):
                st.session_state.leave_results = None
                st.rerun()
        
        if st.session_state.leave_results is None:
            st.info("System on standby. Run Smart Sync to load inbox requests.")
        elif len(st.session_state.leave_results) == 0:
            st.warning("No new relevant leave requests found.")
        else:
            for item in st.session_state.leave_results:
                badge_color = "#4ade80" if item['action'] == "Auto-Replied ✅" else "#ff922b"
                card_html = f"""
                <div class="mail-item">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h4>{item['title']}</h4>
                            <p><b>From:</b> {item['from']}</p>
                            <p style="color:#cbd5e1; margin-top:6px;"><i>{item['summary']}</i></p>
                        </div>
                        <div style="text-align:right; min-width:110px;">
                            <span class="badge-tag">{item['category']}</span><br>
                            <span style="font-size:11px; color:{badge_color}; font-weight:700; display:inline-block; margin-top:6px;">{item['action']}</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
    else:  # Sent Box View
        sent_head_col1, sent_head_col2 = st.columns([7, 3])
        with sent_head_col1:
            st.markdown("<h3 style='color:#ffffff; font-weight:700; margin-top:0;'>📤 Sent Box History</h3>", unsafe_allow_html=True)
        with sent_head_col2:
            if st.button("Clear History 🗑️", key="clear_sent_btn"):
                st.session_state.sent_history = []
                st.rerun()
                
        if len(st.session_state.sent_history) == 0:
            st.info("No dispatched replies found in the sent history yet.")
        else:
            for sent_item in reversed(st.session_state.sent_history):
                formatted_body = sent_item['body'].replace('\n', '<br>')
                sent_card_html = f"""
                <div class="mail-item" style="border-left-color: #4ade80;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h4>Re: {sent_item['subject']}</h4>
                            <p><b>To:</b> {sent_item['to']}</p>
                            <p style="color:#94a3b8; font-size:11px; margin-top:2px;"><b>Time:</b> {sent_item['time']}</p>
                            <details style="margin-top: 8px; color: #cbd5e1; font-size: 12px; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 8px;">
                                <summary style="cursor: pointer; color: #ff922b; font-weight: 600;">View Exact Sent Reply</summary>
                                <p style="margin-top: 6px; color: #f1f5f9;">{formatted_body}</p>
                            </details>
                        </div>
                        <div style="text-align:right; min-width:110px;">
                            <span class="badge-tag">{sent_item['category']}</span><br>
                            <span style="font-size:11px; color:#4ade80; font-weight:700; display:inline-block; margin-top:6px;">Sent ✅</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(sent_card_html, unsafe_allow_html=True)
