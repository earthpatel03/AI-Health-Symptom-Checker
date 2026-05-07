
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Health Assistant Pro",
    page_icon="🩺",
    layout="wide"
)

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect("health_app.db", check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT
)
""")

# HISTORY TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    username TEXT,
    disease TEXT,
    risk TEXT,
    confidence REAL,
    date TEXT
)
""")

conn.commit()

# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# DARK / LIGHT MODE
# =========================================================

theme = st.sidebar.toggle("🌙 Dark Mode", value=True)

if theme:
    bg_color = "#0f172a"
    card_color = "#1e293b"
    text_color = "white"

else:
    bg_color = "#f8fafc"
    card_color = "white"
    text_color = "black"

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(f"""
<style>

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

.metric-card {{
    background-color: {card_color};
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
}}

.big-font {{
    font-size: 22px !important;
    font-weight: bold;
}}

</style>
""", unsafe_allow_html=True)

# =========================================================
# MULTI LANGUAGE SUPPORT
# =========================================================

translations = {

    "English": {
        "title": "🩺 AI Health Assistant Pro",
        "age": "Age",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "predict": "Predict Disease",
        "history": "My History",
        "dashboard": "Admin Dashboard"
    },

    "Gujarati": {
        "title": "🩺 AI આરોગ્ય સહાયક",
        "age": "ઉંમર",
        "gender": "લિંગ",
        "male": "પુરુષ",
        "female": "સ્ત્રી",
        "predict": "રોગ શોધો",
        "history": "મારો ઇતિહાસ",
        "dashboard": "એડમિન ડેશબોર્ડ"
    },

    "Hindi": {
        "title": "🩺 AI स्वास्थ्य सहायक",
        "age": "आयु",
        "gender": "लिंग",
        "male": "पुरुष",
        "female": "महिला",
        "predict": "रोग जांचें",
        "history": "इतिहास",
        "dashboard": "एडमिन डैशबोर्ड"
    }
}

language = st.sidebar.selectbox(
    "🌍 Select Language",
    ["English", "Gujarati", "Hindi"]
)

t = translations[language]

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("🔐 Login / Signup")

    auth_mode = st.radio(
        "Select Option",
        ["Login", "Signup"]
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # SIGNUP
    if auth_mode == "Signup":

        if st.button("Create Account"):

            if username == "" or password == "":
                st.warning("Please fill all fields")

            else:

                hashed_password = hash_password(password)

                cursor.execute(
                    "INSERT INTO users VALUES (?, ?)",
                    (username, hashed_password)
                )

                conn.commit()

                st.success("✅ Account Created Successfully")

    # LOGIN
    if auth_mode == "Login":

        if st.button("Login"):

            hashed_password = hash_password(password)

            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hashed_password)
            )

            result = cursor.fetchone()

            if result:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success("✅ Login Successful")
                st.rerun()

            else:
                st.error("❌ Invalid Username or Password")

# =========================================================
# MAIN APPLICATION
# =========================================================

