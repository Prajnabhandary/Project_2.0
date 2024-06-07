import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import base64
import time
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
from streamlit_cropperjs import st_cropperjs

# Initialize session state for storing images and actions
if 'images' not in st.session_state:
    st.session_state.images = {'original': None, 'current': None, 'previous': None, 'submitted': None}
if 'actions' not in st.session_state:
    st.session_state.actions = {'basic': None, 'advanced': None}
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'crop'

# Load the image from the backend and resize it to 800x600 pixels
preloaded_image_path = "Assets/brand_cars/Maruti Brezza/brezza_1.jpg"
preloaded_image = Image.open(preloaded_image_path)  # Replace with the path to your preloaded image
preloaded_image = preloaded_image.resize((800, 600))
st.session_state.images['original'] = preloaded_image
if st.session_state.images['current'] is None:
    st.session_state.images['current'] = preloaded_image.copy()

# Helper functions
def refresh_current_image():
    st.session_state.images['current'] = st.session_state.images['original'].copy()
    if st.session_state.current_page == 'crop':
        st.session_state.images['previous'] = None

def enhance_image():
    if st.session_state.images['current']:
        st.session_state.images['previous'] = st.session_state.images['current'].copy()
        enhancer = ImageEnhance.Contrast(st.session_state.images['current'])
        factor = st.slider('Enhancement Factor', 1.0, 3.0, 1.0)
        st.session_state.images['current'] = enhancer.enhance(factor)
        st.image(st.session_state.images['current'], caption='Enhanced Image', use_column_width=True)

def filter_image():
    if st.session_state.images['current']:
        st.session_state.images['previous'] = st.session_state.images['current'].copy()
        filter_type = st.selectbox('Choose a filter', ['DETAIL', 'CONTOUR', 'BLUR', 'EDGE_ENHANCE', 'EMBOSS', 'SHARPEN'])
        if filter_type == 'BLUR':
            st.session_state.images['current'] = st.session_state.images['current'].filter(ImageFilter.BLUR)
        elif filter_type == 'CONTOUR':
            st.session_state.images['current'] = st.session_state.images['current'].filter(ImageFilter.CONTOUR)
        elif filter_type == 'DETAIL':
            st.session_state.images['current'] = st.session_state.images['current'].filter(ImageFilter.DETAIL)
        elif filter_type == 'EDGE_ENHANCE':
            st.session_state.images['current'] = st.session_state.images['current'].filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == 'EMBOSS':
            st.session_state.images['current'] = st.session_state.images['current'].filter(ImageFilter.EMBOSS)
        elif filter_type == 'SHARPEN':
            st.session_state.images['current'] = st.session_state.images['current'].filter(ImageFilter.SHARPEN)
        st.image(st.session_state.images['current'], caption='Filtered Image', use_column_width=True)

def in_painting():
    st.write("Draw on the canvas to in-paint.")
    canvas_result = st_canvas(
        fill_color="white",
        stroke_width=5,
        stroke_color="black",
        background_image=st.session_state.images['current'],
        update_streamlit=True,
        height=600,
        width=800,
        drawing_mode="freedraw",
        key="canvas"
    )
    if canvas_result.image_data is not None:
        st.session_state.images['previous'] = st.session_state.images['current'].copy()
        inpainted_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        st.session_state.images['current'].paste(inpainted_image, (0, 0), inpainted_image)
        st.image(st.session_state.images['current'], caption='In-Painted Image', use_column_width=True)

def add_logo():
    if st.session_state.images['current']:
        st.session_state.images['previous'] = st.session_state.images['current'].copy()
        logo_file = st.file_uploader("Choose a logo...", type=["jpg", "jpeg", "png"])
        if logo_file is not None:
            logo = Image.open(logo_file).convert("RGBA")
            logo = logo.resize((50, 50))
            logo_mask = logo.split()[3].point(lambda i: i * 1.0)
            placement = st.selectbox('Choose logo placement', ['Top Left', 'Top Right', 'Bottom Right', 'Bottom Left'])
            if placement == 'Top Left':
                position = (10, 10)
            elif placement == 'Top Right':
                position = (st.session_state.images['current'].width - 60, 10)
            elif placement == 'Bottom Right':
                position = (st.session_state.images['current'].width - 60, st.session_state.images['current'].height - 60)
            elif placement == 'Bottom Left':
                position = (10, st.session_state.images['current'].height - 60)
            st.session_state.images['current'].paste(logo, position, logo_mask)
            st.image(st.session_state.images['current'], caption='Image with Logo', use_column_width=True)

