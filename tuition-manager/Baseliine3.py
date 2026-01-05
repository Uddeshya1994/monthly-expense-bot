import streamlit as st
import pandas as pd
import os
import urllib.parse
from utils import (
    load_students,
    save_students,
    generate_student_id,
    load_attendance,
    save_attendance,
    load_fees,
    save_fees
)

import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password: str, stored_hash: str) -> bool:
    return hash_password(input_password) == stored_hash

# ================= CONFIG =================
st.set_page_config(page_title="Smart Tuition Manager", layout="wide")
# ================= GLOBAL THEME =================
st.markdown("""
<style>

/* -------- GLOBAL -------- */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f5f7fb;
}

/* -------- SIDEBAR -------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f2937, #111827);
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* -------- HEADINGS -------- */
h1, h2, h3 {
    color: #1f2937;
    font-weight: 600;
}

/* -------- CARDS -------- */
.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* -------- BUTTONS -------- */
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    border-radius: 10px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    border: none;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #4f46e5, #4338ca);
}

/* -------- DOWNLOAD BUTTON -------- */
.stDownloadButton>button {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    border-radius: 10px;
    font-weight: 600;
}

/* -------- INPUTS -------- */
input, textarea, select {
    border-radius: 8px !important;
}

/* -------- TABLES -------- */
thead tr th {
    background-color: #6366f1 !important;
    color: white !important;
}
tbody tr:hover {
    background-color: #eef2ff;
}

/* -------- LINKS -------- */
a {
    color: #4f46e5;
    font-weight: 600;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* -------- SUCCESS / INFO -------- */
div[data-testid="stSuccess"] {
    background-color: #ecfdf5;
    border-left: 6px solid #10b981;
}
div[data-testid="stInfo"] {
    background-color: #eef2ff;
    border-left: 6px solid #6366f1;
}
div[data-testid="stError"] {
    background-color: #fef2f2;
    border-left: 6px solid #ef4444;
}

</style>
""", unsafe_allow_html=True)


TEACHER_PIN = "1234"
BASE_DIR = "study_materials"
os.makedirs(BASE_DIR, exist_ok=True)

# ================= WHATSAPP HELPER =================
def generate_whatsapp_link(phone, message):
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded_msg}"

# ================= SYLLABUS =================
SYLLABUS = {
    "CBSE": {
        "9": {
            "Maths": ["Number Systems", "Polynomials", "Linear Equations"],
            "Science": ["Matter", "Motion", "Force"],
            "English": ["Beehive Ch 1", "Beehive Ch 2"]
        },
        "10": {
            "Maths": ["Real Numbers", "Quadratic Equations", "Trigonometry"],
            "Science": ["Life Processes", "Electricity"],
            "English": ["First Flight Ch 1", "First Flight Ch 2"]
        }
    },
    "ICSE": {
        "9": {
            "Maths": ["Rational Numbers", "Algebra"],
            "Physics": ["Motion", "Laws of Motion"]
        },
        "10": {
            "Maths": ["Banking", "Geometry"],
            "Physics": ["Force", "Energy"]
        }
    }
}

# ================= SESSION INIT =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.student_id = None
    st.session_state.student_class = None

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.title("🔐 Login")

    role = st.radio("Login as", ["Teacher", "Student"])

    if role == "Teacher":
        pin = st.text_input("Enter Teacher PIN", type="password")
        if st.button("Login"):
            if pin == TEACHER_PIN:
                st.session_state.logged_in = True
                st.session_state.role = "Teacher"
                st.rerun()
            else:
                st.error("Invalid PIN")

    else:
        students_df = load_students()
        student_id = st.selectbox(
            "Select Student ID",
            students_df["student_id"] if not students_df.empty else []
        )

        if st.button("Login"):
            row = students_df[students_df["student_id"] == student_id]
            if not row.empty:
                st.session_state.logged_in = True
                st.session_state.role = "Student"
                st.session_state.student_id = student_id
                st.session_state.student_class = row.iloc[0]["class"]
                st.rerun()
            else:
                st.error("Invalid Student")

    st.stop()

