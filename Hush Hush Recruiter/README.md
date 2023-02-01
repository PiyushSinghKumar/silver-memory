
**Overview of Algoritham Used**

1. Enter skill.

2. Enter number of required candidates.

3. Converting ordinal values to numerical values.

4. A Min-Max scaling is typically done via the following equation:
    Xsc = (X-Xmin)/(Xmax-Xmin)
    
5. Taking average of all scaled numerical columns.

6. picking top n candidates.

**'''
    main method that runs the HushHush Recruiter project end to end
    from model running for candidate selection and sending emails
    and saving the response and notifying the hiring manager
'''**
def main():
    
    global sendEmails
    sendEmails = list(HushHush_algo.hushHush())
    print(sendEmails)
    sendNotificationToCandidate()
    interview_screener.server_question_screen()


if __name__ == "__main__":
    main()