def add_footer():
    if st.session_state.images['current']:
        st.session_state.images['previous'] = st.session_state.images['current'].copy()
        draw = ImageDraw.Draw(st.session_state.images['current'])
        footer_text = st.text_input("Enter footer text")
        text_color = st.color_picker("Choose text color", "#FFFFFF")
        font_size = st.slider("Choose font size", 10, 50, 20)
        font_style = st.selectbox("Choose font style", ["Default", "Bold", "Italic"])
        box_around_text = st.checkbox("Add a box around the text")
        box_color = st.color_picker("Choose box color", "#000000") if box_around_text else None

        if footer_text:
            try:
                font = ImageFont.truetype("arial.ttf", font_size) if font_style == "Default" else ImageFont.load_default()
            except IOError:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), footer_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            width, height = st.session_state.images['current'].size
            text_position = (10, height - text_height - 10)

            if box_around_text:
                draw.rectangle([(text_position[0] - 5, text_position[1] - 5), 
                                (text_position[0] + text_width + 5, text_position[1] + text_height + 5)], 
                               fill=box_color)

            draw.text(text_position, footer_text, font=font, fill=text_color)
            st.image(st.session_state.images['current'], caption='Image with Footer', use_column_width=True)

def download_image():
    if st.session_state.images['current']:
        buf = io.BytesIO()
        st.session_state.images['current'].save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(label="Download image", data=byte_im, file_name="edited_image.png", mime="image/png")

def img_to_base64(image_path):
    """Convert image to base64"""
    with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

def crop1():
    st.session_state.images['previous'] = st.session_state.images['current'].copy()
    
    if 'current' in st.session_state.images:
        st.write('Selected image')
        st.image(st.session_state.images['current'])
        with open(preloaded_image_path, "rb") as image_file:
            encoded_string = image_file.read()
        cropped_pic = st_cropperjs(pic=encoded_string, btn_text="Crop", key="foo")
        if cropped_pic:
            st.image(cropped_pic, output_format="PNG")
            st.session_state.images['current'] = Image.open(io.BytesIO(cropped_pic))

def main():
    # st.sidebar.markdown("### Editing Options")
    if st.sidebar.button("Basic Editing"):
        st.session_state.page = 'basic'
        st.session_state.current_page = 'crop'
    if st.sidebar.button("Advance Editing"):
        st.session_state.page = 'advanced'
        st.session_state.current_page = 'in_painting'

    if st.session_state.page == 'basic':
        st.write("## Basic Editing")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Crop"):
                st.session_state.current_page = 'crop'
                st.experimental_rerun()
        with col2:
            if st.button("Enhance"):
                st.session_state.current_page = 'enhance'
                st.experimental_rerun()
        with col3:
            if st.button("Filter"):
                st.session_state.current_page = 'filter'
                st.experimental_rerun()

        if st.session_state.current_page == 'crop':
            crop1()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Refresh", key="refresh_crop"):
                    refresh_current_image()
                    st.experimental_rerun()
            with col2:
                if st.button("Next", key="next_crop"):
                    st.session_state.current_page = 'enhance'
                    st.experimental_rerun()
        elif st.session_state.current_page == 'enhance':
            enhance_image()
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Back", key="back_enhance"):
                    st.session_state.current_page = 'crop'
                    st.experimental_rerun()
            with col2:
                if st.button("Refresh", key="refresh_enhance"):
                    refresh_current_image()
                    st.experimental_rerun()
            with col3:
                if st.button("Next", key="next_enhance"):
                    st.session_state.current_page = 'filter'
                    st.experimental_rerun()
        elif st.session_state.current_page == 'filter':
            filter_image()
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Back", key="back_filter"):
                    st.session_state.current_page = 'enhance'
                    st.experimental_rerun()
            with col2:
                if st.button("Refresh", key="refresh_filter"):
                    refresh_current_image()
                    st.experimental_rerun()
            with col3:
                if st.button("Submit", key="submit_basic"):
                    st.session_state.images['submitted'] = st.session_state.images['current']
                    st.session_state.actions['basic'] = None
                    st.session_state.page = 'advanced'
                    st.session_state.current_page = 'in_painting'
                    st.experimental_rerun()

    elif st.session_state.page == 'advanced':
        st.write("## Advance Editing")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("In-paint"):
                st.session_state.current_page = 'in_painting'
                st.experimental_rerun()
        with col2:
            if st.button("Logo Addition"):
                st.session_state.current_page = 'logo_addition'
                st.experimental_rerun()
        with col3:
            if st.button("Footer Note"):
                st.session_state.current_page = 'footer_note'
                st.experimental_rerun()

        if st.session_state.images['submitted']:
            st.session_state.images['current'] = st.session_state.images['submitted'].copy()
            if st.session_state.current_page == 'in_painting':
                in_painting()
            elif st.session_state.current_page == 'logo_addition':
                add_logo()
            elif st.session_state.current_page == 'footer_note':
                add_footer()

    # Custom styling for Streamlit app
    st.markdown("""
        <style>
            body {
                background-color: #003399;
                font-family: Arial, sans-serif;
                color: #333333;
            }
            .sidebar .sidebar-content {
                background-color: #ffffff;
                padding: 20px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
            .stButton>button {
                background-color: #f0f0f0;
                color: #333333;
                border-radius: 30px;
                border: none;
                padding: 12px 24px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            .stButton>button:hover {
                background-color: #e0e0e0;
            }
            .stRadio>div {
                font-size: 16px;
            }
            .stSlider>div>div>div {
                color: #4CAF50;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #FF5733;
                border-bottom: 2px solid #FF5733;
                padding-bottom: 8px;
                margin-bottom: 16px;
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

