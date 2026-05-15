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

    if data is None: # если !не подошел мастер-пароль
        messagebox.showerror("Error!", "Invalid Master Password!")
        return

    messagebox.showinfo("Success!", "Access Granted!") # успех !доступ есть
    main_choice(data, cipher)
    return


# главное окно выбора
def main_choice(data, cipher):
    choise = tk.Toplevel(window)
    choise.grab_set()
    choise.title("Keyo")
    choise.geometry("400x300") 

    choise_label = tk.Label(choise, text = "Do you want to add a new one, recall an existing one or exit?")
    
    add_button = tk.Button(choise, text = "Add", command = lambda: add_serv_pass(data, cipher))
    recall_button = tk.Button(choise, text = "Recall", command = lambda: get_password(data, cipher, choise))
    exit_button = tk.Button(choise, text = "Exit", command = choise.destroy)

    # пакуем кнопки выбора
    choise_label.pack(pady = 10)
    add_button.pack(pady = 10)
    recall_button.pack(pady = 10)
    exit_button.pack(pady = 10)


# запуск файла и чтение
def load_file(cipher):
    if not os.path.exists('data.json'): # если файла !нет
        return []
    try:
        with open('data.json', 'rb') as f:
            encr_data = f.read()
            decr_data = cipher.decrypt(encr_data).decode()
            return json.loads(decr_data) # выдаем !базу
    except Exception as e:
        return None # если !ошибка расшифровки


# функция записывает в файл
def write_to_file(data, cipher):
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    encr_data = cipher.encrypt(json_str.encode())
    try:
        with open('data.json', 'wb') as f:
            f.write(encr_data)
        print("Saved!") # сохранено !в сейф
    except IOError:
        print("Error saving!") # ошибка записи
    return


# функция печатает список
def get_all_services(data):
    if not data: # если список !пуст
        return False
    print("You have a password set for these services:")
    for i, item in enumerate(data, 1):
        print(f"{i}. {item['service']}")
    print("-" * 20)
    return True


# функция обновляет логин
def add_upd(data, cipher, service_idx):
    remake = tk.Toplevel(window)
    remake.title("Keyo")
    remake.geometry("400x300")

    idx = service_idx - 1 # формула сдвига индекса
    current_login = data[idx]['login']
    name_label = tk.Label(remake, text=f"Enter new login (current: {current_login}): ")
    login_remake = tk.Entry(remake)

    def save_clicked():
        nlogin = login_remake.get() or current_login
        data[idx]['login'] = nlogin # меняем !только логин
        write_to_file(data, cipher) # !записать изменения в файл
        messagebox.showinfo("Success!", "Login updated successfully!")

    save_button = tk.Button(remake, text="OK", command=save_clicked)
    gen = tk.Button(remake, text = "Generate", command = lambda: gen_pass(data, cipher, target_label = service_idx))
    not_gen = tk.Button(remake, text = "Write", command = lambda: write_pass(data, cipher, target_label = service_idx))
    # пакуем изменение логина
    name_label.pack(pady = 5)
    login_remake.pack(pady = 5)
    save_button.pack(pady = 5)
    gen.pack(pady = 5)
    not_gen.pack(pady = 5)


# добавить новый сервис и пароль
def add_serv_pass(data, cipher):
    add_pass = tk.Toplevel(window.grab_set())
    add_pass.title("Keyo")
    add_pass.geometry("400x300")

    # выбор !как получить пароль
    gen = tk.Button(add_pass, text = "Generate", command = lambda: gen_pass(data, cipher, target_label = -1))
    not_gen = tk.Button(add_pass, text = "Write", command = lambda: write_pass(data, cipher, target_label = -1))
    
    gen.pack(pady=5)
    not_gen.pack(pady=5)


# ручной ввод или смена пароля
def write_pass(data, cipher, target_label):
    write = tk.Toplevel(window.grab_set())
    write.title("Keyo - Manual Write")
    write.geometry("400x300")  

    # виджеты для !обоих режимов
    pass_label = tk.Label(write, text="Write password")
    pass_entry = tk.Entry(write, show='*')

    if target_label == -1: # если пишем !новый
        name_label = tk.Label(write, text="Write service")
        name_entry = tk.Entry(write)
        login_label = tk.Label(write, text="Write login")
        login_entry = tk.Entry(write)

        # пакуем !все поля
        name_label.pack(pady=5)
        name_entry.pack(pady=5)
        login_label.pack(pady=5)
        login_entry.pack(pady=5)

    # пакуем !только пароль
    pass_label.pack(pady=5)
    pass_entry.pack(pady=5)

    def save_clicked():
        if target_label == -1: # режим !создания
            nserv = name_entry.get()
            nlogin = login_entry.get()
            npass = pass_entry.get()
            
            if not nserv or not nlogin or not npass:
                messagebox.showwarning("Error!", "All fields must be filled!")
                return
                
            new_entry = {
                "service": nserv,
                "login": nlogin,
                "pass": npass
            }
            data.append(new_entry) 
            write_to_file(data, cipher) # !записать в файл

        else: # режим !перезаписи
            npass = pass_entry.get()
            if not npass:
                messagebox.showwarning("Error!", "Password cannot be empty!")
                return
                
            real_idx = target_label - 1 # формула сдвига индекса
            data[real_idx]['pass'] = npass
            write_to_file(data, cipher) # !записать изменения
        
        messagebox.showinfo("Success!", "Password saved successfully!")
        write.destroy() # !закрыть окно

    save_button = tk.Button(write, text="Save to Vault", command=save_clicked)
    save_button.pack(pady=20)