# ================= SIDEBAR =================
st.sidebar.title("📚 Smart Tuition Manager")
st.sidebar.write(f"Role: **{st.session_state.role}**")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.student_id = None
    st.session_state.student_class = None
    st.rerun()

if st.session_state.role == "Teacher":
    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Students", "Attendance", "Fees", "Study Materials"]
    )
else:
    menu = "Study Materials"

# ================= DASHBOARD =================
if menu == "Dashboard" and st.session_state.role == "Teacher":
    st.title("📊 Dashboard")

    students_df = load_students()
    attendance_df = load_attendance()
    fees_df = load_fees()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Students", len(students_df))
    col2.metric("Attendance Records", len(attendance_df))

    if not fees_df.empty:
        fees_df["amount"] = fees_df["amount"].astype(float)
        paid = fees_df[fees_df["status"] == "Paid"]["amount"].sum()
        pending = fees_df[fees_df["status"] == "Pending"]["amount"].sum()
    else:
        paid = pending = 0

    col3.metric("Fees Paid (₹)", f"{paid:.0f}")
    col4.metric("Fees Pending (₹)", f"{pending:.0f}")

# ================= STUDENTS =================
elif menu == "Students" and st.session_state.role == "Teacher":
    st.title("👨‍🎓 Student Management")

    df = load_students()

    with st.form("add_student"):
        student_id = generate_student_id(df)
        st.text_input("Student ID", student_id, disabled=True)
        name = st.text_input("Student Name")
        cls = st.text_input("Class")
        parent = st.text_input("Parent Name")
        phone = st.text_input("Parent Phone (with country code)")

        if st.form_submit_button("Add Student"):
            if not name or not cls:
                st.error("Name and Class are required")
            else:
                df = pd.concat([df, pd.DataFrame([{
                    "student_id": student_id,
                    "name": name,
                    "class": cls,
                    "parent_name": parent,
                    "parent_phone": phone
                }])], ignore_index=True)
                save_students(df)
                st.success("Student added")
                st.rerun()

    st.divider()
    st.dataframe(df, use_container_width=True)

# ================= ATTENDANCE =================
elif menu == "Attendance" and st.session_state.role == "Teacher":
    st.title("🗓️ Attendance")

    students_df = load_students()
    attendance_df = load_attendance()

    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Date")
    with col2:
        selected_class = st.selectbox(
            "Class",
            sorted(students_df["class"].unique())
        )

    class_students = students_df[students_df["class"] == selected_class]
    existing_df = attendance_df[
        (attendance_df["date"] == str(selected_date)) &
        (attendance_df["class"] == selected_class)
    ]

    attendance_map = {}

    for _, row in class_students.iterrows():
        record = existing_df[existing_df["student_id"] == row["student_id"]]

        if record.empty:
            default_index = 0
        elif record.iloc[0]["status"] == "Present":
            default_index = 1
        else:
            default_index = 2

        status = st.selectbox(
            f"{row['student_id']} - {row['name']}",
            ["Not Available", "Present", "Absent"],
            index=default_index,
            key=f"{selected_date}_{row['student_id']}"
        )

        if status != "Not Available":
            attendance_map[row["student_id"]] = {
                "date": str(selected_date),
                "student_id": row["student_id"],
                "name": row["name"],
                "class": row["class"],
                "status": status
            }

    col_save, col_export = st.columns(2)

    with col_save:
        if st.button("💾 Save / Update Attendance"):
            attendance_df = attendance_df[
                ~(
                    (attendance_df["date"] == str(selected_date)) &
                    (attendance_df["class"] == selected_class)
                )
            ]
            if attendance_map:
                attendance_df = pd.concat(
                    [attendance_df, pd.DataFrame(attendance_map.values())],
                    ignore_index=True
                )
            save_attendance(attendance_df)
            st.success("Attendance saved")

    with col_export:
        export_df = attendance_df[
            (attendance_df["date"] == str(selected_date)) &
            (attendance_df["class"] == selected_class)
        ]
        if export_df.empty and attendance_map:
            export_df = pd.DataFrame(attendance_map.values())

        if not export_df.empty:
            st.download_button(
                "⬇️ Export Attendance (CSV)",
                export_df.to_csv(index=False),
                file_name=f"attendance_{selected_class}_{selected_date}.csv",
                mime="text/csv"
            )

