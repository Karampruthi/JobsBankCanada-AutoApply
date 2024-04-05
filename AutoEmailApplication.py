# Import necessary libraries
from cover_letter_variables import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import ast

# Function to send email with optional attachment
def send_email(sender_address, sender_pass, receiver_address, subject, body, attachment_path=None):
    """
    Sends an email from sender to receiver with a subject, body, and optional attachment.
    
    Parameters:
    - sender_address: Email address of the sender.
    - sender_pass: Password for the sender's email account.
    - receiver_address: Email address of the receiver.
    - subject: Subject line of the email.
    - body: Main content of the email.
    - attachment_path: Path to the file to be attached with the email.
    
    Returns:
    - True if the email was sent successfully, False otherwise.
    """
    try:
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(attachment.read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', f"attachment; filename={attachment_path.split('/')[-1]}")
                message.attach(p)

        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # Use 587 for TLS
        session.starttls()  # Secure the connection
        session.login(sender_address, sender_pass)  # Login to the email server
        session.sendmail(sender_address, receiver_address, message.as_string())
        session.quit()
        print("Email sent successfully to", receiver_address)
        return True
    except Exception as e:
        print(f"Failed to send email to {receiver_address}: {e}")
        return False

# Function to extract screening questions from job instructions
def extract_screening_questions(job_instructions_str):
    """
    Extracts screening questions from a job instructions string.
    
    Parameters:
    - job_instructions_str: A string representation of a list containing job instructions.
    
    Returns:
    - A list of screening questions.
    """
    instructions = ast.literal_eval(job_instructions_str)
    questions = []
    for item in instructions:
        if "This job posting includes screening questions" in item:
            questions = instructions[instructions.index(item) + 1:]
            break
    return [q for q in questions if '?' in q]

# Function to format screening answers
def format_screening_answers(questions, standard_responses):
    """
    Formats answers to screening questions based on predefined responses.
    
    Parameters:
    - questions: A list of screening questions.
    - standard_responses: A dictionary mapping questions to standard responses.
    
    Returns:
    - A string with formatted questions and answers.
    """
    answers = []
    for question in questions:
        answer = standard_responses.get(question, "I would be pleased to discuss this question further during an interview.")
        answers.append(f"{question} Answer: {answer}")
    return '\n'.join(answers)

# Main script to send emails to jobs listed in 'jobbank.csv' that haven't been applied to
jobs_to_apply = pd.read_csv('jobbank.csv')
jobs_to_apply = jobs_to_apply.drop_duplicates(subset='job_id', keep='first')
jobs_to_apply['Applied'] = jobs_to_apply['Applied'].fillna(False)

# Sender's email credentials
sender_address = 'your.email@gmail.com'
sender_pass = 'yourpassword'  # Consider using environment variables or secure input for credentials

# Process each job and send an email application
for index, row in jobs_to_apply[jobs_to_apply['Applied']==False].iterrows():
    position = row['Position']
    receiver_address = row['Email']
    subject = f'Application for {position.title()}'
    attachment_path = 'Your_Resume.pdf'  # Ensure this path is correct

    # Check if there are screening questions
    if len(ast.literal_eval(row.job_instructions)) > 3:
        questions = extract_screening_questions(row.job_instructions)
        formatted_answers = format_screening_answers(questions, standard_responses)
        body = cover_letter_template_sqa.format(position_title=position.title(), screening_qa=formatted_answers)
    else:
        body = cover_letter_template.format(position_title=position.title())

    # Send email and update the 'Applied' status
    email_success = send_email(sender_address, sender_pass, receiver_address, subject, body, attachment_path)
    jobs_to_apply.at[index, 'Applied'] = email_success

# Save updates to 'jobbank.csv'
jobs_to_apply.to_csv('jobbank.csv', index=False)

print("Finished processing job applications.")
