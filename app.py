from flask import Flask
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import render_template
import pandas as pd

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/email/<recipient>/<subject>/<body>')
def email(recipient, subject, body):
    print("Email ...")
    print(recipient)
    print(subject)
    print(body)
    send_email(recipient, None, subject, body)
    print('after send email')
    return "hello"


# Sending the GSM lead an email informing them that the empty charge is too high
def send_email(recipients, cc, subject, text, files=None, html=True):
    try:
        print('Sending email...')
        msg = MIMEMultipart()
        msg['From'] = 'colebromaps@gmail.com'
        msg['To'] = recipients
        # msg['To'] = ", ".join(recipients)
        if cc:
            msg['Cc'] = ", ".join(cc)
        msg['Subject'] = subject

        if html:
            msg.attach(MIMEText(text, 'html'))
        else:
            msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=f
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % f
            msg.attach(part)

        smtp = smtplib.SMTP('localhost', timeout=2)
        smtp.sendmail(msg['From'], recipients, msg.as_string())
        smtp.close()
        print("Sent email to: " + str(recipients))
        return True

    except Exception as ex:
        print("Could not send email!")
        print(ex.args)
        raise ex


@app.route('/test')
def test_account():
    app_name = 'Cloud Billing Platform'
    app_ip = '10.203.55.14'

    send_email('cbrossar@cisco.com', None, 'Confirm Registered Account',
               render_template('user_account_confirm.html', app_name=app_name, app_ip=app_ip))
    return 'Sent successfully!'


@app.route('/azure')
def azure():
    test = [{'service_admin_email': ['cole.brossart@gmail.com'],
             'service_admin_name': 'Cole',
             'azr_acct_name': 'Cisco-ENB-CSR1000v',
             'billing_admin_email': ['cole.brossart@gmail.com'],
             'dept_code': '020020942'}]

    # read in via csv file!
    df = pd.read_csv("tenants.csv")

    print(df)

    tenants = []
    for index, row in df.iterrows():
        tenant = dict(service_admin_email=(row['service_admin_email']).split(","),
                      service_admin_name=row['service_admin_name'],
                      azr_acct_name=row['azr_acct_name'],
                      billing_admin_email=(row['billing_admin_email']).split(","),
                      dept_code=row['dept_code'])
        tenants.append(tenant)

    for tenant in tenants:
        print(tenant)
    send_email(tenant['service_admin_email'], tenant['billing_admin_email'],
               "Action Required: Azure Account: " + tenant['azr_acct_name'] + " Configuration in CloudHealth",
               render_template('azure_ch_enablement.html', user=tenant))