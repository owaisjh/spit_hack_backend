import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

#create_table = "CREATE TABLE orders (id INTEGER PRIMARY KEY, username text, user_name text, items text, cost int, address text, contact int, paymenttype text, status int, daterec date, datecomp date)"
#create_table = "ALTER TABLE allmeds ADD PRIMARY KEY (id) "

#create_table = "CREATE TABLE presorder (id INTEGER PRIMARY KEY, username text, pres text, status int)"
#create_table =" CREATE TABLE users (email	text, password	text,	name	text, contact	int, aadhar_no text, wallet_id text, PRIMARY KEY(wallet_id));"

#create_table = "CREATE TABLE orders (id INTEGER PRIMARY KEY, username text, user_name text, items text, cost int, address text, contact int, paymenttype text, status int, daterec date, datecomp date)"

#create_table =" CREATE TABLE offers (id INTEGER PRIMARY KEY, employerEmail text, employerWalletId text, emplyeeEmail text, emplyeeWalletId text, hourRate float, duration int, leavesAllowed int, leavesPenalty int, earlyBonus int, status int);"



# query = "INSERT INTO users VALUES ( ?, ?, ?, ?,?, ?)"
#
# cursor.execute(query, ("admin@admin.com", "password", "Admin", 1234567890,"APZ123" ,"loldoesthisevenwork?123"))

create_table="ALTER TABLE transactions ADD receiverName; "

cursor.execute(create_table)
# query = "SELECT * FROM users "
# result = cursor.execute(query, )
# row = result.fetchall()
connection.commit()
connection.close()
# print(row)



