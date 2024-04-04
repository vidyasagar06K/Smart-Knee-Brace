from mpu6050 import mpu6050
import time
from tabulate import tabulate
import smtplib
import getpass
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def create_excel_file(data, file_name='data.xlsx'):
    # Create a Pandas DataFrame
    df = pd.DataFrame(data, columns=["Time (sec)", "Angular Velocity (deg/sec)", "Angle (deg)"])

    # Save the DataFrame to an Excel file
    df.to_excel(file_name, index=False)

def send_email(to_email, to_email_password, subject, body, attachment_path=None):
    # Email configuration
    sender_email = 'vidyasagar16k@outlook.com'
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject

    # Attach body text
    message.attach(MIMEText(body, 'plain'))

    # Attach Excel file if provided
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name="data.xlsx")
            part['Content-Disposition'] = f'attachment; filename={attachment_path}'

        message.attach(part)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, to_email_password)
        server.sendmail(sender_email, to_email, message.as_string())

def integrate(data, time_interval):
    angle = 0.0
    integrated_data = []

    for row in data:
        angular_velocity = row[1]
        angle += angular_velocity * time_interval
        integrated_data.append([row[0], angular_velocity, angle])

    return integrated_data

if __name__ == "__main__":
    # MPU6050 setup and measurement
    mpu = mpu6050(0x68)
    sampling_rate = 2000  # Hz
    time_interval = 1 / sampling_rate
    measurement_duration = 4
    calibration_duration = 2
    calibration_data = {'x': 0, 'y': 0, 'z': 0}

    print("Calibrating... Keep the MPU6050 still.")
    time.sleep(1)

    start_time = time.time()
    while time.time() - start_time < calibration_duration:
        gyro_data = mpu.get_gyro_data()
        calibration_data['x'] += gyro_data['x']
        calibration_data['y'] += gyro_data['y']
        calibration_data['z'] += gyro_data['z']
        time.sleep(time_interval)

    calibration_data = {key: value / (calibration_duration / time_interval) for key, value in calibration_data.items()}
    print("Calibration complete. Offset values:", calibration_data)

    # Initial values
    angle = 0.0
    angular_velocity = 0.0
    start_time = time.time()

    # Data list to store measurement results
    data = []

    while time.time() - start_time < measurement_duration:
        loop_start_time = time.time()

        gyro_data = mpu.get_gyro_data()
        calibrated_gyro_data = {key: gyro_data[key] - calibration_data[key] for key in gyro_data}
        angular_velocity = calibrated_gyro_data['x']
        angle += angular_velocity * time_interval

        data.append([time.time() - start_time, abs(angular_velocity), abs(angle)])

        elapsed_time = time.time() - loop_start_time
        sleep_time = max(0, time_interval - elapsed_time)
        time.sleep(sleep_time)

    # Display data in tabular form
    print(tabulate(data, headers=["Time (s)", "Angular Velocity (deg/s)", "Angle (degrees)"], tablefmt="grid"))

    # Integrate angular velocity to obtain angle
    integrated_data = integrate(data, time_interval)

    # Create Excel file
    create_excel_file(integrated_data)

    # Get recipient's email
    to_email = input("Enter recipient email address: ")

    # Get sender's email password
    to_email_password = getpass.getpass("Enter your email password: ")

    # Send email with the Excel attachment
    send_email(to_email=to_email,
               to_email_password=to_email_password,
               subject='Data Report',
               body='Attached is the data in Excel format.',
               attachment_path='data.xlsx')

    print("Email sent successfully!")
