# -*- coding: utf-8 -*-
import secrets
import string
import json
import os
import base64

import tkinter as tk
from tkinter import messagebox

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#ФУНКЦИИ---------------------------------------------------------------------------------------------------------------------------------------------------------------

# функция генерации ключа шифрования

def generate_key(mas_pass, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(mas_pass.encode()))
    return Fernet(key)


# функция файла соли

def get_cipher():
    master_pass = ms_entry.get()
    if not master_pass:
        info_label.config(text="Password cannot be empty!")
        return
    if not os.path.exists('salt.bin'): # проверяем соль
        salt = os.urandom(16) # генерация 
        with open('salt.bin', "wb") as f:
            f.write(salt)
    else:
        with open('salt.bin', "rb") as f: # если есть то просто читаем
            salt = f.read()
    
    cipher = generate_key(master_pass, salt)
    data = load_file(cipher)

    # Если data вернула None (ошибка расшифровки), то пароль неверный.
    if data is None:
        messagebox.showerror("Error!", "Invalid Master Password!")
        return

    messagebox.showinfo("Success!", "Access Granted!")

    main_choice(data, cipher)
    return

def main_choice(data, cipher):
    choise = tk.Toplevel(window)
    choise.title("Keyo")
    choise.geometry("1200x800") 

    choise_label = tk.Label(choise, text = "Do you want to add a new one, recall an existing one or exit?")
    

    add_button = tk.Button(choise, text = "Add", command = lambda: messagebox.showinfo("Info", "Add function coming soon!"))
    recall_button = tk.Button(choise, text = "Recall", command = lambda: get_password(data, choise))
    exit_button = tk.Button(choise, text = "Exit", command = choise.destroy)

    choise_label.pack(pady = 10)
    add_button.pack(pady = 10)
    recall_button.pack(pady = 10)
    exit_button.pack(pady = 10)

# запуск файла

def load_file(cipher):
    if not os.path.exists('data.json'): 
        return []
    try:
        with open('data.json', 'rb') as f:
            encr_data = f.read()
            decr_data = cipher.decrypt(encr_data).decode()
            return json.loads(decr_data)
    except Exception as e:
        # ИСПРАВЛЕНО: Возвращаем None при ошибке, чтобы функция get_cipher поняла, что пароль не подошел
        return None 


# функция записывает в файл

def write_to_file(data, cipher):
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    encr_data = cipher.encrypt(json_str.encode())
    try:
        with open('data.json', 'wb') as f:
            f.write(encr_data)
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

    write_to_file(data, cipher)


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
    write_to_file(data, cipher)


# генерация пароля

def gen_pass(target_label):
    l = 12
    chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        npass = "".join(secrets.choice(chars) for _ in range(l))
        if any(c.islower() for c in npass) and any(c.isdigit() for c in npass) and any(c.isupper() for c in npass) and any(c in string.punctuation for c in npass):
            target_label.config(text = npass)
            return npass


# получение пароля

def get_password(data, choise):
    choise.destroy()
    get_pass = tk.Toplevel(window)
    get_pass.title("Keyo")
    get_pass.geometry("1200x800") 
    
    # ИСПРАВЛЕНО: Временно привязали к заглушке
    add_button = tk.Button(get_pass, text = "Add", command = lambda: messagebox.showinfo("Info", "Add function coming soon!"))
    get_label = tk.Label(get_pass, text = "")
    listbox = tk.Listbox(get_pass)
    
    # ИСПРАВЛЕНО: Привязали кнопку Recall к твоей же функции show_selected, которую ты написал ниже!
    recall = tk.Button(get_pass, text = "Recall", command = lambda: show_selected(data, listbox))

    if not data: # Проверка: если список пустой
        get_label.config(text = "You don't have any passwords. Would you like to add a new one?")
        
    for i in data:
        listbox.insert(tk.END, i['service'])

    add_button.pack(pady = 10)
    get_label.pack(pady = 10)
    listbox.pack(pady = 10)
    recall.pack(pady = 10)

    # ИСПРАВЛЕНО: Убран старый консольный блок try-except с input(), 
    # так как теперь выбор происходит через Listbox и кнопку Recall на экране.
    
    get_pass.mainloop() # ИСПРАВЛЕНО: Добавлен mainloop для окна get_pass, чтобы оно не закрывалось сразу


def show_selected(test_data, listbox):
    selected_index = listbox.curselection() 
    if selected_index:
        idx = selected_index[0]
        account = test_data[idx]
        info = f"Login: {account['login']}\nPassword: {account['pass']}"
        messagebox.showinfo("Success!", info)
        


def success():
    gen = tk.Tk()
    gen.title("Keyo")
    gen.geometry("450x250") 

    test_data = [
    {"service": "Google", "login": "user@gmail.com", "pass": "G123"},
    {"service": "Yandex", "login": "user@ya.ru", "pass": "Y456"},
    {"service": "GitHub", "login": "git_user", "pass": "Git789"}
]

    listbox = tk.Listbox(gen)
    label = tk.Label(gen, text = "")
    my_button = tk.Button(gen, text = "Generate!", command = lambda: gen_pass(label))
    view = tk.Button(gen, text = "view", command = lambda: show_selected(test_data, listbox))
    
    
    for i in test_data:
        listbox.insert(tk.END, i['service'])

    view.pack(pady = 10)
    listbox.pack(pady = 10)
    label.pack(pady = 10)
    my_button.pack(pady = 10)

    gen.mainloop()

def test_print():
    t = my_entry.get()
    if t == "1234":
        messagebox.showinfo("Success!", "Access Granted!")
        window.destroy()
        success()
        return
    messagebox.showerror("Error!", "Access Denied!")
    

# НАЧАЛО---------------------------------------------------------------------------------------------------------------------------------------------------------------

window = tk.Tk()
window.title("Keyo")
window.geometry("1200x800") 

info_label = tk.Label(window, text = "")
ms_entry = tk.Entry(window, show = '*')
check_button = tk.Button(window, text="Enter", command = get_cipher)

if not os.path.exists('salt.bin'):
    info_label.config(text = "Hello! It looks like you're a new user. Our program relies on your master password. Please create one and enter it in this window. The program won't work without it, so please remember it.")
else:
    info_label.config(text = "Nice to see you again, please enter your master password.")

info_label.pack(pady = 10)
ms_entry.pack(pady = 10)
check_button.pack(pady = 10)

window.mainloop()
