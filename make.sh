sudo apt -y install mysql-client-5.7
sudo apt -y install mysql-server-5.7
sudo apt -y install mysql-workbench
sudo pip3 install pyotp
sudo pip3 install mysql-connector-python
sudo /usr/sbin/mysqld --skip-grant-tables --skip-networking &
echo "Type In:"
echo "sudo mysql -u root"
echo "FLUSH PRIVILEGES;"
echo "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';;"
echo "exit"
echo "sudo /etc/init.d/mysql restart"
echo "python3.6 dbConnection.py"
