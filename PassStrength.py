# =======================================================================
# SCC.363 Security and Risk Coursework 1
# Password strength program that checks for valid usernames and password
# strength based on the top common passwords. Passwords require a minimum
# length of 8, 1 symbol, 1 capital letter, 1 number, 1 lowercase letter.
# =======================================================================
import re

# Valid username function - Uses regex to check string is in email format
# @return bool - True if username is valid email, false otherwise
def isValidUsername(username):
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    result = re.findall(pattern, username)
    if (result):
        return True
    else:
        return False

# Valid password function - Uses regex to check string is a valid password
# @return bool - returns true if password is considered strong, false otherwise
def isValidPassword(password):
    pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()-_/=+{};:,<.>]).*$"
    result = re.findall(pattern, password)
    if (result):
        return True
    elif (len(result) < 8):
        print("-----------------------")
        print("Please make sure your password is more than 8 characters.")
        return False
    else:
        return False
