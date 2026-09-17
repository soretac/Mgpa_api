import secrets
import string
import datetime

def abonnement():
    # define the alphabet
    digits = string.digits
    
    
    # fix password length
    ab_length = 4
    
    # generate a password string
    ab = ""
    for i in range(ab_length):
        ab += "".join(secrets.choice(digits))
    
    return ab



# def num_abonnement():
#     racine = abonnement()
#     dat = str(datetime.date.today())
#     print(dat)
#     d = dat[8:]
#     m = dat[5:7]               
#     ab = str(client.code_ab)+d+m+str(racine)




def PwdGenerator():
    # define the alphabet
    letters = string.ascii_letters
    digits = string.digits


    alphabet = letters + digits

    # fix password length
    pwd_length = 24

    # generate a password string
    pwd = ""
    for i in range(pwd_length):
        pwd += "".join(secrets.choice(alphabet))

    return pwd


def CodeGenerator():
    # define the alphabet
    letters = string.ascii_letters
    digits = string.digits
    alphabet = letters.upper() + digits
    # fix password length
    code_length = 4

    # generate a password string
    cod = ""
    j = 0
    while j < 4:
        for i in range(code_length):
            cod += "".join(secrets.choice(alphabet))

        cod += "".join("-")
        j = j + 1

    for i in range(code_length):
        cod += "".join(secrets.choice(alphabet))

    return cod


def SessionGenerator():
    # define the alphabet
    letters = string.ascii_letters
    digits = string.digits
    alphabet = letters.upper() + digits
    # fix password length
    code_length = 3

    # generate a password string
    cod = ""
    j = 0
    while j < 3:
        for i in range(code_length):
            cod += "".join(secrets.choice(alphabet))

        cod += "".join("-")
        j = j + 1

    for i in range(code_length):
        cod += "".join(secrets.choice(alphabet))

    return cod

