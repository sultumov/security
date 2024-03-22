from flask import Flask, render_template, request, redirect, url_for, session, send_file
import datetime
import time
from main import authenticate_user
from main import registration_user
from main import retrieve_password
from main import increment_login_attempts
from main import log_audit_event
from main import getaudit
from main import getusersinfo
from main import export_data_to_csv
from main import clear_database
from main import search_audit_log
from main import search_users
from main import search_audit_log

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        x = authenticate_user(username, password)
        if x == 1:
            session['username'] = username
            log_audit_event(username, "авторизован")
            return redirect(url_for('dashboard'))
        elif x == 4:
            session['username'] = username
            log_audit_event(username, "авторизован с правами")
            return redirect(url_for('admindashboard'))
        elif x == 3:
            z = increment_login_attempts(username)
            if z == 0:
                x = authenticate_user(username, password)
                if x == 1:
                    session['username'] = username
                    log_audit_event(username, "авторизован")
                    return redirect(url_for('dashboard'))
                elif x == 4:
                    session['username'] = username
                    log_audit_event(username, "авторизован с правами")
                    return redirect(url_for('admindashboard'))
            elif z == 1:
                error = 'Пользователь заблокирован на 30 секунд.'
                log_audit_event(username, "пользователь заблокирован на 30 секунд")

                return render_template('login.html', error=error, unlock_time=datetime.datetime.now() + datetime.timedelta(seconds=30))

            return render_template('login.html')
        elif x == 2:
            error = 'Неверный пароль'
            log_audit_event(username, "неверный пароль")
            z = increment_login_attempts(username)
            if z == 1:
                error = 'Пользователь заблокирован на 30 секунд.'
               ##### content()
                log_audit_event(username, "пользователь заблокирован на 30 секунд")
                return render_template('login.html', error=error,
                                       unlock_time=datetime.datetime.now() + datetime.timedelta(seconds=30))
            return render_template('login.html', error=error)
    return render_template('login.html')


def countdown(seconds):
    while seconds > 0:
        time.sleep(1)
        seconds -= 1

@app.route('/start_countdown')
def start_countdown():
    countdown(10)
    return "Complete"

@app.route('/registration',  methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        x = registration_user(username)
        if x == '3':
            error = 'Идентификатор занят'
            return render_template('registration.html', error=error)

        else:
            session['username'] = username
            log_audit_event(username, "пользователь зарегистрирован")
            return redirect(url_for('newdashboard'))


    return render_template('registration.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))


@app.route('/admindashboard', methods=['GET', 'POST'])
def admindashboard():
    if 'username' in session:
        if request.method == 'POST':
            query = request.form.get('query')
            if query:
                # Выполнить поиск в базе данных на основе введенного запроса
                data = search_audit_log(query)
            else:
                # Если запрос пустой, отобразить все записи из audit_log
                data = getaudit()
        else:
            # Если запрос GET, отобразить все записи из audit_log
            data = getaudit()

        return render_template('admindashboard.html', username=session['username'], data=data)
    else:
        return redirect(url_for('login'))


@app.route('/newdashboard')
def newdashboard():
    if 'username' in session:
        password = retrieve_password(session['username'])
        return render_template('newdashboard.html', username=session['username'], password=password)
    else:
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    log_audit_event(session['username'], "вышел")
    #Удаляем имя пользователя из сеанса
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'username' in session:
        if request.method == 'POST':
            query = request.form.get('query')
            if query:
                # Выполнить поиск в базе данных на основе введенного запроса
                data = search_users(query)
            else:
                # Если запрос пустой, отобразить все записи из audit_log
                data = getusersinfo()
        else:
            data = getusersinfo()
        return render_template('users.html', username=session['username'], data=data)
    else:
        return redirect(url_for('login'))

@app.route('/download', methods=['GET'])
def download():
    export_data_to_csv()  # Выгружаем данные из базы данных в CSV файл
    # clear_database()      # Очищаем базу данных

    # Отправляем файл пользователю для скачивания
    return send_file('exported_data.csv', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
