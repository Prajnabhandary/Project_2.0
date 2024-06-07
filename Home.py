import streamlit as st
import pandas as pd
import numpy as np
from streamlit_image_select import image_select
from st_pages import Page, show_pages, add_page_title
from PIL import Image
import base64
import io

# logo sidebar
file = open("Assets/maruti-suzuki-logo-png-transparent_resize_100.png", "rb")
contents = file.read()
img_str = base64.b64encode(contents).decode("utf-8")
buffer = io.BytesIO()
file.close()
img_data = base64.b64decode(img_str)
img = Image.open(io.BytesIO(img_data))
resized_img = img.resize((150, 100))  # x, y
resized_img.save(buffer, format="PNG")
img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
st.session_state['logo'] = img_b64
st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url('data:image/png;base64,{st.session_state['logo']}');
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 90px 20px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def main():

    show_pages(
    [
        Page("Home.py", "Home"),
        Page("pages/Generation.py", "Generation"),
        Page("pages/Editing.py", "Editing")

    ]
                )
    
    st.markdown(
        """
    <style>
    div[class^="block-container"] {
        padding-top: 0rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title('Welcome to Maruti - Generation AI application')
    st.write(" ")
    st.header("Quick start guide ")
    st.write(" ")
    st.write("Step 1: Select brand")
    st.image('Assets/home_page_images/image1.png')
    st.write("Step 2: Select Image")
    st.image('Assets/home_page_images/image2.png')
    st.write("Step 3: Select Model")

if __name__ == "__main__":
    main()