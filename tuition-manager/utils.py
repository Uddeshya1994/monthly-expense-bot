import pandas as pd
import os

STUDENTS_FILE = "students.csv"
ATTENDANCE_FILE = "attendance.csv"
FEES_FILE = "fees.csv"

# ---------- STUDENTS ----------
def load_students():
    if os.path.exists(STUDENTS_FILE):
        return pd.read_csv(STUDENTS_FILE, dtype=str)
    return pd.DataFrame(columns=[
        "student_id", "name", "class", "parent_name", "parent_phone"
    ])

def save_students(df):
    df.to_csv(STUDENTS_FILE, index=False)

def generate_student_id(df):
    if df.empty:
        return "STU001"

    ids = df["student_id"].dropna().astype(str)
    last_number = (
        ids.str.replace("STU", "", regex=False)
           .astype(int)
           .max()
    )
    return f"STU{last_number + 1:03d}"

# ---------- ATTENDANCE ----------
def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        return pd.read_csv(ATTENDANCE_FILE, dtype=str)
    return pd.DataFrame(columns=["date", "student_id", "name", "class", "status"])

def save_attendance(df):
    df.to_csv(ATTENDANCE_FILE, index=False)

# ---------- FEES ----------
def load_fees():
    if os.path.exists(FEES_FILE):
        return pd.read_csv(FEES_FILE, dtype=str)
    return pd.DataFrame(columns=[
        "student_id", "name", "class", "month", "amount", "status"
    ])

def save_fees(df):
    df.to_csv(FEES_FILE, index=False)
