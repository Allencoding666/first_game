import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="allen7788",
    database="first_game",
)

cursor = connection.cursor()

cursor.execute("SELECT `score` FROM `user_score` ORDER BY `score` DESC LIMIT 3;")
recodes = cursor.fetchall()
for i in recodes:
    print(i)

cursor.close()
connection.close()


a = ["1", "5", "2", "9"]
a.sort()
print(a)
