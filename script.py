import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
import getpass


def read_data():
    print('reading data')
    df = pd.read_csv("data.csv")
    print(df)
    return df.to_dict('records')


# Sending the GSM lead an email informing them that the empty charge is too high
def send_email(smtp, sender, recipients, cc, subject, text, files=None):
    try:
        print('Sending email...')
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipients
        msg['Cc'] = cc
        msg['Subject'] = subject

        msg.attach(MIMEText(text, 'html'))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=f
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % f
            msg.attach(part)

        smtp.sendmail(sender, recipients, msg.as_string())
        print("Sent email to: " + str(recipients))
        return True

    except Exception as ex:
        print("Could not send email!")
        print(ex.args)
        raise ex


def main():

    host = 'smtp.gmail.com'
    port = 587
    sender = 'colebromaps@gmail.com'
    try:
        password = getpass.getpass()
    except Exception as error:
        print('ERROR', error)

    smtp = smtplib.SMTP(host=host, port=port)
    smtp.starttls()
    smtp.login(sender, password)

    data = read_data()

    env = Environment(
        loader=PackageLoader('script', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    for d in data:
        t = env.get_template('example.html')

        send_email(smtp, sender, d['email'], None, "Subject", t.render(data=d))

    smtp.close()


if __name__ == '__main__':
    main()



