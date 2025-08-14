import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="CSV Cleaner & Analyzer", page_icon="📊", layout="wide")
st.title("📊 CSV Cleaner & Analyzer")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    encoding = st.selectbox("Select encoding", ["utf-8", "latin-1", "utf-16"], index=0)
    try:
        df = pd.read_csv(uploaded_file, encoding=encoding)
        if df.empty:
            st.error("❌ Uploaded file is empty.")
            st.stop()
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()

    st.subheader("🔍 Raw Data")
    st.dataframe(df.head())

    # Store original stats
    original_rows = len(df)
    original_missing = df.isnull().sum().sum()
    original_exact_duplicates = df.duplicated().sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Original Rows", original_rows)
    col2.metric("Original Columns", df.shape[1])
    col3.metric("Missing Values", original_missing)
    col4.metric("Exact Duplicates", original_exact_duplicates)

    # Data types
    st.write("**Data Types:**")
    st.dataframe(pd.DataFrame({'Column': df.columns, 'Data Type': df.dtypes.astype(str)}))

    # Missing values
    st.write("**Missing values by column:**")
    missing_df = df.isnull().sum().to_frame('Missing Count')
    missing_df['Missing %'] = (missing_df['Missing Count'] / len(df) * 100).round(2)
    missing_df = missing_df[missing_df['Missing Count'] > 0]
    if not missing_df.empty:
        st.dataframe(missing_df)
    else:
        st.info("✅ No missing values found")

    st.subheader("🧹 Smart Cleaning & Deduplication")

    # Initialize cleaning flags
    text_standardized = False
    email_fixed = False
    gender_resolved = False
    age_imputed = False
    deduplicated = False

    # Checkbox for each cleaning operation
    if st.checkbox("Text standardized (trimmed, title case)"):
        for col in df.select_dtypes(include=['object']).columns:
            if col != 'Email':  # Handle email separately
                df[col] = df[col].astype(str).str.strip().str.title()  # "los angeles" → "Los Angeles"
        text_standardized = True
        st.success("✅ Text standardized (trimmed, title case)")

    if st.checkbox("Emails standardized and typos fixed"):
        email_corrections = {
            r'\b(gamil|gmaill|gmal)\.com\b': 'gmail.com',
            r'\b(hotmial|hotmaiil)\.com\b': 'hotmail.com',
            r'\b(yahho|yaho)\.com\b': 'yahoo.com'
        }
        df['Email'] = df['Email'].str.strip().str.lower().replace(email_corrections, regex=True)
        email_fixed = True
        st.success("✅ Emails standardized and typos fixed")

    if st.checkbox("Gender resolved by name (most common per person)"):
        if 'Gender' in df.columns and 'Name' in df.columns:
            mode_gender = df.dropna(subset=['Gender']).groupby('Name')['Gender'].agg(lambda x: x.mode()[0] if not x.mode().empty else None)
            null_gender = df['Gender'].isnull()
            df.loc[null_gender, 'Gender'] = df.loc[null_gender, 'Name'].map(mode_gender)
            gender_resolved = True
            st.success("✅ Gender resolved by name (most common per person)")
        else:
            st.warning("⚠️ 'Gender' or 'Name' column not found.")

    if st.checkbox("Missing Age filled using name-group median"):
        if 'Age' in df.columns and 'Name' in df.columns:
            # First: impute using same-name median
            age_by_name = df.groupby('Name')['Age'].transform('median')
            df['Age'] = df['Age'].fillna(age_by_name)
            # Then: fill remaining with global median
            df['Age'] = df['Age'].fillna(df['Age'].median())
            age_imputed = True
            st.success("✅ Missing Age filled using name-group median")
        else:
            st.warning("⚠️ 'Age' or 'Name' column not found.")

    if st.checkbox("Deduplicated by Name — one record per person"):
        if 'Name' in df.columns:
            # Sort to prioritize complete, valid entries
            df['is_complete'] = df.drop(columns=['Name'], errors='ignore').notnull().sum(axis=1)
            df['email_valid'] = df['Email'].str.contains('@').fillna(False)
            df = df.sort_values(['Name', 'is_complete', 'email_valid'], ascending=False)
            df = df.drop_duplicates(subset=['Name'], keep='first').drop(columns=['is_complete', 'email_valid'])
            df = df.sort_index().reset_index(drop=True)
            deduplicated = True
            st.success("✅ Deduplicated by Name — one record per person")
        else:
            st.warning("⚠️ 'Name' column not found.")

    # Final stats
    final_rows = len(df)
    final_missing = df.isnull().sum().sum()
    final_exact_duplicates = df.duplicated().sum()

    st.subheader("📊 Final Report")
    report_data = {
        "Metric": [
            "Original Rows",
            "Final Rows",
            "Records Removed",
            "Missing Values (Before)",
            "Missing Values (After)",
            "Duplicates (Before)",
            "Duplicates (After)"
        ],
        "Value": [
            original_rows,
            final_rows,
            original_rows - final_rows,
            original_missing,
            final_missing,
            original_exact_duplicates,
            final_exact_duplicates
        ]
    }
    st.dataframe(pd.DataFrame(report_data))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Before: Rows", original_rows)
        st.metric("Before: Missing", original_missing)
        st.metric("Before: Duplicates", original_exact_duplicates)
    with col2:
        st.metric("After: Rows", final_rows)
        st.metric("After: Missing", final_missing)
        st.metric("After: Duplicates", final_exact_duplicates)

    if final_rows == 0:
        st.error("❌ All rows were removed. Check data quality.")
        st.stop()

    # Visualizations
    st.subheader("📈 Visualizations")
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) > 0:
        if st.checkbox("Show Histogram"):
            col = st.selectbox("Histogram column", numeric_cols, key="hist")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.histplot(df[col].dropna(), kde=True, ax=ax)
            ax.set_title(f'Distribution of {col}')
            st.pyplot(fig)
            plt.close()

        if st.checkbox("Show Box Plot") and len(numeric_cols) > 0:
            col = st.selectbox("Box plot column", numeric_cols, key="box")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.boxplot(y=df[col], ax=ax)
            ax.set_title(f'Box Plot of {col}')
            st.pyplot(fig)
            plt.close()

        if st.checkbox("Show Correlation Heatmap") and len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax)
            ax.set_title("Correlation Heatmap")
            st.pyplot(fig)
            plt.close()
    else:
        st.warning("⚠️ No numeric columns for visualization.")

    # Final cleaned data
    st.subheader("✅ Final Cleaned Data (One Record Per Person)")
    st.dataframe(df)

    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Cleaned CSV",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

