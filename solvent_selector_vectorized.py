import streamlit as st
import pandas as pd
from io import BytesIO
import os;
import numpy as np;
#from openpyxl.utils import get_column_letter
#from openpyxl.styles import Alignment

abs_path = os.path.dirname(os.path.abspath(__file__));


def initApp():    
    #from eval_names import getResults

    version = 1.0;
    tool_name = f"KouTer Green Solvents V{version:.2f}"
    st.title(tool_name)
   

# Initialize session state for acknowledgment
if 'acknowledged' not in st.session_state:
    st.session_state.acknowledged = False
if 'declined' not in st.session_state:
    st.session_state.declined = False

# Disclaimer text
disclaimer_text = """

⚠️ This tool relies on AI-generated data that can contain errors. The tool is intended for informational and research purposes only. Users should not rely on it for laboratory safety decisions. Always consult official Safety Data Sheets (SDS) and follow institutional safety protocols. ⚠️

I understand this tool is **not for laboratory use** and I will consult **official Safety Data Sheets (SDS)** 
before using any chemicals.
"""


# If declined, show subtle message
if st.session_state.declined:
    st.info("You have chosen not to acknowledge the disclaimer. The tool is unavailable for use.")


# Show disclaimer with options
if not st.session_state.acknowledged and not st.session_state.declined:
    st.title("⚠️ Safety Disclaimer")
    st.write(disclaimer_text)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("I Acknowledge"):
            st.session_state.acknowledged = True
            st.rerun()  # Immediately rerun script

    with col2:
        if st.button("I Do Not Acknowledge"):
            st.session_state.declined = True
            st.rerun()

# If acknowledged, show main app
if st.session_state.acknowledged:
    initApp();
