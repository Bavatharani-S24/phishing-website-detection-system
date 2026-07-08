import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM users")

cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin','admin123','admin')")
cursor.execute("INSERT INTO users (username, password, role) VALUES ('user','user123','user')")

conn.commit()
conn.close()

print("Users added successfully")