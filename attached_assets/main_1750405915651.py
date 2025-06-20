from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    with open('news.json') as f:
        news = json.load(f)
    return render_template('index.html', news=news)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] == 'user@example.com' and request.form['password'] == 'password':
            session['user'] = request.form['email']
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        with open("subscribers.txt", "a") as f:
            f.write(email + "\n")
        return "Thanks for subscribing!"
    return render_template('subscribe.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
