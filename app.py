import streamlit as st
from PIL import Image

im = Image.open("image\logo.png")

st.set_page_config(
    page_title="Hello",
    layout="wide",
)

# Set the background color
st.markdown(
    """
    <style>
    body {
        background-color: #FE414D;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🌐 Warehouse Management & Optimization")
st.image(im, use_column_width=True)