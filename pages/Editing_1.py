import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import base64
import time
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_cropperjs import st_cropperjs
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

# Initialize session state for storing images and actions
if 'images' not in st.session_state:
    st.session_state.images = {'original': None, 'current': None, 'previous': None, 'submitted': None}
if 'actions' not in st.session_state:
    st.session_state.actions = {'basic': None, 'advanced': None}
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Load the image from the backend and resize it to 800x600 pixels
preloaded_image_path = "Assets/brand_cars/Maruti Brezza/brezza_1.jpg"
preloaded_image = Image.open(preloaded_image_path)  # Replace with the path to your preloaded image
preloaded_image = preloaded_image.resize((800, 600))
st.session_state.images['original'] = preloaded_image
st.session_state.images['current'] = preloaded_image.copy()

# Helper functions
def refresh_image():
    st.session_state.images['current'] = st.session_state.images['original'].copy()
    st.session_state.images['previous'] = None
    st.image(st.session_state.images['current'], caption='Original Image', use_column_width=True)

def undo_image():
    if st.session_state.images['previous']:
        st.session_state.images['current'] = st.session_state.images['previous'].copy()
        st.session_state.images['previous'] = None
        st.image(st.session_state.images['current'], caption='Previous Image', use_column_width=True)

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
        filter_type = st.selectbox('Choose a filter', ['BLUR', 'CONTOUR', 'DETAIL', 'EDGE_ENHANCE', 'EMBOSS', 'SHARPEN'])
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
        image_with_draw = np.array(st.session_state.images['current'].convert('RGB'))[:, :, ::-1].copy()
        image_normal = np.array(st.session_state.images['previous'].convert('RGB'))[:, :, ::-1].copy()
        gray_normal = cv2.cvtColor(image_normal, cv2.COLOR_BGR2GRAY)
        gray_draw = cv2.cvtColor(image_with_draw, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_draw, gray_normal)
        _, mask = cv2.threshold(diff, 8, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled_mask = np.zeros_like(mask)
        cv2.drawContours(filled_mask, contours, -1, color=(255, 255, 255), thickness=cv2.FILLED)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(mask,[c], 0, (255,255,255), -1)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        # st.image(opening, caption='Mask Image', use_column_width=True)
        
        model_option = st.selectbox(
            "Select a Model for inpainting:",
            ("SDXL", "DALLE"),index=None)
        if model_option:
            st.session_state['model_inpaint'] = model_option
        st.write(' ')
        if 'model_inpaint' in st.session_state:
            Postive_prompt = st.text_input("Enter a prompt",placeholder="add a street lamp on the curb near the car")
            if 'prompt_inpaint' not in st.session_state:
                st.session_state['prompt_inpaint'] = ''
            st.session_state['prompt_inpaint'] = Postive_prompt
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button('Person walking with the dog'):
                    Postive_prompt = 'Person walking with the dog'
                    st.session_state['prompt_inpaint'] = Postive_prompt
            with col2:
                if st.button('Big majestic green tree with  large leaves, high resolution, 4k'):
                    Postive_prompt = 'Big majestic green tree with  large leaves, high resolution, 4k,'
                    st.session_state['prompt_inpaint'] = Postive_prompt
            with col3:
                if st.button('black futuristic glass building, high resolution, 4k'):
                    Postive_prompt = 'black futuristic glass building, high resolution, 4k'
                    st.session_state['prompt_inpaint'] = Postive_prompt
            st.write("Prompt entered:", Postive_prompt)
            st.session_state['prompt_inpaint'] = Postive_prompt
            if 'prompt_inpaint' in st.session_state:
                col1, col2, col3  = st.columns(3)
                with col1:
                    pass
                with col2:
                    center_button = st.button('Generate inpaint')
                with col3 :
                    pass





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
            font = ImageFont.truetype("arial.ttf", font_size) if font_style == "Default" else ImageFont.load_default()
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
            return True
    return False

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

    # Load and display sidebar image with glowing effect


    st.sidebar.markdown("### Editing Options")
    if st.sidebar.button("Basic Editing", key="basic"):
        st.session_state.page = 'basic'
    if st.sidebar.button("Advance Editing", key="advance"):
        st.session_state.page = 'advanced'

    if st.session_state.page == 'basic':
        st.write("## Basic Editing")
        #st.markdown("<h1 style='text-align: center; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); -webkit-background-clip: text; color: transparent;'>Basic Editing</h1>", unsafe_allow_html=True)
        action = st.radio("Select Action", ["Crop", "Enhance", "Filter"], key="basic_action")
        if action == "Crop":
            # crop_image()
            crop1()
            pass
        elif action == "Enhance" or st.session_state.actions['basic'] == 'enhance':
            enhance_image()
            if st.button("Next", key="next_enhance"):
                st.session_state.actions['basic'] = 'filter'
        elif action == "Filter" or st.session_state.actions['basic'] == 'filter':
            filter_image()
            if st.button("Submit", key="submit_basic"):
                st.session_state.images['submitted'] = st.session_state.images['current']
                st.session_state.actions['basic'] = None
                st.success("Image submitted! Proceeding to advance editing.")
                st.session_state.page = 'advanced'  # Navigate to advanced editing

    elif st.session_state.page == 'advanced':
        st.write("## Advance Editing")
        if st.session_state.images['submitted']:
            st.session_state.images['current'] = st.session_state.images['submitted'].copy()
            action = st.radio("Select Action", ["In-Painting", "Logo Addition", "Footer Note"], key="advanced_action")
            if action == "In-Painting":
                in_painting()
            elif action == "Logo Addition" or st.session_state.actions['advanced'] == 'logo':
                add_logo()
            elif action == "Footer Note" or st.session_state.actions['advanced'] == 'footer':
                if add_footer():
                    download_image()
                    st.button("Submit", key="submit_advanced")

    # Global buttons for navigation and actions
    if st.session_state.page not in ['home', 'editing_panel']:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.button("Undo", on_click=undo_image, key="undo")
        with col2:
            st.button("Refresh", on_click=refresh_image, key="refresh")
        with col3:
            st.button("Next", key="next")

    # Custom styling for Streamlit app
    st.markdown("""
        <style>
            body {
                background-color: #f5f5f5;
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
                background-color: #4CAF50;
                color: white;
                border-radius: 30px;
                border: none;
                padding: 12px 24px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            .stButton>button:hover {
                background-color: #45a049;
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
            .cover-glow {
                box-shadow: 
                    0 0 5px #7a7a7a,
                    0 0 10px #7a7a7a,
                    0 0 15px #7a7a7a,
                    0 0 20px #7a7a7a,
                    0 0 25px #009688,
                    0 0 30px #009688,
                    0 0 35px #009688;
                border-radius: 50%;  /* Circle */
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()