import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import HushHush_algo
import interview_screener


def sendHiringManagerNotification():
    '''
    function to send email to hiring manager when a candidate takes the interview
    and submits the response
    '''
    message = Mail(
        from_email='abc@gmail.com',
        to_emails='hiringManager@gmail.com',
        subject='Candidate Response Submitted',
        html_content='<strong>Hi,<br> The response of the candidate has been recorded.<br> -Cheers<br>HushHush Recruiter</strong>')
    try:
        sg = SendGridAPIClient('send_grid_key')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        print('Notification email sent to hiring manager')
    except Exception as e:
        print('Something went wrong...')
        print(e.message)

def sendNotificationToCandidate():
    '''
    function to send notification to selected candidates after the model is completed.
    '''
    message = Mail(
        from_email='abc@gmail.com',
        to_emails='candidates_list@gmail.com',
        subject='HushHush Recruiter',
        html_content='<strong>Dear Candidate, <br> Congratulations! You have been selected for Doodle online screening interview round to continue click on the link below.<br><a href="https://www.temporary-url.com/6CA14">click here to start the test</a><br><br> -Cheers<br>HushHush Recruiter</strong>')
    try:
        sg = SendGridAPIClient('send_grid_key')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        print('Email sent to selected candidates')
    except Exception as e:
        print('Something went wrong...')
        print(e.message)


def main():
    '''
    main method that runs the HushHush Recruiter project end to end
    from model running for candidate selection and sending emails
    and saving the response and notifying the hiring manager
    '''
    global sendEmails
    sendEmails = list(HushHush_algo.hushHush())
    print(sendEmails)
    sendNotificationToCandidate()
    interview_screener.server_question_screen()


if __name__ == "__main__":
    main()


