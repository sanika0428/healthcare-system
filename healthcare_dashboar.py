import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from diagnose_data import diagnosis_crud
from diagnose_data.diagnosis import show_diagnosis
from billing import show_billing
from statistics import statistics_dashboard
from crud import get_all_patients, add_patient, update_patient
from diagnose_data.data_entry import export_all_recoveries
from diagnose_data.patients_crud import load_patients_basic


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Healthcare Analytics Platform",
    layout="wide",
    page_icon="C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\image.png"
)

# =====================================================
# GLOBAL CSS
# =====================================================
st.markdown("""
<style>
.sidebar-btn > button {
    width: 100%;
    padding: 12px;
    margin: 6px 0;
    border-radius: 10px;
    background-color: #1f2937;
    color: white;
    border: 1px solid #374151;
    font-size: 16px;
    text-align: left;
}
.sidebar-btn-active > button {
    background-color: #2563eb !important;
}
.patient-card {
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
}
.patient-critical {
    background-color: #fee2e2;
    border-color: #fecaca;
    color: #b91c1c;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONSTANTS
# =====================================================
COST_BASIS = {"Standard":1000,"Advanced":3000,"Experimental":5000}
COST_PER_DAY = 500

# =====================================================
# SESSION STATE INIT
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "active_patient" not in st.session_state:
    st.session_state.active_patient = None


if "editing_patient_id" not in st.session_state:
    st.session_state.editing_patient_id = None

if "view_diagnosis_patient_id" not in st.session_state:
    st.session_state.view_diagnosis_patient_id = None

if "patients_df" not in st.session_state:
    st.session_state.patients_df = pd.DataFrame(columns=[
        "id",
        "name",
        "age",
        "gender",
        "phone",
        "email",
        "blood_group",
        "emergency_contact",
        "address",
        "insurance_policy",
        "policy_id",
        "coverage",
        "admission_date",
        "status",
        "last_visited"
    ])

if "billing_df" not in st.session_state:
    st.session_state.billing_df = pd.DataFrame(
        columns=["bill_id","patient_id","treatment","days","amount","date"]
    )

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.image("C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\logo2.png")  
def nav(label, icon):
    active = st.session_state.page == label
    css = "sidebar-btn-active" if active else "sidebar-btn"
    st.sidebar.markdown(f"<div class='{css}'>", unsafe_allow_html=True)
    if st.sidebar.button(f"{icon} {label}", use_container_width=True):
        st.session_state.page = label
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

nav("Dashboard","🏠")
nav("Patients","👨‍⚕️")
nav("Diagnosis","🧪")
nav("Billing","💰")
nav("Analytics","📊")

# =====================================================
# DASHBOARD
# =====================================================
if st.session_state.page == "Dashboard":

    # 🔥 Always sync dashboard with DB
    try:
        st.session_state.patients_df = get_all_patients()
    except Exception:
        pass

    patients = st.session_state.patients_df
    bills = st.session_state.billing_df

    st.markdown(
        "<h1>🩺 Healthcare Analytics Platform</h1>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", len(patients))
    c2.metric("Critical", len(patients[patients["status"] == "Critical"]))
    c3.metric("Recovered", len(patients[patients["status"] == "Recovered"]))
    c4.metric("Active", len(patients[patients["status"] == "Active"]))
    c5.metric(
        "💰 Revenue",
        f"₹ {bills['amount'].sum() if not bills.empty else 0}"
    )

    st.markdown("---")

    colA, colB = st.columns(2)

    # ================= PIE CHART =================
    with colA:
        st.subheader("📊 Patient Status Distribution")

        if not patients.empty and "status" in patients.columns:
            fig, ax = plt.subplots()
            patients["status"].value_counts().plot(
                kind="pie",
                autopct="%1.1f%%",
                startangle=90,
                ax=ax
            )
            ax.set_ylabel("")
            st.pyplot(fig)
        else:
            st.info("No patient data available")

    # ================= CRITICAL PATIENTS =================
    with colB:
        st.subheader("🚨 Critical Patients")

        critical = patients[patients["status"] == "Critical"]

        if critical.empty:
            st.caption("No critical patients at the moment.")

        for _, row in critical.iterrows():
            st.markdown(f"""
            <div class="patient-card patient-critical">
                <div class="patient-name">{row['name']}</div>
                <div class="patient-meta">
                    {row['age']} yrs • {row['gender']}<br>
                    📞 {row['phone']}
                </div>
            </div>
            """, unsafe_allow_html=True)
# PATIENTS
# ================= PATIENTS PAGE =================
elif st.session_state.page == "Patients":
    st.title("Patients")

    # 🔥 ALWAYS load from DB
    patients_df = get_all_patients()

    # ---------- Avatar ----------
    def avatar(name):
        return f"""
        <div style="
            width:38px;height:38px;
            border-radius:50%;
            background:#2563eb;
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:600;">
            {name[0].upper()}
        </div>
        """

    # ================= ADD PATIENT =================
    @st.dialog("➕ Add Patient", width="small")
    def add_patient_dialog():
        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Name")
            age = c2.number_input("Age", 0, 120, None)
            gender = c3.selectbox("Gender", ["Male","Female","Other"])

            c1, c2 = st.columns(2)
            phone = c1.text_input("Phone")
            email = c2.text_input("Email")

            c1,c2 = st.columns(2)
            blood_group = c1.selectbox("Blood Group",
                ["A+","A-","B+","B-","AB+","AB-","O+","O-"])
            emergency_contact = c2.text_input("Emergency Contact")
            address = st.text_area("Address")

            st.markdown("**Insurance (Optional)**")
            c1, c2, c3 = st.columns(3)
            insurance_policy = c1.text_input("Policy")
            policy_id = c2.text_input("Policy ID")
            coverage = c3.text_input("Coverage")

            c1, c2 = st.columns(2)
            admission_date = c1.date_input("Admission Date")
            status = c2.selectbox("Status", ["Active","Recovered","Critical"])
            last_visited = st.date_input("Last Visited")

            if st.form_submit_button("Add"):
                add_patient({
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "email": email,
                    "blood_group": blood_group,
                    "emergency_contact": emergency_contact,
                    "address": address,
                    "insurance_policy": insurance_policy,
                    "policy_id": policy_id,
                    "coverage": coverage,
                    "admission_date": str(admission_date),
                    "status": status,
                    "last_visited": str(last_visited)
                })
                st.success("Patient added")
                st.rerun()

    if st.button("➕ Add Patient"):
        add_patient_dialog()

    st.divider()

    # ================= PATIENT CARDS =================
    cols = st.columns(4)
    for idx, row in patients_df.iterrows():
        with cols[idx % 4]:
            with st.container(border=True):
                st.markdown(avatar(row["name"]), unsafe_allow_html=True)
                st.markdown(f"**{row['name']}**")
                st.caption(
                    f"""
                    Age: {row['age']} | {row['gender']}  
                    🩸 {row['blood_group']}  
                    📞 {row['phone']}  
                    🛡 {row['status']}
                    """
                )
                if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                    st.session_state.editing_patient_id = row["id"]
                if st.button("📜 View Diagnosis History", key=f"view_diag_{row['id']}"):
                    st.session_state.view_diagnosis_patient_id = row["id"]
                    st.session_state.page = "Diagnosis History"
                    st.rerun()
    # ================= EDIT PATIENT =================
    if st.session_state.editing_patient_id:
        pid = st.session_state.editing_patient_id
        patient_match = patients_df[patients_df["id"] == pid]
        if patient_match.empty:
            st.error("Patient not found.")
            st.session_state.editing_patient_id = None
        else:
            p = patients_df[patients_df["id"] == pid].iloc[0]
            @st.dialog("✏️ Edit Patient", width="small")
            def edit_dialog():
                with st.form("edit_form"):
                    c1, c2, c3 = st.columns(3)
                    name = c1.text_input("Name", p["name"])
                    age = c2.number_input("Age", 0, 120, int(p["age"]))
                    gender = c3.selectbox(
                    "Gender", ["Male","Female","Other"],
                    index=["Male","Female","Other"].index(p["gender"])
                )
                
                    c1, c2 ,c3 = st.columns(3)
                    phone = c1.text_input("Phone", p["phone"])
                    email = c2.text_input("Email", p["email"])
                    emergency_contact=c3.text_input("Emergency Contact",p["emergency_contact"])

                    address = st.text_area("Address", p["address"])
 
                    status = st.selectbox(
                    "Status",
                    ["Active","Recovered","Critical"],
                    index=["Active","Recovered","Critical"].index(p["status"])
                )

                    c1, c2, c3 = st.columns(3)
                    insurance_policy = c1.text_input("Policy", p["insurance_policy"])
                    policy_id = c2.text_input("Policy ID", p["policy_id"])
                    coverage = c3.text_input("Coverage", p["coverage"])

                    if st.form_submit_button("Save"):
                        update_patient(pid, {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "phone": phone,
                        "email": email,
                        "blood_group": p["blood_group"],
                        "emergency_contact": emergency_contact,
                        "address": address,
                        "insurance_policy": insurance_policy,
                        "policy_id": policy_id,
                        "coverage": coverage,
                        "admission_date": p["admission_date"],
                        "status": status,
                        "last_visited": p["last_visited"]
                    })
                        st.session_state.editing_patient_id = None
                        st.success("Updated")
                        st.rerun()

            edit_dialog()
        # ================= DIAGNOSIS HISTORY =================

elif st.session_state.page == "Diagnosis History":

    import pandas as pd
    from diagnose_data.diagnosis_crud import (
        get_diagnoses_by_patient,
        discharge_patient,
        update_diagnosis_status,
        delete_diagnosis
    )
    from diagnose_data.patients_crud import load_patients_basic

    st.subheader("📋 Diagnosis History")

    # -----------------------------
    # Load Patients
    # -----------------------------
    patients_df = load_patients_basic()

    if patients_df.empty:
        st.warning("No patients available.")
        st.stop()

    patient_dict = {
        f"{row['name']} (ID: {row['id']})": row["id"]
        for _, row in patients_df.iterrows()
    }

    selected_label = st.selectbox(
        "Select Patient",
        list(patient_dict.keys())
    )

    pid = patient_dict[selected_label]

    # -----------------------------
    # Get Diagnosis Records
    # -----------------------------
    records = get_diagnoses_by_patient(pid)

    if not records:
        st.info("No diagnosis records found.")
        st.stop()

    # Convert to DataFrame
    diagnosis_df = pd.DataFrame(records, columns=[
        "id",
        "patient_id",
        "disease",
        "status",
        "symptoms",
        "expected_recovery_time",
        "date_of_diagnosis",
        "date_of_recoveryordischarge",
        "actual_recovery_time"
    ])

    st.divider()

    # -----------------------------
    # Editable History Table
    # -----------------------------
    for _, row in diagnosis_df.iterrows():

        diag_id = row["id"]

        with st.container():

            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])

            # Disease
            c1.markdown(f"**Disease:** {row['disease']}")
            is_recovered= row["status"] == "Recovered"
            # Status dropdown
            status_option = c2.selectbox("Status",["Diagnosed", "Recovered"],index=["Diagnosed", "Recovered"].index(row["status"]),key=f"status_{diag_id}" ,disabled=is_recovered)
            # Recovery Date
            recovery_date = c3.date_input(
                "Recovery Date",
                value=pd.to_datetime(row["date_of_recoveryordischarge"]).date()
                if row["date_of_recoveryordischarge"]
                else None,
                key=f"date_{diag_id}"
            )

            # Update Button
            if c4.button("Update", key=f"update_{diag_id}"):

                if status_option == "Recovered" and recovery_date:

                    discharge_patient(
                        diagnosis_id=diag_id,
                        recovery_date=recovery_date
                    )
                    export_all_recoveries(diag_id)

                else:
                    update_diagnosis_status(
                        diagnosis_id=diag_id,
                        status=status_option
                    )

                st.success("Updated successfully")
                st.rerun()

            # Delete Button
            if c5.button("Delete", key=f"delete_{diag_id}"):
                delete_diagnosis(diag_id)
                st.warning("Diagnosis deleted")
                st.rerun()

        st.divider()



# DIAGNOSIS (CONNECTED TO PATIENT)
elif st.session_state.page == "Diagnosis":
    show_diagnosis()
# Billing
elif st.session_state.page=="Billing":
    show_billing()
#Analytics page
elif st.session_state.page=="Analytics":
    statistics_dashboard()
st.markdown("<hr><center>Healthcare Analytics Platform • Streamlit</center>", unsafe_allow_html=True)
