import flask
from flask import request
import scheduler_
from threading import Thread
from datetime import datetime, date

app = flask.Flask(__name__)
app.config["DEBUG"] = True
pm = scheduler_.ProcessManager()


@app.route('/alert/vaccine/create_alert', methods=['POST'])
def home():
    body = request.get_json()
    date_i = body['date']
    age_slot = body['age_slot']
    district_id = body['district_id']
    email_id = body['email_id']

    ## This needs details of date age_slot district_id and email_id
    #{    "date": "08-05-2021",  "district_id": 314, "age_slot": 45, "email_id": "jay7697agrawal@gmail.com" }
    #After the process if slot will be up you'll get an email with details of slots if not slots will be find then
    #You'll get message for no slot found ##
    
    now = date.today()
    expiration_date = datetime.strptime(date_i, "%d-%m-%Y").date()

    if expiration_date >= now:
        try:
            Thread(target=pm.process_manager, args=[district_id, date_i, age_slot, email_id]).start()
            result = {'status': 200, 'message': 'fetch_start'}
        except:
            result = {'status': 404, 'message': 'some_issue'}
    else:
        result = {'status': 200, 'message': "You have entered the date from past"}

    return result


app.run(host='0.0.0.0', port='3001')