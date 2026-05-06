print("Sup, I'm your password manager. Choose the service whose password you need:")
serv_pass = {'Discord': 'nya<3', 'Gmail': 'gfhjkm12', 'Telegram': '_6J'}
j = 1
for i in serv_pass:
    key = list(serv_pass.keys())[j - 1]
    print(j, ') ', key, sep = "")
    j += 1
request = int(input())
value = list(serv_pass.values())[request - 1]
print(value)
