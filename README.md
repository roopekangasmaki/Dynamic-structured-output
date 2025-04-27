## Structured output from PDF files

### Description
This project provides a Streamlit-based application to extract structured data from PDF files. Users can upload PDF files, define a schema for the fields to be extracted, and process the files using the Google Gemini API. The extracted data is presented in a structured format suitable for analysis or integration.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Dynamic-structured-output.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Dynamic-structured-output
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
1. Run the Streamlit app:
   ```bash
   streamlit run st_frontend.py
   ```
2. Upload one or more PDF files through the app interface.
3. Define the schema for the fields you want to extract using the schema editor.
4. Click the "Extract data" button to process the files. The extracted data will be displayed in a table format within the app.

### Notes
- The app uses the Google Gemini API for document understanding. Ensure you have a valid Gemini API key stored in the `secrets.toml`. See https://docs.streamlit.io/develop/concepts/connections/secrets-management for information about where to save the file.
- Be mindful of the API rate limits: 15 files per minute and 1500 files per day.
- Avoid uploading sensitive files, as they may be used for training purposes by the API provider.

### License
This project is licensed under the MIT License. See the `LICENSE` file for details.
