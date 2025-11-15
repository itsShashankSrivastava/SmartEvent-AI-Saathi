from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import pandas as pd
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter(prefix="/agent", tags=["guest-invitations"])

# Email templates for different event types
EMAIL_TEMPLATES = {
    "wedding": {
        "subject": "You're Invited to Our Wedding Celebration! 💍",
        "body": """
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #fff5f7; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #d946ef; text-align: center;">💍 Wedding Invitation 💍</h1>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">Dear {name},</p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    We are delighted to invite you to celebrate our special day with us!
                </p>
                <div style="background-color: #fce7f3; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event_type}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                    <p style="margin: 5px 0;"><strong>Venue:</strong> {venue}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {event_time}</p>
                </div>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Your presence would mean the world to us as we begin this beautiful journey together.
                </p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    With love and warm regards,<br>
                    <strong>The Happy Couple</strong>
                </p>
            </div>
        </body>
        </html>
        """
    },
    "birthday": {
        "subject": "You're Invited to a Birthday Celebration! 🎂",
        "body": """
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #fef3c7; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #f59e0b; text-align: center;">🎂 Birthday Party Invitation 🎉</h1>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">Dear {name},</p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    You're invited to join us for a fantastic birthday celebration!
                </p>
                <div style="background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event_type}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                    <p style="margin: 5px 0;"><strong>Venue:</strong> {venue}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {event_time}</p>
                </div>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Let's make this day unforgettable with lots of fun, laughter, and cake!
                </p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Looking forward to celebrating with you!<br>
                    <strong>See you there!</strong>
                </p>
            </div>
        </body>
        </html>
        """
    },
    "corporate": {
        "subject": "Invitation to Corporate Event 🏢",
        "body": """
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f0f9ff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #3b82f6; text-align: center;">🏢 Corporate Event Invitation</h1>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">Dear {name},</p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    We cordially invite you to attend our upcoming corporate event.
                </p>
                <div style="background-color: #dbeafe; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event_type}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                    <p style="margin: 5px 0;"><strong>Venue:</strong> {venue}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {event_time}</p>
                </div>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    This event promises to be an excellent opportunity for networking and professional growth.
                </p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    We look forward to your presence.<br>
                    <strong>Best regards,<br>Event Management Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
    },
    "anniversary": {
        "subject": "Join Us for an Anniversary Celebration! 💕",
        "body": """
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #fce7f3; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #ec4899; text-align: center;">💕 Anniversary Celebration 💕</h1>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">Dear {name},</p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    We would be honored to have you join us as we celebrate this special milestone!
                </p>
                <div style="background-color: #fce7f3; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event_type}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                    <p style="margin: 5px 0;"><strong>Venue:</strong> {venue}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {event_time}</p>
                </div>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Your presence will make our celebration even more memorable.
                </p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    With warm wishes,<br>
                    <strong>The Celebrants</strong>
                </p>
            </div>
        </body>
        </html>
        """
    },
    "engagement": {
        "subject": "You're Invited to Our Engagement Celebration! 💍",
        "body": """
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f3e8ff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #a855f7; text-align: center;">💍 Engagement Celebration 💍</h1>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">Dear {name},</p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    We're thrilled to invite you to celebrate our engagement!
                </p>
                <div style="background-color: #f3e8ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event_type}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                    <p style="margin: 5px 0;"><strong>Venue:</strong> {venue}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {event_time}</p>
                </div>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Join us as we embark on this exciting new chapter of our lives!
                </p>
                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    With love,<br>
                    <strong>The Engaged Couple</strong>
                </p>
            </div>
        </body>
        </html>
        """
    }
}

# Store guest lists per agent
guest_lists = {}

@router.post("/upload-guest-list")
async def upload_guest_list(
    file: UploadFile = File(...),
    agent_id: Optional[str] = Form(None)
):
    """Upload guest list Excel/CSV file"""
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload .xlsx, .xls, or .csv file")
        
        # Validate columns
        if 'Name' not in df.columns or 'Email' not in df.columns:
            raise HTTPException(status_code=400, detail="File must contain 'Name' and 'Email' columns")
        
        # Extract guest data
        guests = []
        for _, row in df.iterrows():
            name = str(row['Name']).strip()
            email = str(row['Email']).strip()
            if name and email and '@' in email:
                guests.append({"name": name, "email": email})
        
        if not guests:
            raise HTTPException(status_code=400, detail="No valid guest entries found in file")
        
        # Store guest list
        if agent_id:
            guest_lists[agent_id] = guests
        
        return {
            "success": True,
            "total_guests": len(guests),
            "guests": guests[:5],  # Return first 5 as preview
            "message": f"Successfully uploaded {len(guests)} guests"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.post("/send-invitations/{agent_id}")
async def send_invitations(
    agent_id: str,
    event_type: str = Form(...),
    event_date: str = Form("TBD"),
    venue: str = Form("TBD"),
    event_time: str = Form("TBD")
):
    """Send email invitations to all guests"""
    try:
        if agent_id not in guest_lists:
            raise HTTPException(status_code=404, detail="No guest list found for this session")
        
        guests = guest_lists[agent_id]
        event_type_lower = event_type.lower()
        
        # Get template
        template = EMAIL_TEMPLATES.get(event_type_lower, EMAIL_TEMPLATES["corporate"])
        
        # Send emails (mock implementation - replace with actual SMTP)
        sent_count = 0
        failed = []
        
        for guest in guests:
            try:
                # Format email body
                email_body = template["body"].format(
                    name=guest["name"],
                    event_type=event_type,
                    event_date=event_date,
                    venue=venue,
                    event_time=event_time
                )
                
                # Send actual email
                print(f"📧 Sending invitation to {guest['name']} ({guest['email']})")
                send_email(guest['email'], template['subject'], email_body)
                
                sent_count += 1
            except Exception as e:
                failed.append({"name": guest["name"], "email": guest["email"], "error": str(e)})
        
        return {
            "success": True,
            "total_sent": sent_count,
            "total_failed": len(failed),
            "failed_emails": failed,
            "message": f"Successfully sent {sent_count} invitations"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send invitations: {str(e)}")

def send_email(to_email: str, subject: str, html_body: str):
    """Send email using SMTP (Gmail)"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        raise Exception("Email credentials not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env file")
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