else:

    st.sidebar.success(
        f"👋 Welcome {st.session_state.username}"
    )

    page = st.sidebar.radio(
        "📂 Navigation",
        [
            "Health Checker",
            t["history"],
            t["dashboard"]
        ]
    )

    # =====================================================
    # HEALTH CHECKER PAGE
    # =====================================================

    if page == "Health Checker":

        st.title(t["title"])

        st.warning(
            "⚠️ Educational purpose only. Not medical advice."
        )

        # -------------------------------------------------
        # USER INFO
        # -------------------------------------------------

        st.sidebar.header("👤 User Information")

        age = st.sidebar.slider(
            t["age"],
            1,
            100,
            25
        )

        gender = st.sidebar.radio(
            t["gender"],
            [t["male"], t["female"]]
        )

        weight = st.sidebar.number_input(
            "Weight (kg)",
            20.0,
            200.0,
            70.0
        )

        height = st.sidebar.number_input(
            "Height (cm)",
            100.0,
            250.0,
            170.0
        )

        # -------------------------------------------------
        # BMI
        # -------------------------------------------------

        bmi = weight / ((height / 100) ** 2)

        # -------------------------------------------------
        # SYMPTOMS
        # -------------------------------------------------

        st.subheader("🧬 Symptom Severity")

        col1, col2 = st.columns(2)

        with col1:

            fever = st.slider("Fever", 0, 3, 0)
            cough = st.slider("Cough", 0, 3, 0)
            headache = st.slider("Headache", 0, 3, 0)
            fatigue = st.slider("Fatigue", 0, 3, 0)
            vomiting = st.slider("Vomiting", 0, 3, 0)

        with col2:

            body_pain = st.slider("Body Pain", 0, 3, 0)
            sore_throat = st.slider("Sore Throat", 0, 3, 0)
            breathing_issue = st.slider("Breathing Issue", 0, 3, 0)
            chest_pain = st.slider("Chest Pain", 0, 3, 0)
            diarrhea = st.slider("Diarrhea", 0, 3, 0)

        # -------------------------------------------------
        # DATASET
        # -------------------------------------------------

        data = pd.DataFrame({

            "fever": [3,2,1,0,3,2,1,0,3,2],
            "cough": [3,2,1,0,2,3,1,0,3,2],
            "headache": [2,3,1,0,2,3,1,0,2,1],
            "fatigue": [3,2,1,0,2,3,1,0,3,2],
            "vomiting": [0,1,0,0,2,1,0,0,1,2],
            "body_pain": [3,2,1,0,2,3,1,0,3,2],
            "sore_throat": [2,1,3,0,2,1,3,0,2,1],
            "breathing_issue": [3,2,0,0,3,2,0,0,3,2],
            "chest_pain": [2,1,0,0,2,1,0,0,2,1],
            "diarrhea": [1,2,0,0,1,2,0,0,1,2],

            "disease": [
                "COVID-19",
                "Flu",
                "Cold",
                "Healthy",
                "COVID-19",
                "Viral Fever",
                "Cold",
                "Healthy",
                "COVID-19",
                "Flu"
            ]
        })

        X = data.drop("disease", axis=1)
        y = data["disease"]

        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        model.fit(X, y)

        # -------------------------------------------------
        # PREDICTION
        # -------------------------------------------------

        if st.button(t["predict"]):

            input_data = np.array([[
                fever,
                cough,
                headache,
                fatigue,
                vomiting,
                body_pain,
                sore_throat,
                breathing_issue,
                chest_pain,
                diarrhea
            ]])

            prediction = model.predict(input_data)[0]

            probabilities = model.predict_proba(input_data)[0]

            confidence = round(
                np.max(probabilities) * 100,
                2
            )

            # -------------------------------------------------
            # RISK LEVEL
            # -------------------------------------------------

            total_score = (
                fever +
                cough +
                headache +
                fatigue +
                vomiting +
                body_pain +
                sore_throat +
                breathing_issue +
                chest_pain +
                diarrhea
            )

            if total_score <= 8:
                risk = "Low"
                risk_color = "green"

            elif total_score <= 18:
                risk = "Medium"
                risk_color = "orange"

            else:
                risk = "High"
                risk_color = "red"

            # -------------------------------------------------
            # SAVE HISTORY
            # -------------------------------------------------

            cursor.execute("""
            INSERT INTO history VALUES (?, ?, ?, ?, ?)
            """, (
                st.session_state.username,
                prediction,
                risk,
                confidence,
                str(datetime.now())
            ))

            conn.commit()

            # -------------------------------------------------
            # RESULT CARDS
            # -------------------------------------------------

            st.subheader("📋 Prediction Results")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f"""
                <div class="metric-card">
                <h3>🦠 Disease</h3>
                <h1>{prediction}</h1>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="metric-card">
                <h3>⚠️ Risk</h3>
                <h1 style="color:{risk_color}">
                {risk}
                </h1>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="metric-card">
                <h3>🎯 Confidence</h3>
                <h1>{confidence}%</h1>
                </div>
                """, unsafe_allow_html=True)

            # -------------------------------------------------
            # BMI ANALYSIS
            # -------------------------------------------------

            st.subheader("📏 BMI Analysis")

            bmi_col1, bmi_col2 = st.columns(2)

            with bmi_col1:
                st.metric("BMI", round(bmi, 2))

            with bmi_col2:

                if bmi < 18.5:
                    st.warning("Underweight")

                elif bmi < 25:
                    st.success("Normal Weight")

                elif bmi < 30:
                    st.warning("Overweight")

                else:
                    st.error("Obese")

            # -------------------------------------------------
            # SYMPTOM CHART
            # -------------------------------------------------

            symptom_df = pd.DataFrame({

                "Symptoms": [
                    "Fever",
                    "Cough",
                    "Headache",
                    "Fatigue",
                    "Vomiting",
                    "Body Pain",
                    "Sore Throat",
                    "Breathing Issue",
                    "Chest Pain",
                    "Diarrhea"
                ],

                "Severity": [
                    fever,
                    cough,
                    headache,
                    fatigue,
                    vomiting,
                    body_pain,
                    sore_throat,
                    breathing_issue,
                    chest_pain,
                    diarrhea
                ]
            })

            fig = px.bar(
                symptom_df,
                x="Symptoms",
                y="Severity",
                text="Severity",
                title="Symptom Severity Analysis"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # -------------------------------------------------
            # DISEASE PROBABILITY CHART
            # -------------------------------------------------

            probability_df = pd.DataFrame({
                "Disease": model.classes_,
                "Probability": probabilities
            })

            fig2 = px.pie(
                probability_df,
                names="Disease",
                values="Probability",
                title="Disease Probability"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            # -------------------------------------------------
            # AI RECOMMENDATION
            # -------------------------------------------------

            st.subheader("🤖 AI Recommendations")

            if risk == "Low":

                st.success("""
                ✅ Drink more water  
                ✅ Take proper rest  
                ✅ Eat healthy food  
                """)

            elif risk == "Medium":

                st.warning("""
                ⚠️ Monitor symptoms carefully  
                ⚠️ Take medication on time  
                ⚠️ Avoid crowded places  
                """)

            else:

                st.error("""
                🚨 Consult doctor immediately  
                🚨 Seek medical attention  
                🚨 Avoid physical stress  
                """)

    # =====================================================
    # HISTORY PAGE
    # =====================================================

    elif page == t["history"]:

        st.title("📜 My Health History")

        query = """
        SELECT * FROM history
        WHERE username=?
        """

        history_df = pd.read_sql_query(
            query,
            conn,
            params=(st.session_state.username,)
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    elif page == t["dashboard"]:

        st.title("📊 Admin Analytics Dashboard")

        users_df = pd.read_sql_query(
            "SELECT * FROM users",
            conn
        )

        history_df = pd.read_sql_query(
            "SELECT * FROM history",
            conn
        )

        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        m1, m2 = st.columns(2)

        with m1:
            st.metric(
                "👤 Total Users",
                len(users_df)
            )

        with m2:
            st.metric(
                "📄 Total Reports",
                len(history_df)
            )

        # -------------------------------------------------
        # ANALYTICS
        # -------------------------------------------------

        if not history_df.empty:

            # DISEASE TREND
            disease_count = (
                history_df["disease"]
                .value_counts()
                .reset_index()
            )

            disease_count.columns = [
                "Disease",
                "Count"
            ]

            fig1 = px.bar(
                disease_count,
                x="Disease",
                y="Count",
                text="Count",
                title="Most Common Diseases"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            # RISK TREND
            risk_count = (
                history_df["risk"]
                .value_counts()
                .reset_index()
            )

            risk_count.columns = [
                "Risk",
                "Count"
            ]

            fig2 = px.pie(
                risk_count,
                names="Risk",
                values="Count",
                title="Risk Level Distribution"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        else:

            st.info("No analytics data available")

    # =====================================================
    # LOGOUT
    # =====================================================

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()