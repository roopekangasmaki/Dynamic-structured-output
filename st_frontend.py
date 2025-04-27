import streamlit as st
import pandas as pd
import backend.extract_data as extract_data
import json


def uploader():
    """Upload a PDF file and return the file object."""
    uploaded_files = st.file_uploader("Choose a PDF file", type="pdf", accept_multiple_files=True)
    if uploaded_files is None:
        st.write("Please upload a PDF file.")
        return None
    processed_files = {}
    for file in uploaded_files:
        processed_files[file.name] = file.read()
    return processed_files

def schema_editor():
    """Schema editor for the fields to be extracted."""
    text_to_datatype_map = {
        "text": "string",
        "number": "float",
        "whole number": "int",
        #"date": "date", ## date type is not supported in Gemini API yet
        #"datetime": "datetime", ## datetime type is not supported in Gemini API yet
        #"time": "time", ## time type is not supported in Gemini API yet
        "TRUE/FALSE": "boolean"
    }
    data = pd.DataFrame(columns=["Field", "Type", "Description"])
    columns = {
        "Field": st.column_config.TextColumn("Field", help="Field to be extracted", required=True),
        "Type": st.column_config.SelectboxColumn("Type", help="Type of the field", required=True, options=text_to_datatype_map.keys()),
        "Description": st.column_config.TextColumn("Description", help="Description of the field", required=False),
    }
    schema_df = st.data_editor(data=data, num_rows="dynamic", key="schema_editor", column_config=columns)
    schema_df["Type"] = schema_df["Type"].map(text_to_datatype_map)
    return schema_df

def extract_data_from_files(uploaded_files, schema_df, api_key):
    """Extract data from the uploaded files based on the schema."""
    structured_df = pd.DataFrame(columns=schema_df["Field"])
    # Add file_name column if more than one file is uploaded
    if len(uploaded_files) > 1:
        structured_df["file_name"] = None
    for file_name, file_content in uploaded_files.items():
        # Assuming extract_data is a function that takes file content and schema and returns structured data
        schema_json = schema_df.to_json(orient="records")
        structured_data_json = extract_data.extract(file_content, schema_json, api_key)
        structured_data_json["file_name"] = file_name
        new_row = pd.Series(structured_data_json)
        new_row["file_name"] = file_name
        structured_df = pd.concat([structured_df, pd.DataFrame([structured_data_json])], ignore_index=True, join="inner")
        print(structured_df)
    st.write(f"Structured data from files:")
    st.dataframe(structured_df)

def main():
    st.title("Structured output from PDF files")

    st.write("This is a simple Streamlit app that converts PDF files to structured data. The app uses the free Gemini API to extract data " \
        "from the PDF files, so check Google for privacy policies and terms of service. " \
        "Most importantly, you shouldn't upload files you don't want Google to use for training their LLMs." \
        "Because the app uses the free Gemini API, it may hit the rate limit (15 files processed per minute and 1500 files per day at the moment). " \
        "If you hit the rate limit, please wait a few minutes and try again and if it still doesn't work, wait until next day. " )
    st.header("Upload a PDF file(s) to get started.")

    uploaded_files = uploader()

    if len(uploaded_files) > 0:
        st.write("Files uploaded successfully!")
    st.header("Schema Editor")
    st.write("Define the fields you want to extract from your PDF file(s). " \
            "Language can be anything. " \
            "Field is field name, type is type of field, " \
            "and description can be used to provide additional information. " \
            "If more than one file is uploaded, file_name column is automatically added.")
    schema_df = schema_editor()
    
    if st.button("Extract data"):
        extract_data_from_files(uploaded_files, schema_df, st.secrets["GEMINI_API_KEY"])

main()