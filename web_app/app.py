from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/submit")


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'telegram_nick': request.form['telegram_nick'],
            'referrer_nick': request.form.get('referrer_nick'),
            'dob': request.form['dob'],
            'phone': request.form['phone'],
            'interview_time': request.form['interview_time']
        }

        try:
            response = requests.post(BACKEND_URL, json=data)
            response.raise_for_status()
            flash("Форма успешно отправлена!", "success")
            return redirect(url_for('success'))
        except requests.exceptions.HTTPError as errh:
            flash(f"HTTP Error: {errh}", "danger")
        except requests.exceptions.ConnectionError as errc:
            flash(f"Error Connecting: {errc}", "danger")
        except requests.exceptions.Timeout as errt:
            flash(f"Timeout Error: {errt}", "danger")
        except requests.exceptions.RequestException as err:
            flash(f"Something went wrong: {err}", "danger")

    return render_template('form.html')


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
