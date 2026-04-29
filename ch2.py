import sqlite3
import struct

conn = sqlite3.connect("C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\patients.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        id,
        patient_id,
        disease,
        status,
        symptoms,
        expected_recovery_time,
        date_of_diagnosis,
        date_of_recoveryordischarge,
        actual_recovery_time
    FROM diagnoses
""")

rows = cursor.fetchall()

for row in rows:
    id_val = row[0]
    blob_patient_id = row[1]

    # Convert 8-byte BLOB to integer
    patient_id_int = struct.unpack("<Q", blob_patient_id)[0]

    cursor.execute("""
        INSERT INTO diagnoses_new (
            id,
            patient_id,
            disease,
            status,
            symptoms,
            expected_recovery_time,
            date_of_diagnosis,
            date_of_recoveryordischarge,
            actual_recovery_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_val,
        patient_id_int,
        row[2],
        row[3],
        row[4],
        row[5],
        row[6],
        row[7],
        row[8]
    ))

conn.commit()
conn.close()
