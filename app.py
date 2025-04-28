from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alarms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Alarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(64), nullable=False)
    event_type = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_first_request
def init_db():
    db.create_all()

@app.route('/')
def index():
    logs = Alarm.query.order_by(Alarm.timestamp.desc()).all()
    return render_template_string('''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AlarmCloud Log Panel</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
        rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-4">
    <h1 class="mb-4">🚨 Alarm Logları</h1>
    <table class="table table-striped">
      <thead class="table-dark">
        <tr><th>#</th><th>Account No</th><th>Olay Türü</th><th>Zaman</th></tr>
      </thead><tbody>
        {% for a in logs %}
        <tr>
          <td>{{ a.id }}</td><td>{{ a.account_no }}</td>
          <td>{{ a.event_type }}</td>
          <td>{{ a.timestamp.strftime("%Y-%m-%d %H:%M:%S") }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <hr>
    <h4>🔄 Test İçin Yeni Kayıt Ekle</h4>
    <form method="post" action="{{ url_for('add') }}" class="row g-2">
      <div class="col-auto"><input name="account_no" class="form-control" placeholder="Account No" required></div>
      <div class="col-auto"><input name="event_type" class="form-control" placeholder="Event Type" required></div>
      <div class="col-auto"><button class="btn btn-primary">Ekle</button></div>
    </form>
  </div>
</body>
</html>
''', logs=logs)

@app.route('/add', methods=['POST'])
def add():
    a = Alarm(account_no=request.form['account_no'],
              event_type=request.form['event_type'])
    db.session.add(a)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
