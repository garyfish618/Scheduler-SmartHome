import threading
import logging
import json
import os
from datetime import date
import schedule
from flask import Flask, request, Response



#Setup Logger
logging.basicConfig(format='%(asctime)s %(message)s', filename='Scheduler.log', filemode='w', level=logging.DEBUG)

#New schedules to be registered go in this Queue
schedule_queue = []
schedules = {}
app = Flask(__name__)        
lock = threading.Lock()
persistence_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '/schedules')

class Scheduler (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    
    def run(self):
        start_schedule_loop()

def start_schedule_loop():
    logging.debug("Starting schedule loop")
    schedule_counter = 0
    while True:
        schedule.run_pending()
        
        with lock:
            if schedule_queue:
                while schedule_queue:
                    msg = schedule_queue.pop(0)
                    logging.debug("Creating new job")
                    tod = msg.hour + ":" + msg.minute
                    #Export schedule object for persistence.
                    file_number = str(schedule_counter).zfill(2)
                    filename = 'schedule-'  + file_number
                    clean_msg = dict((k, msg[k]) for k in ('days_of_week', 'json_response', 'biweekly', 'hour', 'minute')) # Removing any extra fields on msg to clean it up
                    with open(os.path.join(persistence_directory, filename + ".json"), 'w') as outfile:
                        json.dump(clean_msg, outfile)

                    schedule_counter += 1
                    
                    for day in clean_msg['days_of_week']:
                        jobs = []                       
                        if day == 'monday':
                            job = schedule.every().monday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])
                        
                        elif day == 'tuesday':
                            job = schedule.every().tuesday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])

                        elif day == 'wednesday':
                            job = schedule.every().wednesday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])

                        elif day == 'thursday':
                            job = schedule.every().thursday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])

                        elif day == 'friday':
                            job = schedule.every().friday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])

                        elif day == 'saturday':
                            job = schedule.every().saturday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])

                        elif day == 'sunday':
                            job = schedule.every().sunday.at(tod).do(send_json, clean_msg['json_response'], clean_msg['biweekly'])

                        jobs.append(job)

                    schedules[filename] = jobs

        
def send_json(json_response, biweekly, host, port):
    todays_date = date.today().strftime("%d")


    if not biweekly or int(todays_date) % 2 == 0:
        #Fire HTTP request
        pass


def start_web_server():
    port = '5001'
    logging.info('Listening for schedule requests on port %s', port)
    app.run('0.0.0.0', port=port, debug=False)
    
@app.route('/schedule/', methods=['POST'])
def schedule_data():
    if request.method == 'POST':
        #Check if it is a valid schedule object
        if request.form.keys() >= {"days_of_week", 'json_response', 'biweekly', 'hour', 'minute'}:
            with lock:
                schedule_queue.append(request.form)
                logging.debug(" Received message: %s", json.dumps(request.form))

            return Response(status=201)
        return Response(status=404)


schedule_thread = Scheduler("SCHEDULER")
schedule_thread.start()
logging.info("%s Starting Schedule Listener...")
start_web_server()