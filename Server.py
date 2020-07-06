# =======================================================================
# SCC.363 Security and Risk Coursework 1
# Server File - Handles requests made by the client. Handles sign up
# and log in. Uses salt and has before storing in the database.
# =======================================================================
from datetime import datetime
import hashlib
import smtplib
import socket
import ssl
import uuid
import mysql.connector
import pyotp
import re
from cryptography.fernet import Fernet

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="medicalfacility"
)
mycursor = mydb.cursor()

# Global variables
hotp = pyotp.HOTP('base32secret3232')
sessionUser = ""
ip_address = ""
user_id = 0
serverResponse = "Default"
i = 0


# =======================================================================
# Server run function - Runs the server and loops over for multiple
# connections. Decryptes incoming packets before being sent to various 
# functions. The various functions in the database require a valid email
# to be stored for this session, which requires the appropriate password.
# =======================================================================
def serverRun():
    global serverResponse
    global sessionUser
    global ip_address
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((socket.gethostname(), 8080))
    server.listen(5)

    while True:
        clientsocket, addr = server.accept()
        ip_address = str(addr).split("'")[1]
        data = clientsocket.recv(4096)
        msg = data.decode("utf-8")
        print(msg)
        msgID = msg.split(" ")[0]
        print(msgID)
        message = msg.split(" ")[1]
        print(message)

        # Client enters their login - store in global variable
        if msgID == "EMAIL":
            sessionUser = str(decryptMessage(message)).split("'")[1]
            print(sessionUser)
            serverResponse = "Accepted email"

        # Client enters password - check if login or register and handle accordingly
        elif msgID == "PASS":
            plainpassword = str(decryptMessage(message)).split("'")[1]
            checkNewUser = ("SELECT email FROM accounts WHERE email = '%s'" % sessionUser)
            mycursor.execute(checkNewUser)
            if mycursor.fetchone():
                login(plainpassword)
            else:
                register(plainpassword)
                serverResponse = "Registered as " + sessionUser

        # Client enters false linking of their account
        elif msgID == "DELETEACCOUNT":
            sql = ("UPDATE audit_logs SET user_id = NULL WHERE user_id = %s" % user_id)
            mycursor.execute(sql)
            mydb.commit()
            sql = ("DELETE FROM accounts WHERE user_id = %s" % user_id)
            mycursor.execute(sql)
            mydb.commit()
            serverResponse = "User Registration Failed"
            addLog("Account deleted from the database")

        # Client requests a one time password
        elif msgID == "ONETIME":
            if message == "CONFIRM":
                genOneTime()
                serverResponse = "One Time Sent"
            else:
                if checkOneTime(message):
                    serverResponse = "Accepted"
                else:
                    serverResponse = "Denied"

        # Client requests to link their account with a patient details
        elif msgID == "PCN":
            pcn = str(decryptMessage(message)).split("'")[1]
            sql = ("SELECT pcn FROM patients WHERE pcn = %s" % pcn)
            mycursor.execute(sql)
            status = mycursor.fetchone()
            if status:
                sql = ("SELECT pcn FROM accounts WHERE pcn = %s" % pcn)
                mycursor.execute(sql)
                if mycursor.fetchone():
                    serverResponse = "Failed to link to this PCN, contact the administrator"
                else:
                    sql = ("UPDATE accounts SET pcn = %s WHERE user_id = %s" % (pcn, user_id))
                    mycursor.execute(sql)
                    sql = ("INSERT INTO account_roles (user_id, role_id) VALUES (%s, %s)")
                    values = (user_id, 4)
                    mycursor.execute(sql, values)
                    mydb.commit()
                    serverResponse = "Successfully linked to your account"
                    addLog("User has linked their account")
            else:
                serverResponse = "Couldn't find that PCN number, contact the administrator"

        # Client requests to link their account with a staff details
        elif msgID == "Staff-number":
            staffnumber = str(decryptMessage(message)).split("'")[1]
            sql = ("SELECT staff_num FROM staff WHERE staff_num = %s" % staffnumber)
            mycursor.execute(sql)
            status = mycursor.fetchone()
            if status:
                sql = ("SELECT staff_num FROM accounts WHERE staff_num = %s" % staffnumber)
                mycursor.execute(sql)
                if mycursor.fetchone():
                    serverResponse = "Failed to link to this Staff-number, contact the administrator"
                else:
                    sql = ("UPDATE accounts SET staff_num = %s WHERE user_id = %s" % (staffnumber, user_id))
                    mycursor.execute(sql)
                    sql = ("INSERT INTO account_roles (user_id, role_id) VALUES (%s, %s)")
                    values = [
                        (user_id, 3),
                        (user_id, 2)
                    ]
                    mycursor.executemany(sql, values)
                    mydb.commit()
                    serverResponse = "Successfully linked to your account"
                    addLog("User has linked their account")
            else:
                serverResponse = "Couldn't find that staff number, contact the administrator"

        # Client requests their personal list of permissions
        elif msgID == "GP":
            serverResponse = getPerm()

        # Client requests to view all patients
        elif msgID == "VIEWALLPATIENTS":
            sql = ("SELECT * FROM patients")
            mycursor.execute(sql)
            result = mycursor.fetchall()
            print(result)
            serverResponse = str(result)
            addLog("User viewed all patients")

        # Client requests to view only their own patient details
        elif msgID == "VIEWYOURPATIENTDETAILS":
            sql = ("SELECT pcn FROM accounts WHERE user_id = '%s'" % user_id)
            mycursor.execute(sql)
            result = mycursor.fetchone()
            if result is None:
                serverResponse = "Couldn't fetch your records, contact the administrator"
            else:
                sql = ("SELECT * FROM patients WHERE pcn = %s" % result)
                mycursor.execute(sql)
                result = mycursor.fetchone()
                serverResponse = str(result)
                addLog("User viewed their details")

        # Client requests to update a patient details based on their user id
        elif msgID == "UPDATEANYPATIENTDETAILS":
            print(msgID)
            details = str(decryptMessage(message)).split("'")[1].split("/")
            print(details)
            sql = ("UPDATE patients SET first_name = '%s' WHERE pcn = %s" % (details[1], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET surname = '%s' WHERE pcn = %s" % (details[2], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET street_number = '%s' WHERE pcn = %s" % (details[3], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET address = '%s' WHERE pcn = %s" % (details[4], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET postcode = '%s' WHERE pcn = %s" % (details[5], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET phone_number = '%s' WHERE pcn = %s" % (details[6], details[0]))
            mycursor.execute(sql)
            mydb.commit()
            serverResponse = "Successfully uppdated a patient"
            addLog("User updated a patients records")

        # Client requests to update their own details
        elif msgID == "UPDATEYOURPATIENTDETAILS":

            print(msgID)
            details = str(decryptMessage(message)).split("'")[1].split("/")
            print(details)
            sql = ("SELECT pcn FROM accounts WHERE user_id = %s" % user_id)
            mycursor.execute(sql)
            result = mycursor.fetchone()[0]
            print(result)
            print(details[1])
            sql = ("UPDATE patients SET first_name = '%s' WHERE pcn = %s" % (details[1], result))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET surname = '%s' WHERE pcn = %s" % (details[2], result))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET street_number = '%s' WHERE pcn = %s" % (details[3], result))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET address = '%s' WHERE pcn = %s" % (details[4], result))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET postcode = '%s' WHERE pcn = %s" % (details[5], result))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET phone_number = '%s' WHERE pcn = %s" % (details[6], result))
            mycursor.execute(sql)
            mydb.commit()
            serverResponse = "Successfully uppdated your details"
            addLog("User updated a patients records")

        # Client requests to delete a patient based on a given user id
        elif msgID == "DELETEPATIENT":
            patientID = str(decryptMessage(message)).split("'")[1]
            print("Deleting patient " + patientID + " from database")
            sql = ("DELETE FROM patients WHERE pcn = '%s'" % patientID)
            mycursor.execute(sql)
            mydb.commit()
            serverResponse = "Successfully deleted a patient"
            addLog("User deleted a patients records")

        # Client requests to view all the health records of a given patient
        elif msgID == "VIEWALLHEALTHRECORDS":
            print(msgID)
            details = str(decryptMessage(message)).split("'")[1].split("/")
            print(details[0])
            sql = ("SELECT * FROM health JOIN patients ON patients.pcn = health.pcn WHERE patients.pcn = %s" % details[
                0])
            mycursor.execute(sql)
            result = mycursor.fetchall()
            if result:
                serverResponse = str(result)
                addLog("User viewed health records")
            else:
                serverResponse = "Couldn't find your records, contact the administrator"

        # Client requests to view their own health records
        elif msgID == "VIEWYOURHEALTHRECORDS":
            sql = ("SELECT pcn FROM accounts WHERE user_id = %s" % user_id)
            mycursor.execute(sql)
            result = mycursor.fetchone()
            if result is None:
                serverResponse = "Couldn't fetch your records, contact the administrator"
            else:
                sql = ("SELECT * FROM health WHERE pcn = %s" % result)
                mycursor.execute(sql)
                result = mycursor.fetchall()
                serverResponse = str(result)
                addLog("User Viewed their health records")

        # Client requests to add a health record associated with a patient
        elif msgID == "ADDAHEALTHRECORD":
            print(msgID)
            details = str(decryptMessage(message)).split("'")[1].split("/")
            print(details)
            gettime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = (
                "INSERT INTO health (health_record, pcn, ailment, treatment, created_at) VALUES (%s, %s, %s, %s, %s)")
            val = (0, details[0], details[1], details[2], gettime)
            mycursor.execute(sql, val)
            mydb.commit()
            serverResponse = "Health record successfully added"
            addLog("User added a health record")

        # Client requests to view their own staff details
        elif msgID == "VIEWASTAFFMEMBER":
            print(msgID)
            details = str(decryptMessage(message)).split("'")[1].split("/")
            print(details)
            sql = ("SELECT * FROM staff WHERE user_id = '%s'" % details[0])
            mycursor.execute(sql)
            result = mycursor.fetchall()
            if result:
                serverResponse = str(result)
            else:
                serverResponse = "Couldn't find that member of staff"

        # Client requests to update a member of staff
        elif msgID == "UPDATESTAFF":
            print(msgID)
            details = str(decryptMessage(message)).split("'")[1].split("/")
            print(details)
            sql = ("UPDATE patients SET first_name = '%s' WHERE staff_num = %s" % (details[1], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET surname = '%s' WHERE staff_num = %s" % (details[2], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET street_number = '%s' WHERE staff_num = %s" % (details[3], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET address = '%s' WHERE staff_num = %s" % (details[4], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET postcode = '%s' WHERE staff_num = %s" % (details[5], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET phone_number = '%s' WHERE staff_num = %s" % (details[6], details[0]))
            mycursor.execute(sql)
            sql = ("UPDATE patients SET salary = '%s' WHERE staff_num = %s" % (details[5], details[0]))
            mycursor.execute(sql)
            mydb.commit()
            serverResponse = "Successfully uppdated a patient"

        # Client requests to delete a member of staff
        elif msgID == "DELETESTAFF":
            staffNum = str(decryptMessage(message)).split("'")[1]
            print("Deleting staff " + staffNum + " from database")
            sql = ("DELET FROM staff WHERE staff_num = %s" % staffNum)
            mycursor.execute(sql)
            mydb.commit()
            serverResponse = "Successfully deleted a staff record"
            addLog("User deleted a staff")

        # Client requests to view the audit logs
        elif msgID == "VIEWAUDITLOGS":
            sql = ("SELECT * FROM audit_logs")
            mycursor.execute(sql)
            result = mycursor.fetchall()
            serverResponse = str(result)
            addLog("User viewed the audoit logs")

        clientsocket.send(bytes(serverResponse, "utf-8"))
        serverResponse = ""
        clientsocket.close()


# =======================================================================
# Login function - Retrieves the users salt and hashed password from
# the database. We salt and hash the plain password to check against
# the stored password in the database.
# @param password - the plain text password passed from server run.
# =======================================================================
def login(password):
    global serverResponse
    global user_id
    getHashpassword = ("SELECT password FROM accounts WHERE email = '%s'" % sessionUser)
    mycursor.execute(getHashpassword)
    hashedpassword = str(mycursor.fetchone()[0])
    getSalt = ("SELECT salt FROM accounts WHERE email = '%s'" % sessionUser)
    mycursor.execute(getSalt)
    salt = str(mycursor.fetchone()[0])
    newhashedpassword = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
    sql = ("SELECT user_id FROM accounts WHERE email = '%s'" % sessionUser)
    mycursor.execute(sql)
    user_id = str(mycursor.fetchone()[0])
    addLog("User has logged into the system")
    print("Password: " + password)
    print("Salt===========" + salt)
    print("hashedpass===========" + newhashedpassword)
    print("oldhashpass===========" + hashedpassword)
    if newhashedpassword == hashedpassword:
        serverResponse = "Logged in as " + sessionUser
    else:
        serverResponse = "Incorrect Password"


# =======================================================================
# Register function - registers new users that attempt to log in to the
# system. New users are given the default role of non-medical staff, 
# which has no permissions associated with it, and must be upraded
# by the regulator of the system.
# @param password - the plain text password passed from server run.
# =======================================================================
def register(password):
    global user_id
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
    print("This is the password: " + password)
    print("This is the salt: " + salt)
    print("This is the hashed: " + hashed_password)
    regUser = (
        "INSERT INTO accounts (user_id, email, salt, password, pcn, staff_num) VALUES (%s, %s, %s, %s, NULL, NULL)")
    userData = (0, sessionUser, salt, hashed_password)
    mycursor.execute(regUser, userData)
    mydb.commit()
    getUserID = ("SELECT user_id FROM accounts WHERE email = '%s'" % sessionUser)
    mycursor.execute(getUserID)
    user_id = str(mycursor.fetchone()[0])
    addRole = ("INSERT INTO account_roles (user_id, role_id) VALUES (%s, %s)")
    rolevalues = (user_id, 5)
    mycursor.execute(addRole, rolevalues)
    mydb.commit()
    addLog("A new user has registered into the system")
    print("New user registered")


# =======================================================================
# Add log function - adds an audit log for later review for activities
# on the database. Adds the users id, ip address, description of the
# operation, and the operation time.
# @param description - a description of the operation that was performed
# =======================================================================
def addLog(description):
    gettime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    getID = ("SELECT user_id FROM accounts WHERE email = '%s';" % sessionUser)
    mycursor.execute(getID)
    user_id = removePunc(str(mycursor.fetchone()))
    if user_id:
        log = (
            "INSERT INTO audit_logs (log_id, user_id, ip_address, description, operation_time) VALUES (%s, %s, %s, %s, %s)")
        logData = (0, user_id, ip_address, description, gettime)
    else:
        log = (
            "INSERT INTO audit_logs (log_id, user_id, ip_address, description, operation_time) VALUES (%s, NULL, %s, %s, %s)")
        logData = (0, ip_address, description, gettime)
    mycursor.execute(log, logData)
    mydb.commit()
    print("Added to log")


# =======================================================================
# Decrypt message function - decrypts the incoming packets based on a 
# stored key. Uses Fernet's cryptography python library
# @param message - the encrypted packet.
# @return decryptedMessage - the plain text decrypted message
# =======================================================================
def decryptMessage(message):
    file = open('key.key', 'rb')
    key = file.read()
    file.close()
    fk = Fernet(key)
    encodedMessage = message.encode("utf-8")
    decryptedMessage = fk.decrypt(encodedMessage)
    return decryptedMessage


# =======================================================================
# Remove Punctutation function - loops over a message and remove the 
# list of punctuations below. Useful when multiple different
# punctuations are present in a string in different places so split() is
# inefficient.
# @param message - string message that will be parsed of punctuation
# @return result - string message free of punctuation
# =======================================================================
def removePunc(message):
    punctuations = '''!()-[]{};:'"\, <>/?@#$%^&*_~'''
    result = ""
    for char in message:
        if char not in punctuations:
            result = result + char
    return result


# =======================================================================
# Gen One Time fucntion - generates a one time password and sends it to
# the users' email address for them to verify who they are using two
# factor authentication.
# =======================================================================
def genOneTime():
    global i
    print("Counter: ", i)
    passcode = hotp.at(i)
    print("One Time: " + passcode)
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "DrGLancaster@gmail.com"
    print("USERNAME: " + sessionUser)
    reciever_email = sessionUser
    password = "WastemanGarethGang69"
    message = 'Subject: {}\n\n{}'.format("DrGLancaster Registration One Time Passcode", """
    Welcome to Doctor GLancaster Surgery
    
    Thank you for using with our service
    
    Please enter this code into the site:
    """ + passcode)
    context = ssl.create_default_context()
    print("Sending")
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, reciever_email, message)
        print("Sent")
        server.quit()

    i += 1
    print("One Time Operation Complete")


# =======================================================================
# Check one time function - checks the one time password against the 
# one that was sent out.
# @param onetimepass - the one time password the user entered
# @return boolean - returns true if correct, false if different
# =======================================================================
def checkOneTime(onetimepass):
    global i
    print("Checking One Time: " + onetimepass)
    print("Counter: ", i)
    checkCounter = i - 1

    if hotp.verify(onetimepass, checkCounter):
        print("True")
        return True
    else:
        print("False")
        return False


# =======================================================================
# Get Permissions function - Queries the database with many joins to
# find the permissions associated with a users account.
# @return a string of the permissions list returned from the database
# =======================================================================
def getPerm():
    permissionJoin = (
            """SELECT permission_name FROM permissions
            JOIN role_permissions
            ON permissions.permission_id = role_permissions.permission_id
            JOIN roles
            ON role_permissions.role_id = roles.role_id
            JOIN account_roles
            ON roles.role_id = account_roles.role_id
            JOIN accounts
            ON account_roles.user_id = accounts.user_id
            WHERE accounts.email = '%s';""" % sessionUser)
    mycursor.execute(permissionJoin)
    permissionList = mycursor.fetchall()
    return stringfy(permissionList)


# =======================================================================
# Stringfy function - turns a list into a string seperated by '/' so 
# it can be sent back to the client.
# =======================================================================
def stringfy(resultstatement):
    strings = ""
    for item in resultstatement:
        strings += item[0] + "/"
    print(strings)
    return strings


# =======================================================================
# Server Run - main method
# =======================================================================
serverRun()
