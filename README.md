# Vaccine_Cowin_Live_Scheduler_Python

This project is working as fetching the live data using API SETU' API.
This project is made for create a notification of slot availability of vaccine via an email notification. 

For Hosting This application you just need a cloud machine with basic config.
This has requirement txt file. You can simply download all required package by this file. 

virtualenv localenv -p python3
source locaelnv/bin/activate
pip install -r requirements.txt

For Running on server this project has app.json file. You can run this on Nodejs' NPM package. 
Start command :- 

sudo pm2 start app.json
sudo pm2 list 
Find the id of this by name  :: VACCINE-SCHEDULER:3001
sudo pm2 log {id}

For Create Notification Use this api 

http://{server_address}:{port}/alert/vaccine/create_alert

params = {
    "date": "08-05-2021", #Date to fetched
    "district_id": 312, #Bhopal
    "age_slot": 45, #Age slot
    "email_id": "example@gmail.com"
}

POST METHOD //

