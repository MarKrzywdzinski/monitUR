import sqlite3
conn = sqlite3.connect('sensor_new.db')       # create a database connection to a SQLite database
            
print("1")
cipa = conn.cursor().execute("SELECT count(*) FROM data_center")
print("2", cipa)
cipa = conn.cursor().execute("SELECT * FROM data_center")
print('gowno', cipa)
table_length = conn.cursor().fetchone()
print("3", table_length)
if table_length >= 100:
# Jeśli tabela ma więcej niż 1000 wierszy, usuń 100 ostatnich
     conn.cursor().execute("DELETE FROM data_center WHERE id IN (SELECT id FROM data_center ORDER BY id DESC LIMIT 100)")
     conn.commit()  
     print(f"Table length: {table_length}. Deleted last 100 rows.")
else:
     print(f"Table length: {table_length}. Table is within limits.")
