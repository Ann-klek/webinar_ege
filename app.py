from flask import Flask, render_template, request, redirect
from email_utils import send_confirmation_email, schedule_webinar_email
import csv

app = Flask(__name__)
DATA_FILE = 'data.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        with open(DATA_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([first_name, last_name, email])

        send_confirmation_email(email, first_name)
        # schedule_webinar_email(email, first_name)

        return redirect('/')
    return render_template('index.html')

if __name__ == '__main__':
    from scheduler import scheduler
    scheduler.start()
    app.run(debug=True)
