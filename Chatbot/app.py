import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import io
import streamlit.components.v1 as components
import time
import boto3
import re # For regex in dataframe search

# --- Set Page Config and Custom CSS ---
st.set_page_config(page_title="Power CSV - Advanced Data Explorer with AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Global App Container */
    .stApp {
        background-color: #000000; /* Pure black background */
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #E0E0E0; /* Light grey text */
        animation: fadeIn 1s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Main Content Area Elements */
    .st-emotion-cache-z5fcl4, .st-emotion-cache-uf99v8, .css-1d391kg, .css-1dp5yy6,
    .css-1fv8s86, .css-1cpxqw2, .css-1r6dm7m, .st-emotion-cache-h5rgjs, .st-emotion-cache-1jmve36 {
        background-color: #000000;
    }

    /* Sidebar Styling */
    .st-emotion-cache-1ldf15l { /* Target sidebar container (adjust if this class changes) */
        background-color: #0A0A0A; /* Very dark grey for sidebar */
        border-right: 1px solid #1A1A1A; /* Darker border */
        padding-top: 2rem;
        box-shadow: 2px 0 10px rgba(0,0,0,0.5); /* More pronounced shadow on dark theme */
        color: #E0E0E0; /* Light text for sidebar */
    }
    /* Ensure text within sidebar components is also light */
    .st-emotion-cache-1ldf15l h3, .st-emotion-cache-1ldf15l h4,
    .st-emotion-cache-1ldf15l label, .st-emotion-cache-1ldf15l p {
        color: #E0E0E0;
    }

    /* Titles and Headers */
    h1 {
        color: #00FF99; /* Neon Green for main title */
        font-size: 3.5em;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #00FF99; /* Stronger neon separator */
        letter-spacing: 2px;
        text-shadow: 0 0 10px #00FF99, 0 0 20px #00FF99; /* Neon glow effect */
        animation: pulseGlow 2s infinite alternate;
    }

    @keyframes pulseGlow {
        from { text-shadow: 0 0 10px #00FF99, 0 0 20px #00FF99; }
        to { text-shadow: 0 0 15px #00FF99, 0 0 30px #00FF99; }
    }

    h2 {
        color: #E0E0E0; /* Light grey for section headers */
        border-bottom: 1px solid #333333;
        padding-bottom: 0.5rem;
        margin-top: 2.5rem;
        font-size: 2em;
        text-shadow: 0 0 5px rgba(255,255,255,0.2);
    }
    h3 {
        color: #00CC77; /* Slightly darker neon green for sub-headers */
        margin-top: 1.5rem;
        font-size: 1.6em;
    }
    h4 { /* Added for sidebar headers etc. */
        color: #B0B0B0;
        font-size: 1.2em;
    }

    /* Buttons */
    .stButton>button {
        background-color: #00FF99; /* Neon Green */
        color: #000000; /* Black text on neon for contrast */
        border-radius: 12px;
        border: none;
        padding: 0.8em 1.8em;
        font-size: 1.1em;
        font-weight: bold;
        transition: all 0.4s ease-in-out;
        box-shadow: 0 4px 15px rgba(0,255,153,0.4); /* Neon glow shadow */
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        background-color: #00E689; /* Darker neon green on hover */
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 6px 20px rgba(0,255,153,0.6); /* More intense neon glow */
    }
    .stButton>button:disabled {
        background-color: #333333;
        color: #888888;
        box-shadow: none;
        cursor: not-allowed;
    }

    /* Multiselect, Selectbox, and Text Inputs */
    .stMultiSelect, .stSelectbox, .stTextInput, .stDateInput, .stSlider, .stRadio {
        margin-bottom: 1.2rem;
    }
    .stMultiSelect>div>div, .stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>div>input, .stSlider>div>div {
        border-radius: 10px;
        border: 1px solid #444444; /* Darker grey border */
        padding: 0.6rem 1rem;
        box-shadow: inset 0 1px 5px rgba(0,0,0,0.4); /* Subtle inner shadow */
        background-color: #1A1A1A; /* Dark grey for inputs */
        color: #E0E0E0; /* Light text within inputs */
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    /* Style for text area inputs */
    .stTextInput textarea {
        border-radius: 10px;
        border: 1px solid #444444;
        padding: 0.6rem 1rem;
        box-shadow: inset 0 1px 5px rgba(0,0,0,0.4);
        background-color: #1A1A1A;
        color: #E0E0E0;
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    .stTextInput textarea:focus {
        border-color: #00FF99;
        box-shadow: inset 0 1px 5px rgba(0,0,0,0.4), 0 0 8px rgba(0,255,153,0.5);
        outline: none; /* Remove default outline */
    }


    .stMultiSelect>div>div:focus-within, .stSelectbox>div>div:focus-within, .stTextInput>div>div>input:focus,
    .stDateInput>div>div>input:focus, .stSlider>div>div:focus-within {
        border-color: #00FF99; /* Neon green focus */
        box-shadow: inset 0 1px 5px rgba(0,0,0,0.4), 0 0 8px rgba(0,255,153,0.5);
    }
    .stMultiSelect label, .stSelectbox label, .stTextInput label, .stDateInput label, .stSlider label, .stRadio label {
        font-weight: bold;
        color: #B0B0B0;
        margin-bottom: 0.5rem;
        display: block;
    }
    /* Adjust dropdown background for selectbox/multiselect options */
    .st-emotion-cache-w0qg0u { /* This targets the actual dropdown list container (may vary) */
        background-color: #1A1A1A !important;
        color: #E0E0E0 !important;
        border-radius: 8px;
        border: 1px solid #444444;
    }
    .st-emotion-cache-w0qg0u div[role="option"] {
        color: #E0E0E0 !important;
        padding: 0.8rem 1rem;
    }
    .st-emotion-cache-w0qg0u div[role="option"]:hover {
        background-color: #333333 !important; /* Darker grey on hover */
    }
    .st-emotion-cache-w0qg0u div[aria-selected="true"] {
        background-color: #005533 !important; /* Slightly green for selected */
    }


    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #333333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6); /* Stronger shadow */
    }
    .stDataFrame table {
        background-color: #111111; /* Secondary background for table */
        color: #E0E0E0;
    }
    .stDataFrame table thead th {
        background-color: #222222; /* Darker grey for table header */
        color: #00FF99; /* Neon green for header text */
        font-weight: bold;
        padding: 0.9rem 1.2rem;
        border-bottom: 1px solid #555555;
    }
    .stDataFrame table tbody tr {
        background-color: #111111;
    }
    .stDataFrame table tbody tr:nth-child(even) {
        background-color: #181818; /* Slightly darker grey for even rows */
    }
    .stDataFrame table tbody tr:hover {
        background-color: #2A2A2A; /* Darker grey on hover */
        transition: background-color 0.2s ease-in-out;
    }
    .stDataFrame table tbody td {
        border-right: 1px solid #333333;
        border-bottom: 1px solid #333333;
        padding: 0.7rem 1rem;
    }

    /* Info, Success, Error messages */
    .stAlert {
        border-radius: 10px;
        padding: 1.2rem;
        font-size: 1.05em;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    }
    .stAlert.info {
        background-color: #003366;
        color: #99CCFF;
        border-left: 6px solid #007bff;
    }
    .stAlert.success {
        background-color: #004D33; /* Darker green */
        color: #99FF99;
        border-left: 6px solid #00FF99; /* Neon green border */
    }
    .stAlert.error {
        background-color: #660000; /* Darker red */
        color: #FF9999;
        border-left: 6px solid #dc3545;
    }

    /* Code blocks */
    .stCodeBlock {
        background-color: #0A0A0A; /* Very dark grey for code blocks */
        color: #00FF99; /* Neon green for code */
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #333333;
        overflow-x: auto;
        font-family: 'Fira Code', 'Cascadia Code', monospace; /* Monospaced font */
        box-shadow: inset 0 0 10px rgba(0,255,153,0.1);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 25px;
        padding: 10px 0;
        border-bottom: 2px solid #333333;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        background-color: #1A1A1A; /* Dark grey for inactive tabs */
        height: 55px;
        padding: 0 25px;
        gap: 10px;
        border-bottom: 5px solid transparent;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 1.2em;
        font-weight: bold;
        color: #B0B0B0;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2A2A2A;
        border-bottom: 5px solid #00CC77; /* Slightly darker neon on hover */
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #000000; /* Black for active tab */
        border-bottom: 5px solid #00FF99; /* Neon green for active tab indicator */
        box-shadow: 0 -3px 15px rgba(0,0,0,0.7);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] > div[data-testid="stMarkdownContainer"] > p {
        color: #00FF99; /* Neon green for active tab text */
    }

    /* Spinner style */
    .stSpinner > div > div {
        color: #00FF99; /* Neon green for spinner */
    }

    /* Speech-to-text button (custom HTML) */
    #btnSpeak {
        background-color: #007bff; /* Keep blue for this specific button for contrast */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.8em 1.5em;
        font-size: 1.2em;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        cursor: pointer;
        margin-top: 1rem;
    }
    #btnSpeak:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    #outputText {
        margin-top: 1rem;
        font-size: 1.1em;
        color: #B0B0B0;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    ::-webkit-scrollbar-track {
        background: #1A1A1A; /* Dark grey track */
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #005533; /* Darker neon green thumb */
        border-radius: 10px;
        border: 2px solid #1A1A1A; /* Adds a border to the thumb */
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #007744; /* Lighter neon green on hover */
    }

</style>
""", unsafe_allow_html=True)


# --- AWS Bedrock Claude Integration (Original with error handling) ---
def call_claude_bedrock(question: str) -> str:
    """
    Calls the Claude model on AWS Bedrock with the given question.
    Requires AWS credentials configured in .streamlit/secrets.toml.
    """
    try:
        # Load AWS credentials from secrets.toml
        aws_access_key = st.secrets["aws"]["aws_access_key_id"]
        aws_secret_key = st.secrets["aws"]["aws_secret_access_key"]
        region = st.secrets["aws"].get("region", "us-east-1")

        bedrock = boto3.client(
            "bedrock-runtime",
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

        prompt = "Human: {}\nAssistant:".format(question)

        body = {
            "prompt": prompt,
            "max_tokens_to_sample": 1000,
            "temperature": 0.7,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"]
        }

        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps(body),
            contentType="application/json"
        )

        response_body = json.loads(response["body"].read().decode())
        return response_body.get("completion", "No response from Zilli.")
    except Exception as e:
        if "No credentials found" in str(e) or "The security token included in the request is invalid" in str(e) or "InvalidAccessKeyId" in str(e):
            return "❌ Error: AWS credentials not found or invalid. Please configure your `secrets.toml` file correctly in the `.streamlit` directory. Refer to Streamlit's documentation on secrets management."
        elif "Could not connect to the endpoint URL" in str(e) or "Connect timeout" in str(e):
            return "❌ Error: Could not connect to AWS Bedrock. Please check your internet connection or AWS region."
        elif "The provided model identifier is not valid" in str(e) or "ModelNotFoundException" in str(e):
            return "❌ Error: The specified Bedrock model 'anthropic.claude-v2' might not be available in your region or is incorrect. Please verify the model ID."
        return "❌ An unexpected error occurred when calling Zilli: {}".format(str(e))

# --- AWS Bedrock Claude Integration (For the new chatbot) ---
# This version is simplified for the specific chatbot interaction as error handling is done in the main function.
def call_bedrock_claude_chatbot(prompt_text: str) -> str:
    """Calls AWS Bedrock (Zilli) for a given prompt, specifically for the chatbot."""
    try:
        aws_access_key = st.secrets["aws"]["aws_access_key_id"]
        aws_secret_key = st.secrets["aws"]["aws_secret_access_key"]
        region = st.secrets["aws"].get("region", "us-east-1")

        bedrock = boto3.client(
            "bedrock-runtime",
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

        body = {
            "prompt": "Human: {}\nAssistant:".format(prompt_text),
            "max_tokens_to_sample": 1000,
            "temperature": 0.7,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"]
        }

        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps(body),
            contentType="application/json"
        )
        response_body = json.loads(response["body"].read().decode())
        return response_body.get("completion", "No response from Zilli.")
    except Exception as e:
        # Return a simple error for the chatbot to display
        return "Error: Could not reach Bedrock. Please check AWS credentials/region or model access. Details: {}".format(str(e))

# --- Helper Functions ---

def escape_sql_identifier(identifier):
    """Escapes SQL identifiers (e.g., column names) by enclosing them in double quotes."""
    # Use format() or concatenation
    return '"{}"'.format(identifier.replace('"', '""'))

def generate_sql(table, select_cols, filters, date_filters, global_search, order_by=None, limit=None, custom_where=None):
    """Generates a SQL SELECT statement based on provided filters."""
    if not select_cols:
        select_clause = "*"
    else:
        select_clause = ", ".join([escape_sql_identifier(col) for col in select_cols])

    where_clauses = []

    if global_search:
        search_conditions = []
        for col in select_cols: # Only search in selected columns for efficiency
            # Corrected: Using str.format() to build the string
            search_conditions.append("{} ILIKE '%{}%'".format(escape_sql_identifier(col), global_search.replace("'", "''")))
        if search_conditions:
            where_clauses.append("({})".format(' OR '.join(search_conditions)))

    for col, cond in filters.items():
        escaped_col = escape_sql_identifier(col)
        if cond[0] == "range":
            if pd.api.types.is_numeric_dtype(df[col]): # Use original df for type check
                where_clauses.append("{} >= {} AND {} <= {}".format(escaped_col, cond[1][0], escaped_col, cond[1][1]))
            else:
                # Handle non-numeric range (e.g., string length if applicable, or skip)
                pass
        elif cond[0] == "in":
            if cond[1]:
                # Escape each value in the list for SQL string literal
                escaped_values = ["'{}'".format(str(val).replace("'", "''")) for val in cond[1]]
                where_clauses.append("{} IN ({})".format(escaped_col, ', '.join(escaped_values)))
            else:
                # If no values selected, effectively filters out everything (or nothing depending on desired logic)
                # For now, if list is empty, effectively means no filter on this column based on 'in'
                pass
        elif cond[0] == "contains":
            if cond[1]:
                # Corrected: Using str.format() to build the string
                where_clauses.append("{} ILIKE '%{}%'".format(escaped_col, cond[1].replace("'", "''")))

    for col, (start, end) in date_filters.items():
        escaped_col = escape_sql_identifier(col)
        start_str = start.strftime("'%Y-%m-%d %H:%M:%S'")
        end_str = end.strftime("'%Y-%m-%d %H:%M:%S'")
        where_clauses.append("{} >= {} AND {} <= {}".format(escaped_col, start_str, escaped_col, end_str))

    if custom_where:
        where_clauses.append("({})".format(custom_where)) # Wrap custom where in parentheses

    where_clause = ""
    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)

    order_by_clause = ""
    if order_by:
        order_terms = ["{} {}".format(escape_sql_identifier(col), direction) for col, direction in order_by]
        order_by_clause = "ORDER BY {}".format(', '.join(order_terms))

    limit_clause = ""
    if limit is not None and limit > 0:
        limit_clause = "LIMIT {}".format(int(limit))

    sql_query = "SELECT {} FROM {} {} {} {}".format(select_clause, escape_sql_identifier(table), where_clause, order_by_clause, limit_clause).strip()
    return sql_query

def search_dataframe_for_answer(df_search: pd.DataFrame, question: str) -> str or None:
    """
    Attempts to find a direct answer to common questions within the DataFrame.
    Returns a string answer or None if no direct answer is found.
    """
    question_lower = question.lower()

    if "count" in question_lower and "rows" in question_lower:
        return "The number of rows in the filtered data is: **{}**".format(df_search.shape[0])

    if "columns" in question_lower or "fields" in question_lower:
        return "The columns in the filtered data are: **{}**".format(', '.join(df_search.columns.tolist()))

    numeric_cols = df_search.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        col_lower = col.lower()
        if "average {}".format(col_lower) in question_lower or "mean {}".format(col_lower) in question_lower:
            avg_val = df_search[col].mean()
            return "The average of '{}' is: **{:.2f}**".format(col, avg_val)
        if "sum {}".format(col_lower) in question_lower:
            sum_val = df_search[col].sum()
            return "The sum of '{}' is: **{:.2f}**".format(col, sum_val)
        if "max {}".format(col_lower) in question_lower or "highest {}".format(col_lower) in question_lower:
            max_val = df_search[col].max()
            return "The maximum value of '{}' is: **{}**".format(col, max_val)
        if "min {}".format(col_lower) in question_lower or "lowest {}".format(col_lower) in question_lower:
            min_val = df_search[col].min()
            return "The minimum value of '{}' is: **{}**".format(col, min_val)

    # Try to find specific value counts for categorical columns
    for col in df_search.select_dtypes(include=['object', 'category']).columns:
        col_lower = col.lower()
        # Look for phrases like "count of X in Y" or "how many X"
        # Using string concatenation and .format() for regex pattern
        match = re.search('count of (.*?) in {}'.format(re.escape(col_lower)), question_lower)
        if not match:
            match = re.search('how many (.*?) (?:in|from)? {}'.format(re.escape(col_lower)), question_lower)

        if match:
            value_to_count = match.group(1).strip()
            # Perform a case-insensitive search
            count = df_search[col].astype(str).str.contains(value_to_count, case=False, na=False).sum()
            if count > 0:
                return "There are **{}** occurrences of '{}' in the '{}' column.".format(count, value_to_count, col)
            else:
                return None # No direct count found for that specific value

    return None

def speech_to_text_component():
    """Embeds JavaScript for speech-to-text functionality."""
    # JavaScript for speech recognition
    # It targets the Streamlit text area by its data-testid and dispatches events
    js_code = """
    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const btn = document.getElementById('btnSpeak');
    const outputText = document.getElementById('outputText');
    let textArea = null; // Will store the reference to the Streamlit text area

    // Function to find the Streamlit text area dynamically
    function findStreamlitTextArea() {
        // Look for the specific data-testid used by Streamlit for text_area
        // The key 'chatbot_question_input' is used in st.text_area(key="chatbot_question_input")
        // The testid combines stTextInput with the key for text areas.
        // It's usually something like 'st-Ds2V' or similar with dynamic ID.
        // A more robust way to find it for text_area is by looking for the input within the div with specific label/key test id.
        // Or, more reliably, use a generic `textarea` selector and check its parent/attributes.
        const allTextAreas = document.querySelectorAll('textarea[data-testid="stTextInput"]');
        for (let i = 0; i < allTextAreas.length; i++) {
            // Check if this textarea is the one associated with our 'chatbot_question_input' key
            // Streamlit text area key usually appears in the parent structure or element data attributes
            // Direct data-testid attribute might not contain the full key string
            // Let's rely on the most common stTextInput data-testid
            if (allTextAreas[i].parentElement && allTextAreas[i].parentElement.parentElement && allTextAreas[i].parentElement.parentElement.labels && allTextAreas[i].parentElement.parentElement.labels[0] && allTextAreas[i].parentElement.parentElement.labels[0].textContent.includes('Ask a question about your data:')) {
                 textArea = allTextAreas[i];
                 console.log("Found Streamlit text area:", textArea);
                 return textArea;
            }
        }
        console.warn("Streamlit text area not found. Retrying...");
        return null;
    }

    // Attempt to find the text area after a short delay to ensure DOM is ready
    setTimeout(() => {
        textArea = findStreamlitTextArea();
    }, 1000); // Wait 1 second

    btn.onclick = () => {
        if (!textArea) {
            textArea = findStreamlitTextArea(); // Try again if not found initially
            if (!textArea) {
                outputText.textContent = 'Error: Chatbot input box not found. Please refresh the page.';
                return;
            }
        }

        recognition.start();
        outputText.textContent = 'Listening...';
        btn.disabled = true;
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        outputText.textContent = 'You said: ' + transcript;

        if (textArea) {
            textArea.value = transcript;
            // Dispatch 'input' and 'change' events to notify Streamlit about the update
            const inputEvent = new Event('input', { bubbles: true });
            const changeEvent = new Event('change', { bubbles: true });
            textArea.dispatchEvent(inputEvent);
            textArea.dispatchEvent(changeEvent);
            console.log("Text area updated with:", transcript);
        } else {
            console.error("Text area not available to update.");
        }
    };

    recognition.onend = () => {
        outputText.textContent = outputText.textContent === 'Listening...' ? 'No speech detected.' : outputText.textContent;
        btn.disabled = false;
    };

    recognition.onerror = (event) => {
        outputText.textContent = 'Error: ' + event.error;
        btn.disabled = false;
        console.error('Speech recognition error:', event.error);
    };
    </script>
    <button id="btnSpeak">🎤 Speak</button>
    <p id="outputText">Click the microphone to speak</p>
    """
    components.html(js_code, height=120)


# --- Initial File Uploader (outside tabs, as it affects all) ---
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if not uploaded_file:
    # If no file is uploaded, we will only show the Home tab
    # The rest of the app logic will be skipped until a file is uploaded.
    # This is handled by the `st.stop()` below.
    pass # Let the Home tab handle the initial display.

# --- Data Loading and Caching ---
# Only load data if a file is uploaded
df = None
datetime_cols = []
filtered_df = pd.DataFrame() # Initialize as empty DataFrame
global_search = ""
select_cols = []
filters = {}
date_filters = {}

if uploaded_file:
    @st.cache_data
    def load_data(file):
        """Loads CSV data with robust date parsing."""
        try:
            df_loaded = pd.read_csv(file, parse_dates=True, infer_datetime_format=True)
        except Exception:
            df_loaded = pd.read_csv(file)
        return df_loaded

    df = load_data(uploaded_file)

    # Detect datetime columns
    datetime_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns.tolist()

    # --- Sidebar Filters (only appear if file is uploaded) ---
    st.sidebar.header("Filter Options")
    st.sidebar.markdown("### 🔍 Data Filters")

    global_search = st.sidebar.text_input("Global search (text)", help="Searches for text across all displayed columns.")
    all_columns = df.columns.tolist()
    select_cols = st.sidebar.multiselect("Columns to display", options=all_columns, default=all_columns,
                                         help="Select which columns you want to see in the data preview.")

    filters = {}
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Column Filters")
    for col in all_columns:
        col_dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(col_dtype):
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            if min_val == max_val:
                st.sidebar.write("*{}: Single value {} (no range filter needed)*".format(col, min_val))
                filters[col] = ("range", (min_val, max_val))
            else:
                val_range = st.sidebar.slider("{} range".format(col), min_val, max_val, (min_val, max_val),
                                              help="Filter numeric range for {}.".format(col))
                filters[col] = ("range", val_range)
        elif col in datetime_cols:
            pass
        else:
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) <= 50 and len(unique_vals) > 0:
                selected_vals = st.sidebar.multiselect("{} values".format(col), options=unique_vals, default=unique_vals,
                                                       help="Select specific values for {}.".format(col))
                filters[col] = ("in", selected_vals)
            elif len(unique_vals) == 0:
                st.sidebar.info("'{0}' has no non-null values.".format(col))
            else:
                txt_filter = st.sidebar.text_input("{} contains (text filter)".format(col), help="Filter rows where {} contains this text (case-insensitive).".format(col))
                if txt_filter:
                    filters[col] = ("contains", txt_filter)

    if datetime_cols:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Date Filters")
    date_filters = {}
    for col in datetime_cols:
        min_date = df[col].min()
        max_date = df[col].max()
        start_date_input = min_date.date()
        end_date_input = max_date.date()

        start_date = st.sidebar.date_input("{} start date".format(col), value=start_date_input,
                                           min_value=start_date_input, max_value=end_date_input,
                                           help="Select the start date for filtering {}.".format(col))
        end_date = st.sidebar.date_input("{} end date".format(col), value=end_date_input,
                                         min_value=start_date_input, max_value=end_date_input,
                                         help="Select the end date for filtering {}.".format(col))

        if start_date > end_date:
            st.sidebar.error("Start date must be before or equal to end date for {}".format(col))
        else:
            date_filters[col] = (pd.to_datetime(start_date), pd.to_datetime(end_date).replace(hour=23, minute=59, second=59))

    def apply_filters(df_in):
        """Applies all selected filters to the DataFrame."""
        df_out = df_in.copy()
        for col, cond in filters.items():
            if cond[0] == "range":
                df_out = df_out[(df_out[col].fillna(df_out[col].min()) >= cond[1][0]) & (df_out[col].fillna(df_out[col].max()) <= cond[1][1])]
            elif cond[0] == "in":
                df_out = df_out[df_out[col].isin(cond[1])]
            elif cond[0] == "contains":
                df_out = df_out[df_out[col].astype(str).str.contains(cond[1], case=False, na=False)]

        if global_search:
            mask = df_out.apply(lambda row: row.astype(str).str.contains(global_search, case=False, na=False).any(), axis=1)
            df_out = df_out[mask]

        for col, (start, end) in date_filters.items():
            df_out = df_out[(df_out[col] >= start) & (df_out[col] <= end)]


        return df_out

    filtered_df = apply_filters(df)
    # Ensure select_cols are applied to filtered_df, handling cases where a column might be missing after filtering
    filtered_df = filtered_df[[col for col in select_cols if col in filtered_df.columns]]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Rows after filtering: **{}** of **{}**".format(filtered_df.shape[0], df.shape[0]))
else:
    # If no file uploaded, stop execution here and only render the Home tab.
    # The rest of the app (tabs, filters, etc.) will not be rendered.
    pass


# --- Home Tab ---
def home_tab():
    st.title("Power CSV - Advanced Data Explorer with AI")
    st.markdown("""
    Welcome to **Power CSV**, your all-in-one solution for advanced CSV data exploration and analysis, powered by AI.
    
    Upload your CSV file to unlock a suite of powerful features:
    
    * **📊 Data & Profile:** Get a quick overview and detailed statistical profiles of your data.
    * **📄 SQL Builder:** Generate custom SQL queries based on your filters and selections.
    * **✅ Data Quality Checks:** Identify and understand missing values, duplicates, and data type inconsistencies.
    * **📦 Export & Filters:** Easily download your filtered data and manage your active filters.
    * **✍️ Code Converter:** Convert code snippets between various programming languages using AI.
    * **⚙️ STTM Assistant:** Generate structured Standardized Transformation and Mapping rules with AI assistance.
    * **💬 Ask Zilli:** Ask natural language questions about your data and get insights from an AI assistant.
    * **📈 Dashboard:** Visualize your data with interactive charts and uncover hidden patterns.
    
    Get started by uploading your CSV file on the left sidebar!
    """)
    st.markdown("---")
    st.subheader("Why Power CSV?")
    st.markdown("""
    * **Intuitive Interface:** Easy to navigate and use, even for non-technical users.
    * **AI-Powered Insights:** Leverage cutting-edge AI for code conversion, STTM generation, and data querying.
    * **Comprehensive Tools:** From basic filtering to advanced data quality and visualization, everything you need in one place.
    * **Interactive & Responsive:** Works seamlessly on any device, adapting to your screen size.
    * **Secure:** Built with privacy and security in mind, especially when integrating with cloud AI services.
    """)
    st.markdown("---")
    st.info("💡 **Tip:** Upload a CSV file to enable all features and start your data journey!")

# --- Data Quality Checks Tab ---
def data_quality_checks_tab(df_to_check: pd.DataFrame):
    st.header("Data Quality Checks")
    st.markdown("Perform comprehensive data quality checks on your uploaded dataset, including missing values, duplicates, and data type inconsistencies.")

    if df_to_check.empty:
        st.warning("The dataset is empty. Please upload data or adjust filters to perform quality checks.")
        return

    st.subheader("1. Missing Values Analysis")
    missing_data = df_to_check.isnull().sum()
    missing_percentage = (df_to_check.isnull().sum() / len(df_to_check)) * 100
    missing_df = pd.DataFrame({
        'Missing Count': missing_data,
        'Missing Percentage (%)': missing_percentage
    }).sort_values(by='Missing Count', ascending=False)

    missing_df_display = missing_df[missing_df['Missing Count'] > 0]

    if missing_df_display.empty:
        st.success("🎉 No missing values found in your dataset!")
    else:
        st.write("Columns with missing values:")
        st.dataframe(missing_df_display, use_container_width=True)

        fig_missing = px.bar(
            missing_df_display.reset_index(),
            x='index',
            y='Missing Count',
            title='Missing Values Count Per Column',
            labels={'index': 'Column', 'Missing Count': 'Count'},
            color='Missing Percentage (%)',
            color_continuous_scale=px.colors.sequential.Sunset
        )
        fig_missing.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                  font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                  xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
        st.plotly_chart(fig_missing, use_container_width=True)

    st.subheader("2. Duplicate Rows Analysis")
    duplicates_count = df_to_check.duplicated().sum()
    if duplicates_count == 0:
        st.success("✅ No duplicate rows found in your dataset.")
    else:
        st.warning("⚠️ Found **{}** duplicate rows.".format(duplicates_count))
        if st.checkbox("Show duplicate rows", key="show_duplicates_checkbox"):
            st.dataframe(df_to_check[df_to_check.duplicated(keep=False)].sort_values(by=df_to_check.columns.tolist()), use_container_width=True)
        if st.button("Remove Duplicate Rows (in displayed data)", key="remove_duplicates_button"):
            df_to_check = df_to_check.drop_duplicates().copy()
            st.success("Removed {} duplicate rows. New row count: {}".format(duplicates_count, df_to_check.shape[0]))
            st.dataframe(df_to_check, use_container_width=True)
            st.info("Note: This removal applies only to the displayed data for this session. It does not alter your original uploaded file.")

    st.subheader("3. Data Type Overview & Inconsistencies")
    st.write("Current detected data types:")
    st.dataframe(df_to_check.dtypes.astype(str).reset_index().rename(columns={'index': 'Column', 0: 'Data Type'}), use_container_width=True)
    st.info("Pay attention to 'object' types that might contain mixed data or dates/numbers that weren't parsed correctly.")

    st.subheader("4. Unique Value Counts Per Column")
    unique_counts = df_to_check.nunique().reset_index()
    unique_counts.columns = ['Column', 'Unique Count']
    st.dataframe(unique_counts.sort_values(by='Unique Count', ascending=False), use_container_width=True)
    st.info("High unique counts might indicate IDs or highly granular data. Low unique counts (e.g., 1) might indicate constant columns.")

    st.subheader("5. Numeric Value Checks")
    numeric_cols = df_to_check.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        negative_counts = {col: (df_to_check[col] < 0).sum() for col in numeric_cols}
        negative_cols = {k: v for k, v in negative_counts.items() if v > 0}
        if negative_cols:
            st.warning("⚠️ Columns with negative values detected:")
            st.write(negative_cols)
        else:
            st.success("✅ No negative values found in numeric columns.")

        zero_counts = {col: (df_to_check[col] == 0).sum() for col in numeric_cols}
        zero_cols = {k: v for k, v in zero_counts.items() if v > 0}
        if zero_cols:
            st.info("ℹ️ Columns with zero values detected:")
            st.write(zero_cols)
        else:
            st.success("✅ No zero values found in numeric columns.")
    else:
        st.info("No numeric columns found to perform numeric value checks.")

    st.subheader("6. Constant Columns (Single Unique Value)")
    constant_cols = [col for col in df_to_check.columns if df_to_check[col].nunique(dropna=False) <= 1]
    if constant_cols:
        st.warning("⚠️ The following columns have only one unique value (or all are NaN):")
        for col in constant_cols:
            st.write("- `{}`: Value = `{}`".format(col, df_to_check[col].dropna().iloc[0] if not df_to_check[col].dropna().empty else 'All NaN'))
    else:
        st.success("✅ No constant columns found.")

    st.subheader("7. AI-Powered Cleaning Suggestions")
    st.markdown("Based on the data quality issues detected, the AI can suggest Python code snippets for common cleaning tasks.")

    if st.button("Generate Cleaning Suggestions with AI", key="generate_cleaning_suggestions"):
        if not df_to_check.empty:
            issues_summary = []
            if not missing_df_display.empty:
                issues_summary.append("Missing values in columns: {}".format(missing_df_display.index.tolist()))
            if duplicates_count > 0:
                issues_summary.append("Duplicate rows: {} found.".format(duplicates_count))
            if negative_cols:
                issues_summary.append("Negative values in numeric columns: {}".format(list(negative_cols.keys())))
            if constant_cols:
                issues_summary.append("Constant columns (single unique value): {}".format(constant_cols))

            if not issues_summary:
                st.info("No major data quality issues detected to suggest cleaning actions for. Great job! 👍")
            else:
                cleaning_prompt = (
                    "Human: I have a pandas DataFrame with the following data quality issues:\n"
                    "{}\n"
                    "The DataFrame columns and their current dtypes are:\n{}\n\n"
                    "Please provide Python code snippets using pandas to address these issues. "
                    "For each issue, suggest a common cleaning approach. "
                    "For example, for missing values, suggest imputation (mean/median for numeric, mode for categorical) or dropping rows/columns. "
                    "For duplicates, suggest dropping them. For constant columns, suggest dropping them. "
                    "Provide clear, concise code blocks and brief explanations for each. "
                    "Do not include conversational filler outside the code and explanations. "
                    "Assume the DataFrame is named `df`.\n"
                    "Assistant:".format(' '.join(issues_summary), df_to_check.dtypes.to_string())
                )
                with st.spinner("Generating AI-powered cleaning suggestions... 🧠"):
                    cleaning_suggestions = call_claude_bedrock(cleaning_prompt)
                    if "❌ Error" in cleaning_suggestions:
                        st.error(cleaning_suggestions)
                    else:
                        st.subheader("AI-Powered Cleaning Code Suggestions:")
                        st.markdown(cleaning_suggestions)
                        st.success("Suggestions generated! Remember to review and adapt them to your specific needs. ✨")
        else:
            st.warning("Please upload a CSV file to get AI cleaning suggestions.")

    st.subheader("8. Categorical Data Encoding")
    st.markdown("""
    Categorical data often needs to be converted into numerical format for machine learning models. Here are common encoding techniques:
    
    * **One-Hot Encoding:** Creates new binary columns for each category.
        * **Use Case:** Nominal (unordered) categorical data where no inherent order exists (e.g., colors, regions). Avoids implying false order.
        * **Example (Python - `pandas.get_dummies`):**
            ```python
            import pandas as pd
            # Assuming 'CategoryColumn' is a categorical column
            df_encoded = pd.get_dummies(df, columns=['CategoryColumn'], prefix='Category')
            ```
    * **Label Encoding:** Assigns a unique integer to each category.
        * **Use Case:** Ordinal (ordered) categorical data where a clear ranking exists (e.g., 'Low', 'Medium', 'High').
        * **Example (Python - `sklearn.preprocessing.LabelEncoder`):**
            ```python
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            df['CategoryColumn_Encoded'] = le.fit_transform(df['CategoryColumn'])
            ```
    * **Ordinal Encoding:** Similar to Label Encoding but allows specifying the order.
        * **Use Case:** Ordinal data where you want to explicitly define the numerical mapping.
        * **Example (Python - `sklearn.preprocessing.OrdinalEncoder`):**
            ```python
            from sklearn.preprocessing import OrdinalEncoder
            encoder = OrdinalEncoder(categories=[['Low', 'Medium', 'High']])
            df['CategoryColumn_Encoded'] = encoder.fit_transform(df[['CategoryColumn']])
            ```
    """)
    st.info("Choose the encoding method based on the nature of your categorical data (ordered vs. unordered).")


# --- Main Tab Rendering Logic ---
if uploaded_file:
    tabs = st.tabs([
        "🏠 Home", # New Home Tab
        "📊 Data & Profile",
        "📄 SQL Builder",
        "✅ Data Quality Checks", # Replaced "Outlier Detection"
        "📦 Export & Filters",
        "✍️ Code Converter",
        "⚙️ STTM Assistant",
        "💬 Ask Zilli",
        "📈 Dashboard"
    ])

    with tabs[0]: # Home Tab
        home_tab()

    with tabs[1]: # Data & Profile
        st.header("Filtered Data Preview")
        st.dataframe(filtered_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Interactive Column Profiling")

        col_to_profile_options = filtered_df.columns.tolist()
        if not col_to_profile_options:
            col_to_profile_options = ["No columns available"]
        
        col_to_profile = st.selectbox("Select column to profile", options=col_to_profile_options, index=0)

        if not filtered_df.empty and col_to_profile != "No columns available":
            col_data = filtered_df[col_to_profile].dropna()
            if pd.api.types.is_numeric_dtype(col_data):
                st.write("### Numeric Column Profile")
                st.dataframe(col_data.describe(percentiles=[.25, .5, .75, .9, .99]).to_frame().T)
                fig_hist = px.histogram(col_data, nbins=30, title="Histogram of {}".format(col_to_profile))
                fig_hist.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                       font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                       xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                st.plotly_chart(fig_hist, use_container_width=True)

                fig_box = px.box(col_data, title="Boxplot of {}".format(col_to_profile))
                fig_box.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                      font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                      xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                st.plotly_chart(fig_box, use_container_width=True)

            elif pd.api.types.is_datetime64_any_dtype(col_data):
                st.write("### Datetime Column Profile")
                st.dataframe(col_data.describe(datetime_is_numeric=True).to_frame().T)
                counts = col_data.dt.date.value_counts().sort_index()
                fig = px.bar(x=counts.index, y=counts.values, labels={'x': col_to_profile, 'y': 'Count'}, title="Counts by Date for {}".format(col_to_profile))
                fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                     font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                     xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("### Categorical Column Profile")
                st.dataframe(col_data.describe().to_frame().T)
                counts = col_data.value_counts().head(20)
                fig = px.bar(x=counts.index.astype(str), y=counts.values, labels={'x': col_to_profile, 'y': 'Count'}, title="Top {} values for {}".format(len(counts), col_to_profile))
                fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                     font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                     xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                st.plotly_chart(fig, use_container_width=True)
        elif filtered_df.empty:
            st.warning("The filtered dataset is empty. Please adjust your filters to see data and profiles.")
        else:
            st.info("Please select a column to view its profile.")

    with tabs[2]: # SQL Builder
        st.header("SQL Query Builder")
        st.markdown("Craft precise SQL queries based on your filtered data and custom criteria.")

        table_name = st.text_input("Table Name (for SQL query)", value="your_table",
                                    help="This name is used in the generated SQL query.")

        sql_select_cols = st.multiselect("Columns to SELECT", options=all_columns, default=select_cols,
                                         help="Choose which columns to include in the SELECT statement. Default is currently displayed columns.")

        st.markdown("#### ORDER BY")
        col1, col2 = st.columns(2)
        with col1:
            sql_order_by_col = st.selectbox("Column to order by", options=[""] + all_columns, index=0,
                                            help="Select a column to sort the results.")
        with col2:
            sql_order_direction = st.selectbox("Order direction", ["ASC", "DESC"], key="order_direction",
                                               help="Choose ascending or descending order.")

        sql_order_by = []
        if sql_order_by_col:
            sql_order_by.append((sql_order_by_col, sql_order_direction))


        sql_limit = st.number_input("LIMIT rows (0 = no limit)", min_value=0, value=filtered_df.shape[0] if filtered_df.shape[0] > 0 else 100, step=1,
                                    help="Limit the number of rows returned by the query. Set to 0 for no limit.")

        st.markdown("---")
        st.subheader("Custom WHERE Clause")
        st.info("The custom WHERE clause will be logically ANDed with existing filters. If you want to completely override filters, only use this field.")
        custom_where = st.text_area("Write your custom WHERE clause here (e.g., `\"ColumnA\" > 100 AND \"ColumnB\" = 'Value'` )", height=100,
                                    help="Enter raw SQL conditions. Use double quotes for column names if they contain spaces or special characters.")


        sql_query = generate_sql(
            table=table_name,
            select_cols=sql_select_cols,
            filters=filters,
            date_filters=date_filters,
            global_search=global_search,
            order_by=sql_order_by,
            limit=sql_limit if sql_limit > 0 else None,
            custom_where=custom_where
        )

        st.subheader("Generated SQL Query")
        st.code(sql_query, language="sql")

        copy_js = """
        <script>
        const sqlToCopy = {};

        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(function() {{
            }}, function(err) {{
                console.error('Async: Could not copy text: ', err);
            }});
        }}
        </script>
        <button onclick="copyToClipboard(sqlToCopy)"
                style="background-color: #00FF99; color: black; border-radius: 8px; border: none; padding: 0.6em 1.2em; font-size: 1.05em; font-weight: bold; transition: all 0.3s ease-in-out; box-shadow: 0 2px 8px rgba(0,255,0,0.2); cursor: pointer;">
            📋 Copy SQL query to clipboard
        </button>
        """.format(json.dumps(sql_query))
        components.html(copy_js, height=50)

        st.markdown("---")
        st.subheader("SQL Query Simulation on DataFrame (filtered)")
        st.write("This table shows the **currently filtered data** which visually represents what your generated SQL query, *if executed on the original dataset with the same logic*, would return (assuming the filters and selections align).")
        st.dataframe(filtered_df, use_container_width=True)

    with tabs[3]: # Data Quality Checks
        data_quality_checks_tab(filtered_df)

    with tabs[4]: # Export & Filters
        st.header("Export & Manage Filters")
        st.markdown("Download your filtered data or reset all active filters.")

        col_exp1, col_exp2 = st.columns([1, 2])
        with col_exp1:
            if st.button("Clear all filters", help="Resets all sidebar filters and displays the original dataset. This will refresh the page."):
                st.cache_data.clear()
                st.experimental_rerun()

        with col_exp2:
            if not filtered_df.empty:
                csv_exp = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download filtered CSV",
                    data=csv_exp,
                    file_name="powercsv_filtered_data.csv",
                    mime="text/csv",
                    help="Download the currently displayed filtered data as a CSV file."
                )
            else:
                st.info("No data to download after filtering.")

        st.markdown("---")
        st.subheader("Current Filters Summary")
        if filters or date_filters or global_search or not (set(select_cols) == set(all_columns) or not select_cols):
            if global_search:
                st.write("**Global Search**: `{}`".format(global_search))
            if select_cols and not (set(select_cols) == set(all_columns) or not select_cols):
                st.write("**Displayed Columns**: {}".format(', '.join(select_cols)))
            for col, cond in filters.items():
                if cond[0] == "range":
                    st.write("**{}**: Range from **{}** to **{}**".format(col, cond[1][0], cond[1][1]))
                elif cond[0] == "in" and cond[1]:
                    st.write("**{}**: Includes values `{}`".format(col, ', '.join(map(str, cond[1]))))
                elif cond[0] == "contains" and cond[1]:
                    st.write("**{}**: Contains text '{}'".format(col, cond[1]))
            for col, (start, end) in date_filters.items():
                st.write("**{}**: From **{}** to **{}**".format(col, start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S')))
        else:
            st.info("No filters currently applied. Showing full dataset and all columns.")

    with tabs[5]: # Code Converter
        st.header("Code Converter")
        st.markdown("Effortlessly convert code snippets between different programming languages using AI.")
        st.info("✍️ Convert your code quickly and accurately between various languages!")

        st.markdown("---")
        col_in, col_out = st.columns(2)

        programming_languages = ["Python", "Java", "JavaScript", "C#", "C++", "Ruby", "Go", "PHP", "SQL", "Rust", "Swift", "Kotlin", "TypeScript"]

        with col_in:
            source_lang = st.selectbox("Source Language", programming_languages, key="source_lang_select")
            input_code = st.text_area("Enter {} code here:".format(source_lang), height=300, key="input_code_area",
                                      placeholder="Paste your {} code here...".format(source_lang))

        with col_out:
            target_lang = st.selectbox("Target Language", programming_languages, key="target_lang_select",
                                       index=programming_languages.index("Python") + 1 if "Python" in programming_languages else 0)

            convert_button = st.button("Convert to {}".format(target_lang), key="convert_button", disabled=(not input_code.strip() or source_lang == target_lang))

            if convert_button:
                if not input_code.strip():
                    st.error("Please enter code to convert.")
                elif source_lang == target_lang:
                    st.warning("Source and target languages are the same. Please choose a different target language.")
                else:
                    conversion_prompt = (
                        "Human: Convert the following {} code to {}.\n"
                        "Ensure the converted code is idiomatic for {} and maintain the original logic and functionality as much as possible.\n"
                        "If there are any assumptions or ambiguities, state them clearly. Provide only the converted code and any necessary explanations/assumptions, no conversational filler.\n\n"
                        "```{}\n"
                        "{}\n"
                        "```\n"
                        "Assistant:".format(source_lang, target_lang, target_lang, source_lang.lower().replace('#','sharp').replace('++','pp'), input_code)
                    )
                    with st.spinner("Converting code from {} to {}... ⏳".format(source_lang, target_lang)):
                        converted_code = call_claude_bedrock(conversion_prompt)
                        if "❌ Error" in converted_code:
                            st.error(converted_code)
                        else:
                            st.subheader("Converted {} Code".format(target_lang))
                            st.code(converted_code, language=target_lang.lower().replace('#','sharp').replace('++','pp'))
                            st.success("Conversion successful! ✅")
                            st.download_button(
                                label="Download {} Code".format(target_lang),
                                data=converted_code.encode("utf-8"),
                                file_name="converted_code.{}.{}".format(target_lang.lower().replace('#','sharp').replace('++','pp'), "txt"), # Added .txt extension
                                mime="text/plain"
                            )

    with tabs[6]: # STTM Assistant
        st.header("STTM Assistant")
        st.markdown("Define and generate **Standardized Transformation and Mapping (STTM)** rules for your data. The AI will help you formulate these rules in a structured document format (e.g., Markdown or JSON).")
        st.info("⚙️ Get structured STTM rules for your data transformations!")

        st.markdown("---")
        st.subheader("1. Define Transformation Goals")
        transformation_goal = st.text_area("Describe your transformation goals and what you want to achieve with the data:",
                                           height=150,
                                           placeholder="E.g., 'Standardize date formats toYYYY-MM-DD', 'Convert 'Gender' column to 'Male/Female' mapping M->Male, F->Female', 'Create a new 'Full Name' column from 'FirstName' and 'LastName'.",
                                           help="Provide a clear, detailed description of your data transformation objectives. Be specific about source and target formats/values.")

        st.subheader("2. Specify Columns and Examples (Optional but Recommended)")
        st.info("Providing example values and current data types helps the AI understand your intent better and generate more accurate STTM rules.")
        
        relevant_cols_options = filtered_df.columns.tolist()
        
        col_sttm_select = st.multiselect("Select relevant columns for STTM", options=relevant_cols_options,
                                         help="Choose columns from your filtered data that will be involved in the transformation.")

        column_details = {}
        if col_sttm_select:
            st.write("Please provide example values and confirm current data type for selected columns:")
            for col in col_sttm_select:
                col_type = str(filtered_df[col].dtype)
                st.text_input("Current detected type of '{}'".format(col), value=col_type, disabled=True, key="sttm_type_{}".format(col))
                
                example_val = filtered_df[col].dropna().sample(min(3, len(filtered_df[col].dropna()))).tolist() if not filtered_df[col].dropna().empty else ["N/A"]
                
                if "sttm_examples_{}".format(col) not in st.session_state:
                    st.session_state["sttm_examples_{}".format(col)] = ", ".join(map(str, example_val))

                user_provided_examples = st.text_area("Example values for '{}' (comma-separated)".format(col),
                                                      value=st.session_state["sttm_examples_{}".format(col)],
                                                      key="sttm_examples_{}".format(col),
                                                      help="Edit if needed to provide more representative examples.")
                column_details[col] = {
                    "type": col_type,
                    "examples": user_provided_examples
                }

        st.subheader("3. Generate STTM Rules")
        generate_sttm_button = st.button("Generate STTM Rules", key="generate_sttm_button",
                                          disabled=(not transformation_goal.strip()))

        if generate_sttm_button:
            if not transformation_goal.strip():
                st.error("Please describe your transformation goals before generating rules.")
            else:
                with st.spinner("Generating STTM rules... ⏳"):
                    context = "The dataset currently has {} rows and {} columns. ".format(filtered_df.shape[0], filtered_df.shape[1]) + \
                              "Its overall column schema is:\n{}\n\n".format(df.dtypes.to_string())

                    if column_details:
                        context += "User has selected and provided details for the following relevant columns:\n"
                        for col, details in column_details.items():
                            context += "- Column: '{}' (Current Type: {}), Representative Examples: [{}]\n".format(col, details['type'], details['examples'])
                    else:
                        context += "No specific columns were selected for detailed examples. Please refer to the overall schema.\n"

                    sttm_prompt = """Human: Based on the following context about a dataset and the user's transformation goal, generate a Standardized Transformation and Mapping (STTM) document.
The document should be highly structured, clear, concise, and actionable for a data engineer to implement.
Include sections for:
1.  **Overview/Purpose**: Briefly state the goal of the transformations.
2.  **Source Data Assumptions**: Any assumptions about the input data structure or content.
3.  **Transformation Rules**:
    * For each transformation, specify:
        * **Source Column(s)**: The original column(s) used.
        * **Target Column**: The new or updated column name.
        * **Transformation Logic**: A clear description or pseudo-code of how the transformation is performed. Be very specific (e.g., "Convert 'MM/DD/YYYY' to 'YYYY-MM-DD'", "Concatenate 'FirstName' and 'LastName' with a space").
        * **Data Type (Target)**: The expected data type after transformation.
        * **Mapping/Lookup (if applicable)**: Explicit mapping rules (e.g., 'M' -> 'Male', 'F' -> 'Female').
        * **Error Handling/Missing Data**: How nulls or invalid data should be handled.
4.  **Example Transformation (Optional but recommended for complex rules)**: Show a simple before-and-after example.
5.  **Output Format (Recommendation)**: Suggest the desired output format (e.g., CSV, Parquet, Database Table).

Use clear Markdown formatting (headings, bullet points, code blocks). Do NOT include any conversational text outside the generated STTM document itself. Just provide the document.

Context:
{}

Transformation Goal:
{}

Assistant:
""".format(context, transformation_goal)
                    sttm_output = call_claude_bedrock(sttm_prompt)

                    if "❌ Error" in sttm_output:
                        st.error(sttm_output)
                    else:
                        st.subheader("Generated STTM Document")
                        st.markdown(sttm_output)
                        st.success("STTM rules generated successfully! ✅")

                        st.download_button(
                            label="Download STTM Document (.csv)",
                            data=sttm_output.encode("utf-8"),
                            file_name="sttm_document.csv",
                            mime="text/markdown",
                            help="Download the generated STTM document in Markdown format."
                        )
        st.markdown("---")
        st.info("""
        **What is STTM?**
        **Standardized Transformation and Mapping (STTM)** documents define how raw data from source systems should be transformed, cleaned, and mapped to a target data model or a standardized format. They are crucial for data integration, warehousing, and ensuring data quality and consistency across various data pipelines.
        """)

    with tabs[7]: # AI Chatbot
        st.header("Ask Zilli")
        st.markdown("Ask natural language questions about your data. The chatbot will prioritize searching your **filtered data**, then consult an AI model (Claude via AWS Bedrock) for broader knowledge or complex interpretations.")
        st.info("💬 Your AI assistant for data insights and general queries!")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # This text_area will be updated by speech-to-text
        question = st.text_area("Ask a question about your data:", key="chatbot_question_input", height=70,
                                placeholder="E.g., 'What is the average sales?', 'Find all customers from New York City'.")

        # Embed the speech-to-text button
        speech_to_text_component()

        if st.button("Submit Question to Chatbot", key="submit_chatbot_question") and question.strip():
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            if not filtered_df.empty:
                with st.spinner("Searching for answer in your data... 🔍"):
                    answer = search_dataframe_for_answer(filtered_df, question)
                    if answer:
                        with st.chat_message("assistant"):
                            st.success("✅ **Answer found directly in your data:**")
                            st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": "✅ **Answer found directly in your data:**\n" + answer})
                    else:
                        with st.chat_message("assistant"):
                            st.info("No direct match found in local data. Consulting AI for a broader answer... 🧠")
                        with st.spinner("Asking Zilli for response... ☁️"):
                            df_summary = "The dataset has {} rows and {} columns. ".format(filtered_df.shape[0], filtered_df.shape[1]) + \
                                         "Column names are: {}. ".format(', '.join(filtered_df.columns.tolist())) + \
                                         "Here are the first 5 rows for context:\n{}".format(filtered_df.head(5).to_markdown(index=False))
                            
                            claude_prompt = (
                                "Given the following data summary and the user's question, provide a helpful and concise answer. "
                                "If the question is about data insights, explain how one might find it or what typical analysis entails. "
                                "Do not assume you have direct access to run code on the data unless explicitly asked. \n\n"
                                "Data Summary:\n{}\n\n"
                                "User Question: {}".format(df_summary, question)
                            )
                            llm_answer = call_bedrock_claude_chatbot(claude_prompt)
                            with st.chat_message("assistant"):
                                st.success("💡 **AI's Response:**")
                                st.write(llm_answer)
                            st.session_state.messages.append({"role": "assistant", "content": "💡 **AI's Response:**\n" + llm_answer})
            else:
                with st.chat_message("assistant"):
                    st.warning("Cannot answer data-specific questions: The filtered dataset is currently empty. Please upload data and adjust filters.")
                    st.info("If you want to ask general questions not related to your specific data, the AI will try to answer based on its general knowledge.")
                
                if st.button("Ask AI general question (data not considered)", key="ask_general_ai_fallback") and question.strip():
                    with st.spinner("Asking Zilli for response ☁️"):
                        llm_answer = call_bedrock_claude_chatbot(question)
                        with st.chat_message("assistant"):
                            st.success("💡 **AI's Response:**")
                            st.write(llm_answer)
                        st.session_state.messages.append({"role": "assistant", "content": "💡 **AI's Response:**\n" + llm_answer})


    with tabs[8]: # Dashboard
        st.header("Interactive Dashboard")
        st.write("This dashboard visualizes your uploaded and filtered data. Select columns to generate various charts.")

        if filtered_df.empty:
            st.warning("The filtered dataset is empty. Please upload a CSV and adjust filters to generate the dashboard.")
        else:
            st.subheader("Dashboard Controls")

            numeric_cols_for_dashboard = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols_for_dashboard = filtered_df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols_for_dashboard = filtered_df.select_dtypes(include=['datetime64']).columns.tolist()

            chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot", "Correlation Heatmap"], key="chart_type_dashboard")

            if chart_type == "Bar Chart":
                if categorical_cols_for_dashboard and numeric_cols_for_dashboard:
                    x_col = st.selectbox("Select Category Column (X-axis)", categorical_cols_for_dashboard, key="bar_x_col")
                    y_col = st.selectbox("Select Value Column (Y-axis)", numeric_cols_for_dashboard, key="bar_y_col")
                    if x_col and y_col:
                        agg_df = filtered_df.groupby(x_col)[y_col].sum().reset_index()
                        fig = px.bar(agg_df, x=x_col, y=y_col, title="Sum of {} by {}".format(y_col, x_col))
                        fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                          font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                          xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No suitable categorical and numeric columns for a Bar Chart.")

            elif chart_type == "Line Chart":
                if datetime_cols_for_dashboard and numeric_cols_for_dashboard:
                    x_col = st.selectbox("Select Date Column (X-axis)", datetime_cols_for_dashboard, key="line_x_col")
                    y_col = st.selectbox("Select Value Column (Y-axis)", numeric_cols_for_dashboard, key="line_y_col")
                    color_col_options = ['None'] + categorical_cols_for_dashboard
                    color_col = st.selectbox("Color by (Optional)", color_col_options, key="line_color_col")

                    if x_col and y_col:
                        if color_col != 'None':
                            agg_df = filtered_df.groupby([pd.Grouper(key=x_col, freq='D'), color_col])[y_col].sum().reset_index()
                            fig = px.line(agg_df, x=x_col, y=y_col, color=color_col, title="Sum of {} Over Time by {}".format(y_col, color_col))
                        else:
                            agg_df = filtered_df.groupby(pd.Grouper(key=x_col, freq='D'))[y_col].sum().reset_index()
                            fig = px.line(agg_df, x=x_col, y=y_col, title="Sum of {} Over Time".format(y_col))
                        
                        fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                          font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                          xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No suitable date and numeric columns for a Line Chart.")

            elif chart_type == "Scatter Plot":
                if numeric_cols_for_dashboard:
                    x_col = st.selectbox("Select X-axis Column (Numeric)", numeric_cols_for_dashboard, key="scatter_x_col")
                    y_col = st.selectbox("Select Y-axis Column (Numeric)", numeric_cols_for_dashboard, index=min(1, len(numeric_cols_for_dashboard) - 1), key="scatter_y_col")
                    color_col_options = ['None'] + categorical_cols_for_dashboard
                    color_col = st.selectbox("Color by (Optional)", color_col_options, key="scatter_color_col")
                    size_col_options = ['None'] + numeric_cols_for_dashboard
                    size_col = st.selectbox("Size by (Optional)", size_col_options, key="scatter_size_col")
                    
                    if x_col and y_col:
                        fig = px.scatter(filtered_df, x=x_col, y=y_col,
                                         color=color_col if color_col != 'None' else None,
                                         size=size_col if size_col != 'None' else None,
                                         title="{} vs {}".format(y_col, x_col))
                        fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                          font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                          xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No suitable numeric columns for a Scatter Plot.")

            elif chart_type == "Histogram":
                if numeric_cols_for_dashboard:
                    x_col = st.selectbox("Select Numeric Column", numeric_cols_for_dashboard, key="hist_x_col")
                    if x_col:
                        fig = px.histogram(filtered_df, x=x_col, nbins=st.slider("Number of Bins", 5, 100, 30), title="Distribution of {}".format(x_col))
                        fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                          font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                          xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No suitable numeric columns for a Histogram.")
            
            elif chart_type == "Box Plot":
                if numeric_cols_for_dashboard:
                    y_col = st.selectbox("Select Numeric Column", numeric_cols_for_dashboard, key="box_y_col")
                    x_col_options = ['None'] + categorical_cols_for_dashboard
                    x_col = st.selectbox("Group by (Optional Category)", x_col_options, key="box_x_col")
                    if y_col:
                        fig = px.box(filtered_df, y=y_col, x=x_col if x_col != 'None' else None, title="Box Plot of {}".format(y_col))
                        fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                          font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                          xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No suitable numeric columns for a Box Plot.")

            elif chart_type == "Correlation Heatmap":
                if numeric_cols_for_dashboard and len(numeric_cols_for_dashboard) > 1:
                    st.subheader("Correlation Heatmap")
                    correlation_matrix = filtered_df[numeric_cols_for_dashboard].corr()
                    fig_corr = px.imshow(correlation_matrix,
                                         text_auto=True,
                                         aspect="auto",
                                         color_continuous_scale=px.colors.sequential.Viridis,
                                         title="Correlation Matrix of Numeric Columns")
                    fig_corr.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                                           font=dict(color="#E0E0E0"), title_font_color="#00FF99",
                                           xaxis_title_font_color="#E0E0E0", yaxis_title_font_color="#E0E0E0")
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.info("Need at least two numeric columns to generate a Correlation Heatmap.")

else: # If no file is uploaded, only show the Home tab
    home_tab()


st.markdown("---")
st.markdown(" developed by **Shiv@2025**")