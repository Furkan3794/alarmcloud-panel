import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates', static_folder='static')
# SQLite veritabanı aynı dizinde "alarms.db" olarak tutulacak
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alarms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Alarm kaydı modeli
class AlarmRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(64), nullable=False)
    event_type = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Model tanımlandıktan hemen sonra tablo(lar)ı oluştur
with app.app_context():
    db.create_all()

# Ana sayfa: artık doğrudan templates/index.html dönecek
@app.route('/')
def index():
    return render_template('index.html')

# (İsteğe bağlı) Log kayıtlarını JSON olarak çekmek için API
@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = AlarmRecord.query.order_by(AlarmRecord.timestamp.desc()).all()
    return jsonify([
        {
            'id': a.id,
            'account_no': a.account_no,
            'event_type': a.event_type,
            'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for a in logs
    ])

# (İsteğe bağlı) Yeni log eklemek için API
@app.route('/api/logs', methods=['POST'])
def add_log():
    data = request.get_json(force=True)
    new_alarm = AlarmRecord(
        account_no=data.get('account_no'),
        event_type=data.get('event_type')
    )
    db.session.add(new_alarm)
    db.session.commit()
    return jsonify({'status':'ok'}), 201

if __name__ == '__main__':
    # Render’da PORT ortam değişkenini, lokalde 5000’i kullan
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