else:
    st.info("📁 Please upload a CSV file to get started")
    if st.button("Try with Sample Data"):
        sample_data = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank'],
            'Gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Female', 'Male'],
            'Age': [25, 30, 35, 28, 32, 27, 29, 31],
            'City': ['New York', 'Los Angeles', 'Chicago', 'Boston', 'Los Angeles', 'Seattle', 'San Francisco', 'Denver'],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT'],
            'Salary': [50000, 60000, 70000, 55000, 65000, 58000, 62000, 68000],
            'Email': [
                'john.doe@gmail.com', 'jane.smith@gmail.com', 'bob.jones@gmail.com',
                'alice.brown@gmail.com', 'charlie.wilson@gamil.com', 'diana.taylor@gmail.com',
                'eve.white@gmail.com', 'frank.miller@gmail.com'
            ]
        })
        # Add duplicates and inconsistencies
        dup_data = pd.DataFrame({
            'Name': ['John', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'John'],
            'Gender': ['Male', 'Male', 'Female', 'Female', 'Male', 'Male', 'Female', 'Male'],
            'Age': [25, 100, 35, 32, 27, 29, 31, 25],
            'City': ['New York', 'Boston', 'Chicago', 'Los Angeles', 'Seattle', 'San Francisco', 'Denver', 'New York'],
            'Department': ['IT', 'Finance', 'IT', 'IT', 'HR', 'Finance', 'IT', 'IT'],
            'Salary': [50000, 150000, 70000, 65000, 58000, 62000, 68000, 50000],
            'Email': [
                'john.doe2@gmail.com', 'alice.brown@gmail.com', 'bob.jones@gmail.com',
                'charlie.wilson@gmail.com', 'diana.taylor@gmail.com', 'eve.white@gmail.com',
                'frank.miller@gmail.com', 'john.doe3@gmail.com'
            ]
        })
        sample_data = pd.concat([sample_data, dup_data], ignore_index=True)
        st.session_state['sample'] = sample_data
        st.success("✅ Sample data loaded with duplicates and inconsistencies!")
        st.dataframe(sample_data)