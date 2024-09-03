import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail, Attachment, FileContent, FileName, FileType, Disposition
from dotenv import load_dotenv
import base64

load_dotenv()

def send_email(zip_data, image_name):
    print(f"Received zip_data length: {len(zip_data)}")
    print(f"Image name: {image_name}")
    
    message = SendGridMail(
        from_email=os.getenv('MAIL_DEFAULT_SENDER'),
        to_emails=os.getenv('MAIL_DEFAULT_SENDER'),
        subject="Generated Image",
        plain_text_content="Please find the attached generated image."
    )
    
    try:
        attached_file = Attachment(
            FileContent(zip_data),
            FileName(f"{image_name}.zip"),
            FileType('application/zip'),
            Disposition('attachment')
        )
        message.attachment = attached_file
    except Exception as e:
        print(f"Error creating attachment: {str(e)}")
        return {"error": f"Error creating attachment: {str(e)}"}, 500

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"SendGrid API response status code: {response.status_code}")
        print(f"SendGrid API response body: {response.body}")
        print(f"SendGrid API response headers: {response.headers}")
        return {"message": "Email sent successfully"}, 200
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {"error": f"Error sending email: {str(e)}"}, 500