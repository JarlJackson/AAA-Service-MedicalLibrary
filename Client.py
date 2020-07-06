# =======================================================================
# SCC.363 Security and Risk Coursework 1
# Client File - Allows the user to sign up/login to the system. Also 
# allows the user to create, read, update and delete database files
# based on their permissions.
# =======================================================================
import socket
import PassStrength
from cryptography.fernet import Fernet

username = ""
password = ""


# =======================================================================
# Client main function - requests the user sign in / sign up for an 
# account. Checks password strength and username validity. Creates a 
# connection with the server and passes encrypted username/password to 
# be verified with the database. Finally calls a get operation function.
# =======================================================================
def clientMain():
    global username
    global password

    print("==========================================")
    print("| Welcome to the medical facility system |")
    print("==========================================")

    while True:
        while not checkUsername():
            pass
        username = encryptMessage(username)
        sendMessage("EMAIL ", username)

        while not checkPassword():
            pass
        password = encryptMessage(password)
        response = sendMessage("PASS ", password)

        if not response == "Incorrect Password":
            while True:
                if oneTimePass():
                    print("Pass Correct")
                    break
                else:
                    print("Pass Incorrect - Sending new one time pass")

            if "Registered" in response:
                if not registerUser():
                    break
            while True:
                response = sendMessage("GP ", "")
                print(response)
                if response:
                    getOperation(response)
                else:
                    break


# =======================================================================
# Get operation function - Lists the various options that are open to
# the user and requests an input of the type of operation they wish
# to perform. Send the request to the server.
# @param response - string list of all options available to user
# =======================================================================
def getOperation(response):
    message = ""
    while True:
        print("==========================================")
        print("|       What would you like to do?       |")
        print("==========================================")
        options = response.split("/")
        i = 1
        for item in options:
            if item:
                print(str(i) + ". " + item)
                i += 1
        operation = input("> ")

        try:
            operation = options[int(operation) - 1]
        except:
            pass
        if operation.upper() in (item.upper() for item in options):
            break
        else:
            print("Invalid operation, please select one of the above options")
    print("==========================================")
    print("|          Checking credentials          |")
    print("==========================================")
    if "VIEW" in operation.upper():
        message = ""
        if operation == "View all health records":
            while True:
                print("=================================================")
                print("|         Enter the pcn of the patient          |")
                print("=================================================")
                try:
                    message = message + input("> ")
                    test = int(message)
                    break
                except ValueError:
                    print("That is not a valid PCN")
            message = encryptMessage(message)
    elif "UPDATE" in operation.upper() or "ADD" in operation.upper():
        if "PATIENT" in operation.upper():
            if operation == "Update any patient details":
                while True:
                    print("=================================================")
                    print("| Enter the ID of the record you want to update |")
                    print("=================================================")
                    try:
                        message = message + input("> ")
                        test = int(message)
                        break
                    except ValueError:
                        print("That is not a valid ID")
            print("=================================================")
            print("|           Enter the new first name            |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|            Enter the new surname              |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|         Enter the new street number           |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|             Enter the new address             |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|           Enter the new postcode              |")
            print("=================================================")
            message = message + "/" + input("> ")
            while True:
                print("=================================================")
                print("|          Enter the new phone number           |")
                print("=================================================")
                try:
                    tempInput = input("> ")
                    test = int(tempInput)
                    message = message + "/" + tempInput
                    break
                except ValueError:
                    print("That is not a valid phone number")
            message = encryptMessage(message)

        elif "STAFF" in operation.upper():
            while True:
                print("=================================================")
                print("| Enter the ID of the record you want to update |")
                print("=================================================")
                try:
                    message = input("> ")
                    test = int(message)
                    break
                except ValueError:
                    print("That is not a valid ID")
            print("=================================================")
            print("|           Enter the new first name            |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|            Enter the new surname              |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|         Enter the new street number           |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|           Enter the new postcode              |")
            print("=================================================")
            message = message + "/" + input("> ")
            while True:
                print("=================================================")
                print("|          Enter the new phone number           |")
                print("=================================================")
                try:
                    tempInput = input("> ")
                    test = int(tempInput)
                    message = message + "/" + tempInput
                    break
                except ValueError:
                    print("That is not a valid phone number")
            while True:
                print("=================================================")
                print("|             Enter the new salary              |")
                print("=================================================")
                try:
                    tempInput = input("> ")
                    test = float(message)
                    message = message + "/" + tempInput
                    break
                except ValueError:
                    print("That is not a valid currency")
            message = encryptMessage(message)

        elif "HEALTH" in operation.upper():
            while True:
                print("=====================================================")
                print("| Enter the patient number you want to perscribe to |")
                print("=====================================================")
                try:
                    message = message + input("> ")
                    test = int(message)
                    break
                except ValueError:
                    print("That is not a valid ID")
            print("=================================================")
            print("|               Enter the ailment               |")
            print("=================================================")
            message = message + "/" + input("> ")
            print("=================================================")
            print("|             Enter the treatment               |")
            print("=================================================")
            message = message + "/" + input("> ")
            message = encryptMessage(message)

    elif "DELETE" in operation.upper():
        while True:
            print("=================================================")
            print("| Enter the ID of the record you want to delete |")
            print("=================================================")
            try:
                message = input("> ")
                test = int(message)
                message = encryptMessage(message)
                break
            except ValueError:
                print("That is not a valid ID")
    sendMessage(operation.replace(" ", "").upper() + " ", message)


