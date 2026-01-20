import streamlit as st
import base64
from main import generateTextToImage, ImageToImage


st.set_page_config(
    page_title="AWS Bedrock Image Generator",
    page_icon="🎨",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #888;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 1rem;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">🎨 AWS Bedrock Image Generator</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-title">Stable Diffusion 3.5 • Text-to-Image & Image-to-Image</div>',
            unsafe_allow_html=True)


# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Settings")

    mode = st.selectbox(
        "Mode",
        ["text-to-image", "image-to-image"]
    )

    model_id = st.text_input(
        "Model ID",
        value="stability.sd3-5-large-v1:0"
    )

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"]
    )

    output_format = st.selectbox(
        "Output Format",
        ["png", "jpeg", "webp"]
    )

    seed = st.number_input(
        "Seed",
        value=123456789,
        step=1,
        help="Use same seed to reproduce similar images"
    )

# Main Layout
left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("📝 Prompt")

    prompt = st.text_area(
        "Prompt",
        placeholder="Ultra-realistic studio photo, cinematic lighting, sharp focus...",
        height=140
    )

    negative_prompt = st.text_input(
        "Negative Prompt",
        placeholder="blurry, low quality, distorted"
    )

    if mode == "image-to-image":
        st.subheader("🖼️ Initial Image")

        init_image_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg"]
        )

        strength = st.slider(
            "Transformation Strength",
            0.0, 1.0, 0.6,
            step=0.05,
            help="Higher = more deviation from original image"
        )

        if init_image_file:
            st.image(init_image_file, caption="Input Image",
                     use_container_width=True)

    generate_btn = st.button("🚀 Generate Image")


# Generation Logic + Loading
with right_col:
    st.subheader("📤 Output")

    if generate_btn:
        if not prompt:
            st.error("Please enter a prompt.")
        elif mode == "image-to-image" and not init_image_file:
            st.error("Please upload an initial image.")
        else:
            with st.spinner("Generating image… this may take a few seconds ⏳"):
                try:
                    if mode == "text-to-image":
                        image_path = generateTextToImage(
                            prompt=prompt,
                            model_id=model_id,
                            negative_prompt=negative_prompt,
                            seed=seed,
                            aspect_ratio=aspect_ratio,
                            output_format=output_format
                        )

                    else:
                        image_b64 = base64.b64encode(
                            init_image_file.read()
                        ).decode()

                        image_path = ImageToImage(
                            prompt=prompt,
                            model_id=model_id,
                            negative_prompt=negative_prompt,
                            seed=seed,
                            output_format=output_format,
                            image_b64=image_b64,
                            strength=strength
                        )

                    st.success("✅ Image generated successfully")
                    st.image(image_path, use_container_width=True)
                    st.caption(f"Saved at: `{image_path}`")

                except Exception as e:
                    st.error("❌ Image generation failed")
                    st.exception(e)
