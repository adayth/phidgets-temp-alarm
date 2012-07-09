import smtplib
from email.mime.text import MIMEText

# Send warning mail with latest readed temperatures
def sendMail(sender, subject, recipients, content):            
    msg = MIMEText(content)
    msg["From"] = sender
    msg["To"] = ', '.join(recipients)
    msg["Subject"] = subject
                        
    s = smtplib.SMTP('localhost')
    #s.login(user, password)
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()