# ================= FEES =================
elif menu == "Fees" and st.session_state.role == "Teacher":
    st.title("💰 Fee Management")

    students_df = load_students()
    fees_df = load_fees()

    with st.form("fee_form"):
        student = st.selectbox(
            "Student",
            students_df["student_id"] + " - " + students_df["name"]
        )
        month = st.selectbox(
            "Month",
            ["Jan","Feb","Mar","Apr","May","Jun",
             "Jul","Aug","Sep","Oct","Nov","Dec"]
        )
        amount = st.number_input("Amount (₹)", min_value=0)
        status = st.selectbox("Status", ["Paid", "Pending"])

        if st.form_submit_button("Save Fee"):
            sid = student.split(" - ")[0]
            srow = students_df[students_df["student_id"] == sid].iloc[0]

            fees_df = fees_df[
                ~(
                    (fees_df["student_id"] == sid) &
                    (fees_df["month"] == month)
                )
            ]

            fees_df = pd.concat([fees_df, pd.DataFrame([{
                "student_id": sid,
                "name": srow["name"],
                "class": srow["class"],
                "month": month,
                "amount": amount,
                "status": status
            }])], ignore_index=True)

            save_fees(fees_df)
            st.success("Fee saved")

    st.divider()
    st.dataframe(fees_df, use_container_width=True)

    st.divider()
    st.subheader("📲 WhatsApp Fee Pending Reminders")

    pending_fees = fees_df[fees_df["status"] == "Pending"]
    if pending_fees.empty:
        st.success("🎉 No pending fees")
    else:
        for _, row in pending_fees.iterrows():
            student = students_df[
                students_df["student_id"] == row["student_id"]
            ].iloc[0]

            message = (
                f"Hello {student['parent_name']},\n\n"
                f"This is a reminder that the tuition fee of ₹{row['amount']} "
                f"for {row['name']} (Class {row['class']}) "
                f"for the month of {row['month']} is pending.\n\n"
                f"Please pay at the earliest.\n\n"
                f"– Tuition Admin"
            )

            whatsapp_link = generate_whatsapp_link(
                student["parent_phone"],
                message
            )

            c1, c2, c3, c4, c5 = st.columns([2,2,2,2,2])
            c1.write(row["student_id"])
            c2.write(row["name"])
            c3.write(f"₹{row['amount']}")
            c4.write(row["month"])
            c5.markdown(
                f"[📲 Send WhatsApp]({whatsapp_link})",
                unsafe_allow_html=True
            )

# ================= STUDY MATERIALS =================
elif menu == "Study Materials":
    st.title("📚 Study Materials")

    board = st.selectbox("Board", ["CBSE", "ICSE"])

    if st.session_state.role == "Student":
        class_no = st.session_state.student_class[:2]
        st.info(f"Showing materials for your class: {st.session_state.student_class}")
    else:
        class_no = st.selectbox("Class", list(SYLLABUS[board].keys()))

    subject = st.selectbox(
        "Subject",
        list(SYLLABUS[board][class_no].keys())
    )

    st.subheader("📘 Topics")
    for t in SYLLABUS[board][class_no][subject]:
        st.write(f"• {t}")

    folder = os.path.join(BASE_DIR, board, class_no, subject)
    os.makedirs(folder, exist_ok=True)

    if st.session_state.role == "Teacher":
        st.subheader("⬆️ Upload (Teacher Only)")
        file = st.file_uploader("Upload PDF / Notes", type=["pdf", "txt"])
        if file:
            with open(os.path.join(folder, file.name), "wb") as f:
                f.write(file.getbuffer())
            st.success("File uploaded")

    st.subheader("📥 Available Materials")
    files = os.listdir(folder)
    if files:
        for f in files:
            with open(os.path.join(folder, f), "rb") as file:
                st.download_button(f"Download {f}", file, file_name=f)
    else:
        st.info("No materials available")
