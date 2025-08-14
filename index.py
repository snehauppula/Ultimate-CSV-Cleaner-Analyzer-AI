import streamlit as st
import pandas as pd
import google.generativeai as genai
from io import StringIO
import os

# Set page config
st.set_page_config(
    page_title="CSV Cleaner with Gemini AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CSV Cleaner with Gemini AI")

# Get API key from environment variable (more secure)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set")
    st.info("Please set your API key: `export GEMINI_API_KEY='your-api-key-here'`")
    st.stop()

# Configure Gemini API
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    st.success("✅ Connected to Gemini AI")
except Exception as e:
    st.error(f"❌ Failed to configure Gemini API: {e}")
    st.stop()

# 📤 File Upload
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    try:
        # Try different encodings if the default fails
        try:
            raw_df = pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)  # Reset file pointer
            raw_df = pd.read_csv(uploaded_file, encoding='latin-1')
        
        st.subheader("📄 Raw Data Preview")
        st.dataframe(raw_df.head())
        
        # Show basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", raw_df.shape[0])
        with col2:
            st.metric("Columns", raw_df.shape[1])
        with col3:
            st.metric("Missing Values", raw_df.isnull().sum().sum())

        # Convert file to text
        uploaded_file.seek(0)  # Reset file pointer
        csv_text = uploaded_file.getvalue().decode("utf-8")

        prompt = f"""
You are a data cleaning expert. Given this CSV data, perform the following preprocessing steps:

1. Remove duplicate rows
2. Fill missing values appropriately:
   - For numerical columns: use mean for missing values
   - For categorical/text columns: use mode (most frequent value)
3. Detect and remove outliers using IQR method for numerical columns
4. Ensure data types are appropriate
5. Return ONLY the cleaned CSV data in the same format (no explanations, just the CSV)

CSV Data:
{csv_text}

Return only the cleaned CSV data:
"""

        if st.button("🧹 Clean using Gemini AI"):
            st.info("🔄 Sending data to Gemini... Please wait.")
            
            with st.spinner("Gemini is analyzing and cleaning your data..."):
                try:
                    response = model.generate_content(prompt)
                    cleaned_csv = response.text.strip()

                    # Try to parse the response as CSV
                    try:
                        # Clean up the response if it has markdown formatting
                        if cleaned_csv.startswith('```csv'):
                            cleaned_csv = cleaned_csv.split('```csv')[1]
                        if cleaned_csv.endswith('```'):
                            cleaned_csv = cleaned_csv.rsplit('```', 1)[0]
                        
                        cleaned_csv = cleaned_csv.strip()
                        
                        cleaned_df = pd.read_csv(StringIO(cleaned_csv))
                        
                        st.success("✅ Data cleaned successfully!")
                        
                        # Show comparison
                        st.subheader("📊 Before vs After Comparison")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Before Cleaning:**")
                            st.metric("Rows", raw_df.shape[0])
                            st.metric("Missing Values", raw_df.isnull().sum().sum())
                        with col2:
                            st.write("**After Cleaning:**")
                            st.metric("Rows", cleaned_df.shape[0])
                            st.metric("Missing Values", cleaned_df.isnull().sum().sum())

                        st.subheader("✅ Cleaned Data Preview")
                        st.dataframe(cleaned_df.head())

                        # Download cleaned CSV
                        csv_bytes = cleaned_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download Cleaned CSV", 
                            csv_bytes, 
                            "cleaned_data.csv", 
                            "text/csv"
                        )

                    except Exception as parse_err:
                        st.error("⚠️ Could not parse Gemini response as CSV.")
                        st.write("**Raw Response:**")
                        st.text_area("Gemini Response:", cleaned_csv, height=200)
                        st.exception(parse_err)

                except Exception as gemini_err:
                    st.error("❌ Failed to get response from Gemini.")
                    st.exception(gemini_err)
                    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)

else:
    st.info("📁 Please upload a CSV file to get started")
    
    # Show sample data option
    if st.button("Try with Sample Data"):
        # Create sample data with issues
        sample_data = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank'],
            'Age': [25, 30, 35, 28, 32, 27, 29, 31],
            'Salary': [50000, 60000, 70000, 55000, 65000, 58000, 62000, 68000],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT'],
            'Experience': [2, 5, 8, 3, 6, 4, 7, 9]
        })
        
        # Add some missing values and duplicates for demonstration
        sample_data.loc[2, 'Age'] = None
        sample_data.loc[4, 'Salary'] = None
        sample_data = pd.concat([sample_data, sample_data.iloc[0:2]])  # Add duplicates
        
        st.success("✅ Sample data loaded! You can now test the AI cleaning features.")
        st.dataframe(sample_data)
