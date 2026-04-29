import sqlite3
import pandas as pd

DB_NAME = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\patients.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def get_all_patients():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df

def add_patient(data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (
            name, age, gender, phone, email, blood_group,
            emergency_contact, address,
            insurance_policy, policy_id, coverage,
            admission_date, status, last_visited
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(data.values()))

    conn.commit()
    conn.close()

def update_patient(patient_id, data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE patients SET
            name = ?,
            age = ?,
            gender = ?,
            phone = ?,
            email = ?,
            blood_group = ?,
            emergency_contact = ?,
            address = ?,
            insurance_policy = ?,
            policy_id = ?,
            coverage = ?,
            admission_date = ?,
            status = ?,
            last_visited = ?
        WHERE id = ?
    """, (
        data["name"],
        data["age"],
        data["gender"],
        data["phone"],
        data["email"],
        data["blood_group"],
        data["emergency_contact"],
        data["address"],
        data["insurance_policy"],
        data["policy_id"],
        data["coverage"],
        data["admission_date"],
        data["status"],
        data["last_visited"],
        patient_id
    ))

    conn.commit()
    conn.close()
