from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import Response
import smtplib
import os
from email.message import EmailMessage

# Инициализация Flask приложения
app = Flask(__name__)

# Строка подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://webinar_db_qidc_user:aDr87iIAhDWseaDCiPwK9leFuFMLiSN7@dpg-d04946i4d50c739un2r0-a.oregon-postgres.render.com/webinar_db_qidc')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def check_auth(username, password):
    return username == os.environ.get("EXPORT_USER", "admin") and password == os.environ.get("EXPORT_PASS", "secret")

def authenticate():
    return Response(
        'Требуется авторизация', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Модель для хранения данных пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name} ({self.email})>'

# Создание таблиц в базе данных при запуске приложения
with app.app_context():
    db.create_all()  # создаём таблицы, если их ещё нет

# Функция для отправки письма на почту
def send_email(subject, body, to_email):
    SENDER_EMAIL = "kleckovkinaa@yandex.ru"
    password = "suslnpqvbmqtvvto"
    smtp_server = "smtp.yandex.ru"
    smtp_port = 587
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, password)
            message = f"Subject: {subject}\n\n{body}"
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

# Отправка подтверждения регистрации
def send_confirmation_email(email, first_name):
    subject = "Подтверждение регистрации на вебинар"
    body = f"Здравствуйте, {first_name}!\nВы успешно зарегистрировались на вебинар.\n📅Ссылку-приглашение вышлем 3 мая\n📚Больше полезной информации по подготовке к ЕГЭ по информатике в моем Telegram-канале.\n 👉 https://t.me/ege_infa_astpva \n\nДо встречи на вебинаре!"
    send_email(subject, body, email)



# Главная страница и форма регистрации
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        # Добавляем пользователя в базу данных
        new_user = User(first_name=first_name, last_name=last_name, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Отправляем подтверждение и планируем письмо со ссылкой
        send_confirmation_email(email, first_name)
        

        # Возвращаем ту же страницу с сообщением об успехе
        return render_template('index.html', success=True)

    return render_template('index.html')

@app.route('/export')
@requires_auth
def export_data():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        })
    return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
