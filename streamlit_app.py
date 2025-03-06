import streamlit as st
import pandas as pd
import os
import json
import datetime
import re
import base64
import streamlit.components.v1 as components

# Google Sheets libraries
import gspread
from google.oauth2.service_account import Credentials


# ----- Helper Function for Video Display -----
def get_video_html(video_path, width):
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        encoded_video = base64.b64encode(video_bytes).decode()
    except Exception as e:
        st.error(f"Error loading video: {e}")
        return ""
    video_html = f"""
    <video width="{width}" controls>
      <source src="data:video/mp4;base64,{encoded_video}" type="video/mp4">
      Your browser does not support the video tag.
    </video>
    """
    return video_html

# ----- App Title and Description -----
st.title("Qualitative Performance Assessment of EndoDAC and Depth Pro Models")
st.write(
    "The video in the center shows a colonoscopy, while the two side videos (left and right) "
    "represent depth maps generated by two predictive models, where blue indicates deeper areas "
    "and red indicates shallower areas. \n"
    "Which of the two side videos (left or right) do you think best reflects reality in terms of accuracy in depth estimation?"
)

# ----- Clinician Questions -----
clinician = st.radio("Are you a clinician?", ["Yes", "No"])
experience_level = None
procedures_performed = None
if clinician == "Yes":
    experience_level = st.radio("What is your experience level?", ["Specializzando", "Resident", "Esperto"])
    procedures_performed = st.radio(
        "How many endoscopic procedures have you performed?",
        ["<50", "Between 50 and 100", ">100"]
    )

# ----- Name Input -----
name = st.text_input("Please enter your name")

# ----- Video Display Settings -----
VIDEO_WIDTH = 640  # adjust video width here

# ----- Video Paths -----
video_paths = [
    "./videos/VideoColonoscopy3.mp4",
    "./videos/VideoColonoscopy4.mp4",
    "./videos/VideoColonoscopy5.mp4",
    "./videos/VideoColonoscopy6.mp4",
    "./videos/VideoColonoscopy7.mp4",
    "./videos/VideoColonoscopy8.mp4",
    "./videos/VideoColonoscopy9.mp4",
    "./videos/VideoColonoscopy10.mp4",
    "./videos/VideoColonoscopy11.mp4",
    "./videos/VideoColonoscopy12.mp4",
]

# ----- Session State Initialization -----
if "question_index" not in st.session_state:
    st.session_state["question_index"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = [None] * len(video_paths)

# ----- Questionnaire and Video Display -----
if name:
    st.header("Questionnaire")
    question_index = st.session_state["question_index"]
    st.subheader(f"Question {question_index + 1}")
    
    # Display video using HTML embed with base64 encoding
    video_path = video_paths[question_index]
    video_html = get_video_html(video_path, VIDEO_WIDTH)
    if video_html:
        components.html(video_html, height=int(VIDEO_WIDTH * 0.75))
    
    existing_response = st.session_state["responses"][question_index]
    default_index = 0 if existing_response == "Left" else 1 if existing_response == "Right" else None
    
    response = st.radio(
        "Which of the two side videos (left or right) do you think best reflects reality in terms of accuracy in depth estimation?", 
        ["Left", "Right"], 
        key=f"question_{question_index}",
        index=default_index if default_index is not None else 0
    )
    
    st.session_state["responses"][question_index] = response
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous") and question_index > 0:
            st.session_state["question_index"] -= 1
            st.rerun()
    with col2:
        if st.button("Next") and question_index < len(video_paths) - 1:
            st.session_state["question_index"] += 1
            st.rerun()
    
    # ----- Submission Block -----
    if question_index == len(video_paths) - 1 and st.button("Submit Answers"):
        # Create a folder for JSON responses if it does not exist
        responses_folder = "responses"
        if not os.path.exists(responses_folder):
            os.makedirs(responses_folder)
        
        # Sanitize name for filename
        safe_name = re.sub(r'[^\w\-_. ]', '_', name).strip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{safe_name}_{timestamp}.json"
        file_path = os.path.join(responses_folder, file_name)
        
        # Prepare response data
        new_data = {
            "Name": name,
            "Clinician": clinician,
            "Experience Level": experience_level if clinician == "Yes" else None,
            "Procedures Performed": procedures_performed if clinician == "Yes" else None,
        }
        for i in range(len(video_paths)):
            new_data[f"Question {i+1}"] = st.session_state["responses"][i] if st.session_state["responses"][i] else "No Response"
        
        # Save locally as JSON
        try:
            with open(file_path, "w") as f:
                json.dump(new_data, f, indent=4)
        except Exception as e:
            st.error(f"Error saving JSON file: {e}")
        
        # ----- Google Sheets Setup -----
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive"
            ]
<<<<<<< HEAD
            # Load credentials from secrets
            creds_data = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(creds_data)
=======
            creds = Credentials.from_service_account_file("./quntitative-depth-estimation-b927cbf8ca78.json", scopes=scope)
>>>>>>> 202dc67696f4eb98c9a3320bb352152d0152704f
            client = gspread.authorize(creds)

            # Now you can use client to access your Google Sheet
            sheet = client.open("Quantitative_assesment").sheet1
            
<<<<<<< HEAD
=======
            # Open your Google Sheet by name
            sheet = client.open("Quantitative_assesment").sheet1  # change to your sheet name
            
>>>>>>> 202dc67696f4eb98c9a3320bb352152d0152704f
            # Prepare row data (order should match your sheet header)
            row_data = [
                name,
                clinician,
                experience_level if clinician == "Yes" else "",
                procedures_performed if clinician == "Yes" else ""
            ]
            row_data.extend([st.session_state["responses"][i] if st.session_state["responses"][i] else "No Response" for i in range(len(video_paths))])
            
            # Append row to the sheet
            sheet.append_row(row_data)
        except Exception as e:
            st.error(f"Error saving to Google Sheets: {e}")
        
        st.success("Your answers have been saved!")
        st.stop()
