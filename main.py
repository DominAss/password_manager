# -*- coding: utf-8 -*-
import secrets
import string
import json
import os

#ФУНКЦИИ---------------------------------------------------------------------------------------------------------------------------------------------------------------

# запуск файла

def load_file():
    if not os.path.exists('data.json'): 
        return []
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError): # ошибка чтения/формата
        return []


# функция записывает в файл

def write_to_file(data):
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Saved!")
    except IOError:
        print("Error saving!") # ошибка записи
    return


# функция печатает список

def get_all_services(data):
    if not data: # если список пуст
        return False
    print("You have a password set for these services:")
    for i, item in enumerate(data, 1):
        print(f"{i}. {item['service']}")
    print("-" * 20)
    return True


# функция добавляет/обновляет пароль

def add_upd(data, service_name, gen_req):
    if service_name == -1:
        add_serv_pass(data, gen_req)
        return
    
    idx = service_name - 1
    if idx < 0 or idx >= len(data): # проверка номера
        print("Invalid number!")
        return

    current_login = data[idx]['login']
    nlogin = input(f"Enter new login (current: {current_login}): ") or current_login

    if gen_req == '1':
        npass = input("Enter password: ")
    else:
        npass = gen_pass()

    data[idx]['login'] = nlogin
    data[idx]['pass'] = npass # Перезаписываем строку с паролем

    write_to_file(data)


# добавить новый сервис и пароль

def add_serv_pass(data, gen_req):
    nserv = input("Service: ")
    if not nserv: return
    nlogin = input("Login: ") # ввод логина
    if gen_req == '1':
        npass = input("Pass: ")
    else:
        npass = gen_pass()

    new_entry = {
    "service": nserv,
    "login": nlogin,
    "pass": npass
}
    data.append(new_entry)
    write_to_file(data)


# генерация пароля

def gen_pass():
    l = 12
    chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        npass = "".join(secrets.choice(chars) for _ in range(l))
        if any(c.islower() for c in npass) and any(c.isdigit() for c in npass) and any(c.isupper() for c in npass) and any(c in string.punctuation for c in npass):
            return npass


# получение пароля

def get_password(data):
    if not data: # Проверка: если список пустой

        print("You don't have any passwords.")
        return

    print("For which service do I need to recall the password?")

    get_all_services(data) # Вызываем твою уже готовую функцию печати списка
    
    try:
        choice = int(input("Enter number: ")) # ввод номера
        print('\n')
        idx = choice - 1 

        if idx < 0 or idx >= len(data): # если номер вне списка
            raise IndexError

        # Печатаем название и пароль
        print(f"Service: {data[idx]['service']}")
        print(f"Login: {data[idx]['login']}")
        print(f"Password: {data[idx]['pass']}")
        print('\n')

    except (ValueError, IndexError): # Более точная обработка ошибок
        print("Invalid number!")
        print('\n')


# НАЧАЛО---------------------------------------------------------------------------------------------------------------------------------------------------------------

data = load_file() # читаем файл один раз

while True:

    print("Sup, I'm your password manager. Do you want to add a new one(1), recall an existing one(2) or exit(3)?") # выбор !записать/!вспомнить
    req = input("1/2/3: ")
    print('\n')

    if req == '3':
        print("Bye!")
        break

    elif req == '2': # если !вспомнить
        get_password(data)


    if req == '1': # если пишем !новый или если добавляем в !пустой

        if not data:
            # если данных нет, сразу идем создавать новый сервис
            print("No services found. Let's add your first one!")
            print("Would you like to write it yourself(1) or have it generated for you(2)?")
            gen_req = input("1/2: ")
            add_serv_pass(data, gen_req)
        else:
            # если данные есть, показываем список и даем выбор
            get_all_services(data)

            try:
                service_name = int(input("Enter service number(or if you need new service - type '-1'): ")) # ввод числа

                print("Would you like to write it yourself(1) or have it generated for you(2)?") # сам/сгенерировать
                gen_req = input("1/2: ") # отдельная переменная, чтобы не сбить req
        
                add_upd(data, service_name, gen_req) # запуск записи
            except ValueError: # если ввели не цифру
                print("Invalid input!")
                print('\n')
