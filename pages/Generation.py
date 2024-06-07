import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from streamlit_image_select import image_select
import time
from PIL import Image, ImageDraw
import numpy as np


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
st.markdown(
        """
    <style>
    div[class^="block-container"] {
        padding-top: 2rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

def get_images_by_folder(main_folder_name):
    subfolders = [subfolder for subfolder in os.listdir(main_folder_name) if os.path.isdir(os.path.join(main_folder_name, subfolder))]
    if subfolders:
        images_dict = {}
        for subfolder in subfolders:
            subfolder_path = os.path.join(main_folder_name, subfolder)
            images = [os.path.join(subfolder_path, file) for file in os.listdir(subfolder_path) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            images_dict[subfolder] = images
        return images_dict
    else:
        images = [os.path.join(main_folder_name, file) for file in os.listdir(main_folder_name) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        return images

def get_images(main_folder_name):
    images = [os.path.join(main_folder_name, file) for file in os.listdir(main_folder_name) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return images


def select_image(Brand_option,brand_folder_images):
    if Brand_option:
        img = image_select(label="Select an image", images=brand_folder_images)
        if 'selected_image' not in st.session_state:
            st.session_state.selected_image = img

def create_mask_from_red_box(image_with_box_path, mask_output_path):
    # Load the image with the red box
    image_with_box = Image.open(image_with_box_path)
    st.image(image_with_box)
    image_np = np.array(image_with_box)
    
    # Define the red box color
    red_color = [255, 0, 0]

    # Create a mask image
    mask = np.zeros((image_np.shape[0], image_np.shape[1]), dtype=np.uint8)

    # Find the red box in the image
    red_box_indices = np.all(image_np[:, :, :3] == red_color, axis=-1)
    print("smndf",red_box_indices)
    # Fill the mask with white (255) in the area of the red box
    mask[red_box_indices] = 255

    # Save the mask image
    mask_image = Image.fromarray(mask)
    st.image(mask_image)
    mask_image.save(mask_output_path)
    return mask_image

def main():
    ## Brand Selection
    st.header("Generation Panel")
    Brand_option = st.selectbox(
            "Select a brand",
            ("Maruti Swift", "Maruti Ertiga", "Maruti Brezza", "Maruti Balena", "Maruti Dzire"),index=None)
    if Brand_option:
        st.session_state['brand'] = Brand_option

    st.write(' ')
    ## Generational model
    model_option = st.selectbox(
            "Select a Model",
            ("SDXL", "DALLE"),index=None)
    if model_option:
        st.session_state['model'] = model_option
    st.write(' ')

    ## View Selection
    view_option = st.selectbox(
            "Select a View",
            ("Front", "Back", "Side", "Auto"),index=None)
    if view_option:
        if view_option == "Auto":
            st.session_state['View'] = "Front"
        else:
            st.session_state['View'] = view_option

    st.write(' ')

    ## Image  Selection
    # st.header("Image Selection")
    if 'View' in st.session_state and 'brand' in st.session_state:
        main_folder_path = "Assets/brand_cars/"+ str(st.session_state['brand']) + '/' +str(st.session_state['View'])
        # brand_folder_images = get_images_by_folder(main_folder_path)
        brand_folder_images = get_images(main_folder_path)
    if 'View' in st.session_state:
        select_image(Brand_option,brand_folder_images)

    st.write(' ')

    ## Theme Selection
    if 'selected_image' in st.session_state:
        Theme = st.text_input("Enter a Theme",placeholder="Diwali background filled with colourful crackes and rockets")
        if 'Theme' not in st.session_state:
            st.session_state['Theme'] = ''
        st.session_state['Theme'] = Theme
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button('Diwali background filled with colourful crackes and rockets'):
                Theme = 'Diwali background filled with colourful crackes and rockets'
                st.session_state['Theme'] = Theme
        with col2:
            if st.button('Holi background filled with colourful smoke'):
                Theme = 'Holi background filled with colourful smoke'
                st.session_state['Theme'] = Theme
        with col3:
            if st.button('Christmas background with christmas tree and lights'):
                Theme = 'Christmas background with christmas tree and lights'
                st.session_state['Theme'] = Theme
        st.write("Theme entered:", st.session_state['Theme'])

    st.write(' ')

    ## Prompt
    if 'Theme' in st.session_state:
        Postive_prompt = st.text_input("Enter a prompt",placeholder="black background resembling a cityscape")
        if 'prompt' not in st.session_state:
            st.session_state['prompt'] = ''
        st.session_state['prompt'] = Postive_prompt
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button('hauntingly beautiful silhouette of an ancient castle against a dark, ominous sky'):
                Postive_prompt = 'hauntingly beautiful silhouette of an ancient castle against a dark, ominous sky'
                st.session_state['prompt'] = Postive_prompt
        with col2:
            if st.button('a mysterious, dark forest backdrop,sporadic bursts of colorful fireflies hovering'):
                Postive_prompt = 'a mysterious, dark forest backdrop,sporadic bursts of colorful fireflies hovering'
                st.session_state['prompt'] = Postive_prompt
        with col3:
            if st.button('gloomy black background resembling a cityscape at twilight'):
                Postive_prompt = 'gloomy black background resembling a cityscape at twilight'
                st.session_state['prompt'] = Postive_prompt
        st.write("Prompt entered:", Postive_prompt)
        st.session_state['prompt'] = Postive_prompt
        
        # print(st.session_state['prompt'])
        # print(st.session_state['Theme'])
    st.write(' ')

    ## generation button
    if 'prompt' in st.session_state and 'Theme' in st.session_state:
        col1, col2, col3  = st.columns(3)
        with col1:
            pass
        with col2:
            center_button = st.button('Generate Background')
        with col3 :
            pass
        
        if center_button:
            st.session_state['wait'] = True
            with st.spinner():
                while st.session_state:  
                    print(st.session_state)
                    time.sleep(3)
            




if __name__ == "__main__":
    main()