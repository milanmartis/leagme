import sqlite3

connection = sqlite3.connect('../instance/database.db')
cursor = connection.cursor()
# WHERE CLAUSE TO RETRIEVE DATA
cursor.execute("SELECT user.id, user.first_name, user_duel.result FROM user JOIN user_duel ON user.id = user_duel.user_id AND user_duel.duel_id = 6")

# printing the cursor data
print(cursor.fetchall())

connection.commit()
connection.close()

