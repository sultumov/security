import pymysql
import datetime
import csv
from getpassword import newpass
from flask import request, render_template

# Глобальная функция для установки соединения с базой данных
def connect_to_database():
    return pymysql.connect(
        host="localhost",
        port=3307,
        user="root",
        password="root",
        database="LAB2"
    )

def authenticate_user(username, password):
    try:
        # Устанавливаем соединение с базой данных
        connection = connect_to_database()
        with connection.cursor() as cursor:
            # Проверяем наличие пользователя в базе данных
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            # Закрываем соединение с базой данных
            connection.close()
            # Проверяем, заблокирован ли пользователь
            if user and user[4]:
                return 3
            elif user and user[5]:
                return 4
            elif user:
                return 1
            else:
                return 2
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса1:", err)
        return False

def registration_user(username):
    try:
        # Устанавливаем соединение с базой данных
        connection = connect_to_database()

        with connection.cursor() as cursor:
            # Проверяем наличие пользователя в базе данных
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, username)
            user = cursor.fetchone()


            # Проверяем, занят ли идентификатор
            if user:
                print("Идентификатор занят")
                return '3'

            else:
                Pass = newpass(username)
                sql_update_attempts = "INSERT INTO users (username, password) VALUES (%s, %s);"
                cursor.execute(sql_update_attempts, (username, Pass))
                connection.commit()
                return Pass

            # Закрываем соединение с базой данных
            connection.close()
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса2:", err)
        return False

def retrieve_password(username):
    try:
        # Устанавливаем соединение с базой данных
        connection = connect_to_database()

        with connection.cursor() as cursor:
            # Проверяем наличие пользователя в базе данных
            sql = "SELECT password FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()

            if result:
                password_tuple = result
                res = password_tuple[0]
                return res
            else:
                print(username)
                return False

    except pymysql.Error as err:
        print("Ошибка при выполнении запроса3:", err)
        return False

    # Закрываем соединение с базой данных
    connection.close()


def log_audit_event(username, event_description):
    try:
        # Получаем текущую дату и время
        current_datetime = datetime.datetime.now()

        connection = connect_to_database()

        with connection.cursor() as cursor:
            # Регистрируем событие в журнале аудита
            sql = "INSERT INTO audit_log (event_datetime, username, event_description) VALUES (%s, %s, %s)"
            event_data = (current_datetime, username, event_description)
            cursor.execute(sql, event_data)

        # Подтверждаем изменения в базе данных
        connection.commit()
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса5:", err)
    finally:
        # Закрываем соединение с базой данных
        connection.close()

def getaudit():
    try:
        #Получаем данные из таблицы журнала
        connection = connect_to_database()
        with connection.cursor() as cursor:
            cursor.execute("select event_datetime,username,"
                           "event_description from audit_log")
            data = cursor.fetchall()
        return data

    except pymysql.Error as err:
        print("Ошибка при выполнении запроса6:", err)


def getusersinfo():
    try:
        #Получаем данные из таблицы журнала
        connection = connect_to_database()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            data = cursor.fetchall()
        return data

    except pymysql.Error as err:
        print("Ошибка при выполнении запроса7:", err)

def increment_login_attempts(username):
    try:
        connection = connect_to_database()
        x = 0

        with connection.cursor() as cursor:
            sql_update_attempts = "UPDATE users SET login_attempts = login_attempts + 1, last_login_attempt = NOW() WHERE username = %s"
            cursor.execute(sql_update_attempts, (username,))
            connection.commit()

            sql_check_attempts = "SELECT login_attempts, last_login_attempt, unlock_time FROM users WHERE username = %s"
            cursor.execute(sql_check_attempts, (username,))
            attempts, last_attempt_time, unlock_time = cursor.fetchone()

            if attempts >= 3:
                # Если попыток >= 3, проверяем, прошло ли уже 30 секунд с момента последней попытки
                if unlock_time and unlock_time <= datetime.datetime.now():
                    # Если unlock_time не None и <= текущему времени, то разблокируем пользователя
                    sql_unlock_account = "UPDATE users SET login_attempts = 0, locked = 0, last_login_attempt = NULL, unlock_time = NULL WHERE username = %s"
                    cursor.execute(sql_unlock_account, (username,))
                    connection.commit()
                    x = 0
                else:
                    # Если не прошло 30 секунд, блокируем пользователя и записываем время разблокировки через 30 секунд
                    sql_lock_account = "UPDATE users SET locked = TRUE, unlock_time = DATE_ADD(NOW(), INTERVAL 30 SECOND) WHERE username = %s"
                    cursor.execute(sql_lock_account, (username,))
                    connection.commit()
                    x = 1

    except pymysql.Error as err:
        print("Ошибка при выполнении запроса4:", err)
    finally:
        connection.close()
        return x

def export_data_to_csv():
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            # Выполняем запрос для получения данных из базы данных
            sql_query = "SELECT * FROM audit_log"
            cursor.execute(sql_query)
            data = cursor.fetchall()

            # Записываем данные в CSV файл
            with open('exported_data.csv', 'w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow([i[0] for i in cursor.description]) # Записываем заголовки столбцов
                csv_writer.writerows(data)
            connection.commit()
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса:", err)
    finally:
        connection.close()

# Функция для очистки базы данных
def clear_database():
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            # Выполняем запрос для очистки таблицы или таблиц базы данных
            sql_query = "TRUNCATE TABLE audit_log"
            cursor.execute(sql_query)
            connection.commit()
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса:", err)
    finally:
        connection.close()

def search_audit_log(query):
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            # Измененный SQL-запрос для поиска по всем полям
            sql_query = "SELECT * FROM audit_log WHERE id LIKE %s OR event_description LIKE %s OR username LIKE %s OR event_datetime LIKE %s"
            cursor.execute(sql_query, ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
            data = cursor.fetchall()
        return data
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса:", err)
    finally:
        connection.close()

def search_users(query):
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            # Измененный SQL-запрос для поиска по всем полям
            sql_query = "SELECT * FROM users WHERE id = %s OR username LIKE %s OR locked LIKE %s OR rools LIKE %s"
            cursor.execute(sql_query, (query, '%' + query + '%', '%' + query + '%', '%' + query + '%'))

            data = cursor.fetchall()
        return data
    except pymysql.Error as err:
        print("Ошибка при выполнении запроса:", err)
    finally:
        connection.close()

