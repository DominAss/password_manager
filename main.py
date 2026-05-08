# функция печатает список
def get_all_services():
    global lines
    print("You have a password set for these services:")
    for i, service in enumerate(lines[::2], 1): 
        print(f"- {service.strip()} [{i}]")
    return

# добавить новый сервис и пароль
def add_serv_pass(gen_req):
    global lines
    nserv = input("Service: ")
    if gen_req == '1':
        npass = input("Pass: ")
    else:
        npass = gen_pass()

    lines.append(nserv + '\n')
    lines.append(npass + '\n')

    write_to_file()

# функция добавляет/обновляет пароль
def add_upd(service_name, gen_req):
    global lines
    if service_name == -1:
        add_serv_pass(gen_req)
        return
    if gen_req == '1':

        npass = input("Enter password: ")

    else:
        npass = gen_pass()
    
    service_idx = (service_name - 1) * 2 # формула индекса строк в соответствии с выбором пользователя
    lines[service_idx + 1] = npass + '\n' # Перезаписываем строку с паролем
    write_to_file()

def gen_pass():
    return "Generated123" # заглушка


# функция записывает в файл
def write_to_file():
    global lines
    with open('data.txt', 'w', encoding='utf-8') as f: # запись обратно
        f.writelines(lines)
    print("Saved!")
    return

def get_password():
    global lines
    if not lines: # Проверка: если список пустой
        print("Your list is empty!")
        return

    print("For which service do I need to remember the password?")

    get_all_services() # Вызываем твою уже готовую функцию печати списка
    
    try:
        choice = int(input("Enter number: "))
        service_idx = (choice - 1) * 2
        # Печатаем название и пароль
        print(f"Service: {lines[service_idx].strip()}")
        print(f"Password: {lines[service_idx + 1].strip()}")
    except (ValueError, IndexError): # Более точная обработка ошибок
        print("Invalid number!")

while True:
    with open('data.txt', 'a+', encoding='utf-8') as f: # юзаю a+, чтобы файл создался, если его нет
        f.seek(0) # кидаю курсор в начало для чтения
        lines = f.readlines()
    count = len(lines)

    print("Sup, I'm your password manager. Do you want to add a new one(1), recall an existing one(2) or exit(3)?") # выбор !записать/!вспомнить
    print("1/2/3")
    req = input()

    if req == '3':
        print("Bye!")
        break

    if req == '2': # если !вспомнить
        get_password()
        if count == 0: # если нечего !вспоминать
            print("It looks like you don't have any passwords. Do you want to add one?") # будем !добавлять/!не будем
            print("y/n")
            req = input()
            if req == "n": # не (исправил с "2" на "n")
                print("Bye!") # пока
                break

    if req == 'y' or req == '1': # если пишем !новый или если добавляем в !пустой

        get_all_services()

        service_name = int(input("Enter service number(or if you need new service - type '-1'): "))

        print("Would you like to write it yourself(1) or have it generated for you(2)?") # сам/сгенерировать
        print("1/2")
        gen_req = input() # отдельная переменная, чтобы не сбить req
        
         #что имеется
        # Проход по !сервисам (только названия)

        add_upd(service_name, gen_req)
