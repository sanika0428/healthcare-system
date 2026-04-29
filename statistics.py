import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind,t
import numpy as np
from scipy.stats import norm

CSV_PATH = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\disease_data.csv"


def statistics_dashboard():
    st.title("📊 Medical Statistics Dashboard")
    # ---------------- LOAD DATA ----------------
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        st.error("No disease_data.csv found yet.")
        return

    # Normalize columns
    df.columns = df.columns.str.strip().str.lower()

    # Convert numeric safely
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["recovery time"] = pd.to_numeric(df["recovery time"], errors="coerce")
    df.dropna(inplace=True)

    if df.empty:
        st.warning("No data available for analysis.")
        return
    # =========================================================
    # 1️⃣ RECOVERY TIME VS AGE
    # =========================================================
    st.subheader("1️⃣ Recovery Time vs Age")

    fig1, ax1 = plt.subplots()
    ax1.scatter(df["age"], df["recovery time"])
    ax1.set_xlabel("Age")
    ax1.set_ylabel("Recovery Time (days)")
    ax1.set_title("Recovery Time vs Age")
    st.pyplot(fig1)
    correlation = df["age"].corr(df["recovery time"])
    st.write(f"📌 Correlation between Age and Recovery Time: **{correlation:.3f}**")

    # =========================================================
    # 2️⃣ DISEASE FREQUENCY
    # =========================================================
    st.subheader("2️⃣ Disease Frequency")

    disease_counts = df["disease"].value_counts()

    fig2, ax2 = plt.subplots()
    ax2.bar(disease_counts.index, disease_counts.values)
    ax2.set_xlabel("Disease")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Disease Frequency")
    plt.xticks(rotation=45)

    st.pyplot(fig2)

    # =========================================================
    # 3️⃣ DISEASE-SPECIFIC ANALYSIS
    # =========================================================
    st.subheader("3️⃣ Disease-Specific Analysis")

    selected_disease = st.selectbox(
        "Select Disease",
        sorted(df["disease"].unique())
    )

    disease_df = df[df["disease"] == selected_disease]

    # --- Age Distribution
    st.write(f"### Age Distribution for {selected_disease}")

    fig3, ax3 = plt.subplots()
    ax3.hist(disease_df["age"], bins=10)
    ax3.set_xlabel("Age")
    ax3.set_ylabel("Frequency")
    ax3.set_title(f"Age Distribution ({selected_disease})")

    st.pyplot(fig3)

    # --- Recovery Distribution
    st.write(f"### Recovery Time Distribution for {selected_disease}")

    fig4, ax4 = plt.subplots()
    ax4.hist(disease_df["recovery time"], bins=10)
    ax4.set_xlabel("Recovery Time (days)")
    ax4.set_ylabel("Frequency")
    ax4.set_title(f"Recovery Time Distribution ({selected_disease})")

    st.pyplot(fig4)

    # --- Age Group Frequency
    st.write(f"### {selected_disease} Frequency by Age Group")

    bins = [0, 18, 35, 50, 65, 100]
    labels = ["0-18", "19-35", "36-50", "51-65", "65+"]

    disease_df["age_group"] = pd.cut(disease_df["age"], bins=bins, labels=labels)

    age_group_counts = disease_df["age_group"].value_counts().sort_index()

    fig5, ax5 = plt.subplots()
    ax5.bar(age_group_counts.index.astype(str), age_group_counts.values)
    ax5.set_xlabel("Age Group")
    ax5.set_ylabel("Frequency")
    ax5.set_title(f"{selected_disease} Frequency by Age Group")

    st.pyplot(fig5)

    # Quick metrics
    st.subheader("📈 Quick Insights")

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Recovery (days)", f"{disease_df['recovery time'].mean():.1f}")
    col2.metric("Min Age", int(disease_df["age"].min()))
    col3.metric("Max Age", int(disease_df["age"].max()))

    # =========================================================
    # 4️⃣ HYPOTHESIS TESTING
    # =========================================================


    st.subheader("4️⃣ Hypothesis Testing (Male vs Female Recovery Time)")

    if "gender" not in df.columns:
        st.warning("Gender column not found in dataset.")
    else:
        male = df[df["gender"].str.lower() == "male"]["recovery time"]
        female = df[df["gender"].str.lower() == "female"]["recovery time"]

        if len(male) > 1 and len(female) > 1:
            t_stat, p_value = ttest_ind(male, female, equal_var=False)

        # Degrees of freedom (Welch–Satterthwaite approximation)
            n1, n2 = len(male), len(female)
            s1, s2 = male.var(), female.var()

            df_welch = ((s1/n1 + s2/n2)**2) / (((s1/n1)**2)/(n1-1) + ((s2/n2)**2)/(n2-1))

            st.write(f"Mean Recovery (Male): {male.mean():.2f} days")
            st.write(f"Mean Recovery (Female): {female.mean():.2f} days")
            st.write(f"T-Statistic: {t_stat:.4f}")
            st.write(f"P-Value: {p_value:.4f}")
            st.write(f"Degrees of Freedom: {df_welch:.2f}")

            alpha = 0.05

            if p_value < alpha:
                st.success("Reject H₀ → Significant difference in recovery time.")
            else:
                st.info("Fail to Reject H₀ → No significant difference detected.")

        # -------------------------
        # 📊 Bell Curve (t-distribution)
        # -------------------------
            fig, ax = plt.subplots()

            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df_welch)

            ax.plot(x, y)

        # Critical t-value (two-tailed)
            t_critical = t.ppf(1 - alpha/2, df_welch)

        # Shade rejection regions
            ax.fill_between(x, y, where=(x >= t_critical))
            ax.fill_between(x, y, where=(x <= -t_critical))

        # Mark observed t-statistic
            ax.axvline(t_stat, linestyle="--")

            ax.set_title("t-Distribution Bell Curve (Hypothesis Testing)")
            ax.set_xlabel("t-value")
            ax.set_ylabel("Probability Density")

            st.pyplot(fig)

        else:
            st.warning("Not enough data for hypothesis testing.")