# =======================================================================
# Send message function - Send a message to the server and gets a
# response.
# @param function - string representing the function you want the server
# to provide.
# @param message - string of the information the server needs to perform
# to function. send an empty string if no information is required.
# @return response - decoded string reponse from the server.
# =======================================================================
def sendMessage(function, message):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((socket.gethostname(), 8080))
        code = bytearray(function, "utf-8")
        code.extend(message)
        client.send(code)
        clientresponse = client.recv(4096)
        client.close()
        response = clientresponse.decode("utf-8")
        if "/" in response:
            return response
        else:
            print("==========================================")
            print("|   " + response)
            print("==========================================")
            return response
    except socket.timeout:
        print("Error occurred. Please try again later.")


# =======================================================================
# Encrypt message function - generates a key and shares it with the 
# server to decrypt the message.
# @param message - a string you wish to encrypt.
# @return encryptedMessage - the encrypted message using a key.
# =======================================================================
def encryptMessage(message):
    key = Fernet.generate_key()
    encodedMessage = message.encode()
    fk = Fernet(key)
    encryptedMessage = fk.encrypt(encodedMessage)
    file = open('key.key', 'wb')
    file.write(key)
    file.close()
    return encryptedMessage


# =======================================================================
# Check username function - checks the username that was entered 
# follows the right format for an email address.
# @ return boolean - returns true if the input is email format, or 
# returns false if it isn't
# =======================================================================
def checkUsername():
    global username
    print("Please enter your email:")
    username = input("> ")
    if PassStrength.isValidUsername(username):
        return True
    else:
        print("=========================================")
        print("This is not an email. Please try again.")
        print("=========================================")
        return False


# =======================================================================
# Check password function - checks the password that was entered 
# follows the right format for a password.
# @ return boolean - returns true if the input is correct password
# format, or returns false if it isn't
# =======================================================================
def checkPassword():
    global password
    print("Please enter your password")
    print("Passwords must be 8 characters, contain 1 capital letter, 1 symbol, and 1 number")
    password = input("> ")
    if PassStrength.isValidPassword(password):
        return True
    else:
        print("=========================================")
        print("This is not an acceptable password. Please try again.")
        print("=========================================")
        return False


# =======================================================================
# One time pass function - requests the user input the one time password
# that was generated be input into the system for two factor 
# authentication.
# =======================================================================
def oneTimePass():
    while True:
        sendMessage("ONETIME CONFIRM", "")
        print("=========================================")
        print("Enter the passcode sent to your email")
        print("=========================================")
        passcode = input("> ")
        if sendMessage("ONETIME ", bytes(passcode, "utf-8")) == "Accepted":
            return True
        else:
            return False


def registerUser():
    while True:
        print("What are you registering as?")
        print("1. Patient")
        print("2. Staff")
        regChoice = input("> ")
        if regChoice.upper() == "PATIENT" or regChoice == "1":
            choice = "PCN"
            break
        elif regChoice.upper() == "STAFF" or regChoice == "2":
            choice = "Staff-number"
            break
        else:
            print("Invalid selection")
            sendMessage("DELETE")
    while True:
        print("Enter your %s: " % choice)
        num = input("> ")
        try:
            test = int(num)
            break
        except:
            print("Invalid %s" % choice)

    num = encryptMessage(num)
    response = sendMessage(choice + " ", num)
    if "contact" in response:
        sendMessage("DELETEACCOUNT ", "")
        return False
    else:
        return True


clientMain()
