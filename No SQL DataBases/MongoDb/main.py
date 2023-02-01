from SRC.SalesAdmin import SA
from SRC.User import user


print("=====Welcome to Wakanda=====")

sign = input("are you [U]ser or [S]alesAdmin ?")
if sign == "u":
    user()

if sign == "s":
    print("welcome")
    print("would you like to initiate loyality program ?")
    sign = input("[Y]es to launch")
    if sign == 'y':
        SA()



