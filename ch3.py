import sqlite3
conn = sqlite3.connect("patients.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE diagnoses_new RENAME TO diagnoses")