# =======================================================================
# SCC.363 Security and Risk Coursework 1
# DBConnection - creates a database for a medical facility and creates
# the tables needed for a role based access scheme. Inserts the default
# roles within the system, and their permissions.
# =======================================================================
import mysql.connector
from datetime import datetime

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root"
)

mycursor = mydb.cursor()

# =======================================================================
# Create database if it doesnt already exist
# =======================================================================
mycursor.execute("CREATE DATABASE IF NOT EXISTS medicalfacility")
print("Database created!")
mycursor.execute("use medicalfacility")

# =======================================================================
# Create tables if they don't already exist
# =======================================================================
mycursor.execute("""CREATE TABLE IF NOT EXISTS patients (
  pcn int NOT NULL AUTO_INCREMENT,
  first_name varchar(255),
  surname varchar(255),
  street_number varchar(255),
  address varchar(255),
  postcode varchar(255),
  phone_number int,
  created_at timestamp,
  PRIMARY KEY (pcn)
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS staff (
  staff_num int NOT NULL AUTO_INCREMENT,
  first_name varchar(255),
  surname varchar(255),
  street_number varchar(255),
  address varchar(255),
  postcode varchar(255),
  phone_number int,
  salary double,
  created_at timestamp,
  PRIMARY KEY (staff_num)
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS accounts (
  user_id int NOT NULL AUTO_INCREMENT,
  email varchar(255) NOT NULL,
  salt varchar(255),
  password varchar(255),
  pcn int,
  staff_num int,
  PRIMARY KEY (user_id),
  FOREIGN KEY (pcn) REFERENCES patients(pcn) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (staff_num) REFERENCES staff(staff_num) ON DELETE CASCADE ON UPDATE CASCADE
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS roles (
  role_id int NOT NULL AUTO_INCREMENT,
  role_name varchar(255),
  PRIMARY KEY (role_id)
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS account_roles (
  user_id int,
  role_id int,
  PRIMARY KEY (user_id,role_id),
  FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE  ON UPDATE CASCADE
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS permissions (
  permission_id int NOT NULL AUTO_INCREMENT,
  permission_name varchar(255),
  PRIMARY KEY (permission_id)
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS role_permissions (
  role_id int,
  permission_id int,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE ON UPDATE CASCADE
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS patient_permissions (
  pcn int,
  permission_id int,
  PRIMARY KEY (pcn, permission_id),
  FOREIGN KEY (pcn) REFERENCES patients(pcn) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE ON UPDATE CASCADE
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS staff_permissions (
  staff_num int,
  permission_id int,
  PRIMARY KEY (staff_num, permission_id),
  FOREIGN KEY (staff_num) REFERENCES staff(staff_num) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE ON UPDATE CASCADE
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS health (
  health_record int NOT NULL AUTO_INCREMENT,
  pcn int NOT NULL,
  ailment varchar(255),
  treatment varchar(255),
  created_at timestamp,
  PRIMARY KEY (health_record)
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS health_permissions (
  health_record int, 
  permission_id int,
  PRIMARY KEY (health_record, permission_id),
  FOREIGN KEY (health_record) REFERENCES health(health_record) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE ON UPDATE CASCADE
)""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS audit_logs (
  log_id int NOT NULL AUTO_INCREMENT,
  user_id int,
  ip_address varchar(255),
  description varchar(255),
  operation_time timestamp,
  PRIMARY KEY (log_id),
  FOREIGN KEY (user_id) REFERENCES accounts(user_id) 
)""")
print(mycursor.rowcount, "Tables created")

# =======================================================================
# Print all the tables that were created
# =======================================================================
#mycursor.execute("SHOW TABLES")
#tables = mycursor.fetchall()
#for table in tables:
   #print(table)

# =======================================================================
# Insert the different roles into database
# =======================================================================
query = ("INSERT INTO roles (role_id, role_name) VALUES (%s, %s)")
values = [
  (0,'Regulator'),
  (0,'Admin Staff'),
  (0,'Medical Staff'),
  (0,'Patient'),
  (0,'Non Medical Staff')
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "Roles were inserted.")

# =======================================================================
# Insert the different permissions into database
# =======================================================================
query = ("INSERT INTO permissions (permission_id, permission_name) VALUES (%s, %s)")
values = [
    (0, 'View all patients'), # 1
    (0, 'View your patient details'), # 2
    (0, 'Update any patient details'), # 3
    (0, 'Update your patient details'), # 4
    (0, 'Delete patient'), # 5
    (0, 'View all health records'), # 6
    (0, 'View your health records'), # 7
    (0, 'Add a health record'), # 8
    (0, 'View a staff member'), # 9
    (0, 'Update staff'), # 10
    (0, 'Delete staff'), # 11
    (0, 'View Audit logs') # 12
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "permissions were inserted.")

# =======================================================================
# Insert the linking table for roles and permissions into database
# =======================================================================
query = ("INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)")
values = [
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (1, 9),
    (1, 10),
    (1, 11),
    (1, 12),
    (2, 1),
    (2, 3),
    (2, 9),
    (2, 10),
    (3, 1),
    (3, 6),
    (3, 8),
    (4, 2),
    (4, 4),
    (4, 7)
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "role permissions were inserted.")

