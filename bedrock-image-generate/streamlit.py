import streamlit as st
import base64
from main import generateTextToImage, ImageToImage

st.title("AWS Bedrock Image Generator")

mode = st.selectbox("Select Mode", ["text-to-image", "image-to-image"])

prompt = st.text_area("Prompt")
negative_prompt = st.text_input("Negative Prompt")
model_id = st.text_input("Model ID", value="stability.sd3-5-large-v1:0")
aspect_ratio = st.selectbox("Aspect Ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
output_format = st.selectbox("Output Format", ["png", "jpeg", "webp"])

if mode == "text-to-image":
    seed = st.number_input("Seed", value=123456789, step=100)
    if st.button("Generate Image"):
        if prompt:
            image_path = generateTextToImage(prompt, model_id, negative_prompt, seed, aspect_ratio, output_format)
            st.image(image_path, caption="Generated Image")
            st.success(f"Image saved to {image_path}")
        else:
            st.error("Please enter a prompt")

elif mode == "image-to-image":
    init_image_file = st.file_uploader("Upload Initial Image", type=["png", "jpg", "jpeg"])
    strength = st.slider("Strength", 0.0, 1.0, 0.6, step=0.1)
    seed = st.number_input("Seed", value=123456789, step=1)
    if st.button("Generate Image"):
        if prompt and init_image_file:
            image_b64 = base64.b64encode(init_image_file.read()).decode()
            image_path = ImageToImage(prompt, model_id, negative_prompt, seed, output_format, image_b64, strength)
            st.image(image_path, caption="Generated Image")
            st.success(f"Image saved to {image_path}")
        else:
            st.error("Please enter a prompt and upload an initial image")
