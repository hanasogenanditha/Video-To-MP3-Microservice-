import smtplib
import os
from email.message import EmailMessage


def notification(message):
    try:
        # message is already a dict
        mp3_fid = message["mp3_fid"]
        receiver_address = message["username"]

        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")

        if not sender_address or not sender_password:
            raise Exception("Email credentials not set")

        msg = EmailMessage()
        msg.set_content(f"Your MP3 is ready!\n\nFile ID: {mp3_fid}")
        msg["Subject"] = "MP3 Download Ready 🎵"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(msg)
        session.quit()

        print("Mail Sent to", receiver_address)
        return None

    except Exception as err:
        print("Email failed:", err)
        return err
