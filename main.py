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
        if count == 0: # если нечего !вспоминать
            print("It looks like you don't have any passwords. Do you want to add one?") # будем !добавлять/!не будем
            print("y/n")
            req = input()
            if req == "n": # не (исправил с "2" на "n")
                print("Bye!") # пока
                break

    if req == 'y' or req == '1': # если пишем !новый или если добавляем в !пустой
        print("Would you like to write it yourself(1) or have it generated for you(2)?") # сам/сгенерировать
        print("1/2")
        gen_req = input() # отдельная переменная, чтобы не сбить req
        
        print("You have a password set for these services:") #что имеется
        # Проход по !сервисам (только названия)
        for i, service in enumerate(lines[::2], 1): 
            print(f"- {service.strip()} [{i}]")

        service_name = int(input("Enter service number(or if you need new service - type '-1'): "))

        if service_name == -1:
            nserv = input("Service: ")
            npass = input("Pass: ")
            lines.append(nserv + '\n')
            lines.append(npass + '\n')

        service_idx = (service_name - 1) * 2

        if service_name != -1:
            lines[service_idx + 1] = npass + '\n' # Перезаписываем строку с паролем

        if gen_req == '1' and service_name != -1:
            npass = input("Enter password: ")
        elif gen_req == '2' and service_name != -1:
            npass = "Generated123" # тут будет логика генерации

        with open('data.txt', 'w', encoding='utf-8') as f: # запись обратно
            f.writelines(lines)
        print("Saved!")
        continue # идем на новый круг

    if count != 0: #если не !пустой
        print("You have a password set for these services:") # что имеется
        # Проход по !сервисам (только названия)
        for i, service in enumerate(lines[::2], 1): 
            print(f"- {service.strip()} [{i}]")

        print("For which service do I need to remember the password?") # на какой !сервис !добавляем/!вспоминаем
        try:
            choice = int(input())
            # Формула: индекс сервиса = (номер-1)*2, пароль — следующий за ним
            service_idx = (choice - 1) * 2
            print("Here you go:", lines[service_idx + 1].strip())
        except:
            print("Invalid number")