# =======================================================================
# Insert patient details into patients
# =======================================================================
query = ("""INSERT INTO patients (pcn, first_name, surname, street_number, address, postcode, phone_number, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""")
values = [
    (0, 'Johnny', 'Bgoode', '17', 'Street Road', 'LA11XX', '0010100101', timestamp),
    (0, 'John', 'Doe', '101', 'Long Street', 'LA12TT', '000010102000', timestamp),
    (0, 'Jane', 'Doe', '1', 'Long Street', 'LA12TT', '001001001001', timestamp),
    (0, 'Greg', 'Man', '5', 'Road Street', 'LA12EE', '998891322', timestamp)
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "patients were inserted.")

# =======================================================================
# Insert staff details into staff
# =======================================================================
query = ("""INSERT INTO staff (staff_num, first_name, surname, street_number, address, postcode, phone_number, salary, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""")
values = [
    (0, 'Old', 'Gregg', '28', 'Lancaster rd', 'LA31XX', '00412345', 40000.00, timestamp),
    (0, 'Mister', 'Man', '302', 'New Street', 'LA41EE', '000999888', 20000.00, timestamp),
    (0, 'Geesus', 'God', '100', 'Yeet Street', 'LA41FF', '00044473822', 30000.00, timestamp),
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "staff were inserted.")

# =======================================================================
# Insert account details into accounts
# =======================================================================
query = ("""INSERT INTO accounts (user_id, email, salt, password, pcn, staff_num) 
        VALUES (%s, %s, %s, %s, %s, %s)""")
values = [
    (0, 'gareth@fmail.com', '4d1a7a4e5d834eafa14af3bb51037060', '3b0f6984f481b72212445e6f287f74fa051f099a6927870b2f0371da76bd8238b1c79dfee6b80307d9cba9b746f3ea60efb2fd5a90269fb041748a90f75c210d', 1, None),
    (0, 'eric@jmail.com', '52cb022f448b4ad1965294e15a2aef26', 'a27afe8ee95e9fd42638e7615db259ebe8b7cdb8f96ecac384fde9e4e4c636fc4315f3e2542c8a744a0d68dbc915c0f4858d0b9907b6f2ac214be003f6b4453b', 2, None),
    (0, 'jarljackson10@gmail.com', '52afc3da1970485daf1c454245aaf83e', '0435b4985a704636a839705a940e31e841adf8825c80d4464ac7d028500aaab948095de4b6a3625c5254763fabdcb3b773c2d744a23e8efbd583c8ffd7f6fe24', 3, None),
    (0, 'henry@lmail.com', 'd8c4e83168d54b688e6ceedd3f983a4c', '4086d5477196492d704f3d242a7185aa9a84355433d867e4a5193b0ec5afddf14a2a0fd1cd83264c625c7526fe167b93759bb3958bfb7adb5e7eb9f6fee83c03', None, 1),
    (0, 'keiran@omail.com', '8dbbdb08ec504fd0873098566dbdde5a', '1a88b4ee930bbf9d51f74325af1151449e09bba33d3fa3a791db40f9d5337aa8b7af4ae498596534ab4e328349438477af46b918086ff283a3575dd33ec85027', None, 2)
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "accounts were inserted.")

# =======================================================================
# Insert account role details into account_roles
# =======================================================================
query = ("""INSERT INTO account_roles (user_id, role_id) VALUES (%s, %s)""")
values = [
    (1, 1), 
    (2, 2), 
    (3, 3), 
    (4, 4), 
    (5, 5)
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "account roles were inserted.")

# =======================================================================
# Insert health records into health
# =======================================================================
query = ("""INSERT INTO health (health_record, pcn, ailment, treatment, created_at) 
        VALUES (%s, %s, %s, %s, %s)""")
values = [
    (0, 1, 'Diabetes', 'Insulin', timestamp),
    (0, 1, 'Depression', 'Pills', timestamp),
    (0, 2, 'Anxiety', 'Pills', timestamp),
    (0, 2, 'Depression', 'CBT', timestamp),
    (0, 3, 'Back pain', 'Pills', timestamp)
]
mycursor.executemany(query, values)
print(mycursor.rowcount, "health records were inserted.")

# =======================================================================
# Insert patient permissions into patient_permissions
# =======================================================================
query = ("""INSERT INTO patient_permissions (pcn, permission_id) VALUES (%s, %s)""")
values = [
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (3, 1),
    (3, 2),
    (3, 3),
    (3, 4),
    (3, 5)
]
mycursor.executemany(query, values)
print("Patient permissions added")

# =======================================================================
# Insert staff permissions into staff_permissions
# =======================================================================
query = ("""INSERT INTO staff_permissions (staff_num, permission_id) VALUES (%s, %s)""")
values = [
    (1, 9),
    (1, 10),
    (1, 11),
    (2, 9),
    (2, 10),
    (2, 11),
]
mycursor.executemany(query, values)
print("Staff permissions added")

# =======================================================================
# Insert health permissions into health permissions
# =======================================================================
query = ("""INSERT INTO health_permissions (health_record, permission_id) VALUES (%s, %s)""")
values = [
    (1, 6),
    (1, 7),
    (1, 8),
    (2, 6),
    (2, 7),
    (2, 8),
    (3, 6),
    (3, 7),
    (3, 8),
    (4, 6),
    (4, 7),
    (4, 8),
    (5, 6),
    (5, 7),
    (5, 8)
]
mycursor.executemany(query, values)
print("Health permissions added")

# =======================================================================
# Finally, commit all inserts and close the connection and cursor
# =======================================================================
mydb.commit()
mycursor.close()
mydb.close()