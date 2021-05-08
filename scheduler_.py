import requests
import json
import time
import os
from datetime import datetime
from datetime import date as date_class
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
DATA_PATH = 'data/'
JSON_PATH = DATA_PATH + 'all_schedules.json'

if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)


def send_email(email_ids, message_i):
    context = ssl.create_default_context()
    sender_email = ''
    sender_password = ''

    # "if any issue here Go to Google's Account Security Settings: www.google.com/settings/security " \
    # "Find the field "Access for less secure apps". Set it to "Allowed"."

    for email_i in email_ids:
        receiver_email = email_i
        message = MIMEMultipart("alternative")
        message["Subject"] = "Vaccination slot notification"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        text = str(message_i)
        part1 = MIMEText(text, "plain")
        message.attach(part1)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )


class ProcessManager:
    def __init__(self):
        self.all_processes = {}
        self.running_ids = []
        self.all_requests = {}
        self.done_ids = {} if not os.path.isfile(JSON_PATH) else json.load(open(JSON_PATH, 'r'))

    def process_manager(self, district_id, date, age_slot, email_id):
        process_id = str(district_id) + '-' + date + '-' + str(age_slot)

        if process_id not in self.done_ids:

            if process_id in self.all_processes:
                self.all_processes[process_id].append(email_id)
            else:
                self.all_processes[process_id] = [email_id]

            if process_id not in self.running_ids:
                sf = StartFetch(district_id, date, age_slot)
                sf.find_slot(self, email_id, process_id)
                self.all_requests[process_id] = sf
                self.running_ids.append(process_id)

            else:
                self.all_requests[process_id].find_slot(self, email_id)

        else:
            data = self.done_ids[process_id]
            send_email([email_id], data)
            print("We have this slots details already but subject to matter of available ")
            ######### Sending this data to mentione email Id ##########


class StartFetch:
    def __init__(self, district_id, date, age_slot):
        self.district = district_id
        self.find_slot_endpoint = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?"
        self.date = date #Date should be in DD-MM-YYYY
        self.age_slot = age_slot
        self.check_timer = 10

    def find_slot(self, class_object, email_id, process_id):
        while True:
            now = date_class.today()
            expiration_date = datetime.strptime(self.date, "%d-%m-%Y").date()

            if expiration_date >= now:
                try:
                    slots = self.constant_checker()
                except:
                    slots = []

                if len(slots) > 0:
                    class_object.done_ids[process_id] = slots
                    json.dump(class_object.done_ids, open(JSON_PATH, 'w'))
                    #send an email notfication to all the mails that are registered with the id
                    print("We got the slots for you !!")
                    send_email([email_id], slots)
                    break

                else:
                    print("We are keep fetching the data for this ID :: ", process_id)

                time.sleep(self.check_timer)
            else:
                message = {'message': "Date has Changed no slot found"}
                class_object.done_ids[process_id] = message
                send_email([email_id], message)

    def constant_checker(self):
        request_url = self.find_slot_endpoint + "district_id={}&date={}".format(self.district, self.date)
        header = {'User-Agent': 'PostmanRuntime/7.26.8'}
        r = requests.get(url=request_url, headers=header)

        centers = r.json()['centers']

        today_stat = []
        if len(centers) > 0:
            print("Slot details are available")

            for center in centers:
                session = center['sessions'][0]
                min_age_limit = session['min_age_limit']

                if min_age_limit == self.age_slot:
                    if session['available_capacity'] > 0:
                        # print("==========================================================")
                        # print("Center Name where age limit is {}+ vaccination is going on".format(self.age_slot))
                        # print("Center Name :: {}".format(center['name']))
                        # print("Center Address :: {}".format(center['address']))
                        # print("==========================================================")
                        now = datetime.now()
                        slot_availablity = {'center _name': center['name'], 'center_adress': center['address'],
                                            'available_capacity': session['available_capacity'],
                                            'vaccine': session['vaccine'], 'slots': session['slots'],
                                            'district_name': center['district_name'],
                                            'state_name': center['state_name'],
                                            'fetch_time': now.strftime("%d/%m/%Y %H:%M:%S")}

                        today_stat.append(slot_availablity)

            if len(today_stat) > 0:
                json.dump(today_stat, open(self.date + '_' + str(self.age_slot) + '_.json', 'w'))
        else:
            print("Slot not available for {}".format(self.date))

        return today_stat


#
# so = StartFetch(314, '08-05-2021', 45)
# so.find_slot()