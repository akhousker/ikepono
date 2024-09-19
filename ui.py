import streamlit as st
import pandas as pd
import numpy as np

st.title('Ikepono')
st.header('manta ray identification')

st.file_uploader("Upload your photos", accept_multiple_files=True)
