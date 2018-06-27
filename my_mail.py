from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtpd import COMMASPACE
import smtplib

from config import *

def send_mail(sub, content, send_mail_list):
    mail_obj = smtplib.SMTP(SMPT_HOST, SMPT_PORT)
    mail_obj.docmd(DOCMD, MAIL_ACCOUNT)
    mail_obj.starttls()
    mail_obj.login(MAIL_ACCOUNT, PASSWD)
    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = COMMASPACE.join(send_mail_list)
    msg['Subject'] = sub
    con = MIMEText(content, 'html', 'utf-8')
    msg.attach(con)
    mail_obj.sendmail(MAIL_ACCOUNT, send_mail_list, msg.as_string())
    mail_obj.quit()

if __name__ == '__main__':
    send_mail('Get Information Completed', 'Get information completed, please check it!', TO_SOMEONE)