# генерация пароля
def gen_pass(data, cipher, target_label): 
    # сначала генерируем пароль в памяти
    l = 12
    chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        npass = "".join(secrets.choice(chars) for _ in range(l))
        if any(c.islower() for c in npass) and any(c.isdigit() for c in npass) and any(c.isupper() for c in npass) and any(c in string.punctuation for c in npass):
            break # нашли !сложный пароль
            
    gen_win = tk.Toplevel(window)
    gen_win.title("Keyo - Generated Password")
    gen_win.geometry("400x300")

    pass_label = tk.Label(gen_win, text=f"Generated Password: {npass}", font=("Arial", 12, "bold"))
    pass_label.pack(pady=10)
    
    name_label = tk.Label(gen_win, text="Write service")
    name_entry = tk.Entry(gen_win)
    login_label = tk.Label(gen_win, text="Write login")
    login_entry = tk.Entry(gen_win)
    
    if target_label == -1: # если надо ввести имя и логин
        name_label.pack(pady=5)
        name_entry.pack(pady=5)
        login_label.pack(pady=5)
        login_entry.pack(pady=5)

    def save_clicked():
        if target_label == -1: # режим !создания с генератором
            nserv = name_entry.get()
            nlogin = login_entry.get()
            if not nserv or not nlogin:
                messagebox.showwarning("Error!", "All fields must be filled!")
                return
            new_entry = {
                "service": nserv,
                "login": nlogin,
                "pass": npass
            }
            data.append(new_entry) 
            write_to_file(data, cipher) # !записать новый в файл
        else: # режим !перезаписи на случайный
            real_idx = target_label - 1
            data[real_idx]['pass'] = npass
            write_to_file(data, cipher) # !записать новый пароль
            
        messagebox.showinfo("Success!", "Password saved successfully!")
        gen_win.destroy() 

    save_button = tk.Button(gen_win, text="Save to Vault", command=save_clicked)
    save_button.pack(pady=20)


# окно просмотра сохраненного
def get_password(data, cipher, choise):
    choise.destroy()
    get_pass = tk.Toplevel(window.grab_set())
    get_pass.title("Keyo")
    get_pass.geometry("800x600") 
    
    add_button = tk.Button(get_pass, text = "Add", command = lambda: add_serv_pass(data, cipher))
    get_label = tk.Label(get_pass, text = "")
    listbox = tk.Listbox(get_pass)
    
    recall = tk.Button(get_pass, text = "Recall", command = lambda: show_selected(data, listbox))

    def open_selected(): # запуск !изменения по клику
        selected_index = listbox.curselection()
        if selected_index:
            idx = selected_index[0]
            add_upd(data, cipher, idx + 1) # открываем !редактор
        else:
            messagebox.showwarning("Warning", "Please select a service first!")

    remake = tk.Button(get_pass, text="Edit Selected", command=open_selected)

    if not data: # если список !пуст
        get_label.config(text = "You don't have any passwords. Would you like to add a new one?")
        
    for i in data:
        listbox.insert(tk.END, i['service']) # закидываем !сервисы в список
 
    # пакуем просмотр списка
    get_label.pack(pady = 10)
    listbox.pack(pady = 10)
    add_button.pack(pady = 10)
    remake.pack(pady = 10)
    recall.pack(pady = 10)


# вытаскивает инфу о сервисе
def show_selected(data, listbox):
    selected_index = listbox.curselection() 
    if selected_index:
        idx = selected_index[0]
        account = data[idx]
        info = f"Login: {account['login']}\nPassword: {account['pass']}"
        messagebox.showinfo("Success!", info) # выдать !логин и !пароль

# НАЧАЛО---------------------------------------------------------------------------------------------------------------------------------------------------------------

window = tk.Tk()
window.title("Keyo")
window.geometry("1200x800") 

info_label = tk.Label(window, text = "")
ms_entry = tk.Entry(window, show = '*')
check_button = tk.Button(window, text="Enter", command = get_cipher)

if not os.path.exists('salt.bin'): # если юзер !новый
    info_label.config(text = "Hello! It looks like you're a new user. Our program relies on your master password. Please create one and enter it in this window. The program won't work without it, so please remember it.")
else: # если юзер !старый
    info_label.config(text = "Nice to see you again, please enter your master password.")

# пакуем окно входа
info_label.pack(pady = 10)
ms_entry.pack(pady = 10)
check_button.pack(pady = 10)

window.mainloop()
