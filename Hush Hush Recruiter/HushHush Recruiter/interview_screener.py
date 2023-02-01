import pymongo
from flask import Flask, render_template, request
import email_sender

def server_question_screen():
    app = Flask(__name__)

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client.HushHush_Recruiter
    candidates_response = db.candidates_response


    @app.route('/form')
    def form():
        return render_template('./question_screen.html')


    @app.route('/data', methods=['POST', 'GET'])
    def data():
        if request.method == 'GET':
            return f"The URL /data is accessed directly. Try going to '/form' to submit form"
        if request.method == 'POST':
            form_data = request.form
            name = request.form['Name']
            city = request.form['City']
            country = request.form['Country']
            question1 = request.form['Question1']
            question2 = request.form['Question2']
            question3 = request.form['Question3']
            question4 = request.form['Question4']
            question5 = request.form['Question5']

            candidates_response.insert_one({'Name': name, 'City': city, 'Country': country, 'Question1': question1,
                                            'Question2': question2, 'Question3': question3, 'Question4': question4,
                                            'Question5': question5})
            email_sender.sendHiringManagerNotification()
            return render_template('./data.html', form_data = form_data)


    app.run(host='localhost', port=5000)
