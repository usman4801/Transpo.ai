# Updated Gmail Logic inside the app
def fetch_and_reply_leave_gmail(email_user, email_pass, target_inbox):
    # Initialize persistent state for processed emails if not exists
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
                    
                    # 1. Subject Extraction
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    
                    # 2. Manual Reply Detection (Skip if 'Re:' is already in subject)
                    if subject.lower().startswith("re:"):
                        continue
                    
                    # 3. Duplicate Prevention (Tracking by Message-ID or From + Subject)
                    msg_id = msg.get("Message-ID")
                    if msg_id in st.session_state.processed_emails:
                        continue
                    
                    from_whom = msg.get("From", "").lower()
                    
                    # Skip promotional
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
                        reply_text = f"Dear Employee,\n\nYour sick leave request has been received. Rest well.\n\nBest Regards,\nHR Team"
                    elif any(word in body_lower for word in personal_keywords):
                        category = "Personal / Annual Leave"
                        reply_text = f"Dear Employee,\n\nYour leave request has been received. Thank you.\n\nBest Regards,\nHR Team"
                    else:
                        continue 

                    # Send Reply
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
                        
                        # Add to processed tracker
                        st.session_state.processed_emails.add(msg_id)
                        status_action = "Auto-Replied ✅"
                    except:
                        status_action = "Failed ❌"

                    processed_logs.append({
                        "title": subject[:40],
                        "from": from_whom,
                        "category": category,
                        "action": status_action
                    })

        mail.logout()
        return processed_logs
    except Exception as e:
        raise e
