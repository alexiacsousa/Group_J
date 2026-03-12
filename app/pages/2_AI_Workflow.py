import streamlit as st
import math
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
from ollama import Client

# --- EXPLICIT OLLAMA CONNECTION ---
# This forces Python to look at the exact local port, fixing Windows localhost bugs.
ollama_client = Client(host='http://127.0.0.1:11434')

# --- HELPER FUNCTIONS ---
def deg2num(lat_deg, lon_deg, zoom):
    """Calculates ESRI map tile coordinates."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def get_esri_satellite_image(lat, lon, zoom):
    """Downloads the image tile from ESRI."""
    x, y = deg2num(lat, lon, zoom)
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
    headers = {"User-Agent": "Okavango-Hackathon-App/1.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.content

def pull_model_if_missing(model_name):
    """Checks if Ollama has the model downloaded, and pulls it if not."""
    try:
        models_info = ollama_client.list()
        existing_models = []
        
        # Check for both newer (object) and older (dictionary) Ollama library formats
        if hasattr(models_info, 'models'):
            for m in models_info.models:
                existing_models.append(m.model)
        else:
            for m in models_info.get('models', []):
                # Safely grab 'model' or fallback to 'name'
                model_id = m.get('model', m.get('name', ''))
                existing_models.append(model_id)
                
        # If the model isn't found, trigger the download
        if model_name not in existing_models and f"{model_name}:latest" not in existing_models:
            with st.spinner(f"Downloading {model_name} from Ollama... (This might take a few minutes)"):
                ollama_client.pull(model_name)
                
    except Exception as e:
        st.error(f"Ollama Connection Error: {e}")
        st.info("Make sure you can see 'Ollama is running' when you visit http://127.0.0.1:11434 in your browser.")
        st.stop()

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="AI Workflow", page_icon="🤖", layout="wide")
    st.title("🤖 AI Workflow: Environmental Analysis")
    
    # 1. WIDGETS
    col1, col2, col3 = st.columns(3)
    with col1:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=-3.0, step=0.01)
    with col2:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-3.0, step=0.01)
    with col3:
        zoom = st.number_input("Zoom Level", min_value=0, max_value=19, value=15, step=1)

    if st.button("Analyze Location", type="primary"):
        
        # 2. IMAGE DOWNLOAD
        images_dir = Path("images")
        images_dir.mkdir(parents=True, exist_ok=True)
        filename = f"esri_{lat}_{lon}_z{zoom}.jpg"
        file_path = images_dir / filename

        with st.spinner("Downloading satellite image..."):
            try:
                image_bytes = get_esri_satellite_image(lat, lon, zoom)
                file_path.write_bytes(image_bytes)
            except Exception as e:
                st.error(f"Error downloading image: {e}")
                return
        
        st.markdown("---")
        img_col, desc_col = st.columns(2)
        
        with img_col:
            st.subheader("Satellite Imagery")
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption=f"Saved to: {file_path}", use_container_width=True)

        # 3. VISION AI (Image Description)
        vision_model = "moondream" 
        with desc_col:
            st.subheader("AI Vision Description")
            pull_model_if_missing(vision_model)
            with st.spinner(f"Analyzing image with {vision_model}..."):
                vision_res = ollama_client.generate(
                    model=vision_model,
                    prompt="Describe this satellite image in detail. Focus on geographical, man-made, and environmental features.",
                    images=[image_bytes]
                )
                image_desc = vision_res.get("response", "No description generated.")
                st.write(image_desc)
        
        # 4. TEXT AI (Risk Assessment)
        st.markdown("---")
        st.subheader("Environmental Risk Assessment")
        text_model = "llama3.2:1b" 
        
        prompt = f"""
        Based on this satellite image description, is this area exhibiting signs of environmental danger, degradation, or risk? 
        Answer strictly 'YES' or 'NO' on the first line, followed by a brief 1-sentence explanation.
        
        Description: {image_desc}
        """
        
        pull_model_if_missing(text_model)
        with st.spinner(f"Evaluating risk with {text_model}..."):
            text_res = ollama_client.generate(model=text_model, prompt=prompt)
            assessment = text_res.get("response", "Could not evaluate.").strip()
        
        # 5. VISUAL INDICATOR
        if assessment.upper().startswith("YES"):
            st.error("🚨 **ENVIRONMENTAL RISK DETECTED**")
            st.warning(assessment)
        else:
            st.success("✅ **NO IMMEDIATE RISK DETECTED**")
            st.info(assessment)

if __name__ == "__main__":
    main()