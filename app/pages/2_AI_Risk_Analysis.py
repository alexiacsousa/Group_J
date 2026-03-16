import sys
import streamlit as st
import math
import requests
import yaml
import csv
import pandas as pd
from pathlib import Path
from PIL import Image
from io import BytesIO
from datetime import datetime
from ollama import Client
from shapely.geometry import Point

sys.path.append(str(Path(__file__).parent.parent))
from data import EnvironmentalData


# --- LOAD CONFIG ---
def load_config() -> dict:
    """Loads the models.yaml configuration file."""
    config_path = Path(__file__).parent.parent.parent / "models.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

# --- OLLAMA CONNECTION ---
ollama_client = Client(host=config["ollama"]["host"])

# --- DATABASE ---
DB_PATH = Path(__file__).parent.parent.parent / "database" / "images.csv"
DB_COLUMNS = [
    "timestamp",
    "latitude",
    "longitude",
    "zoom",
    "image_path",
    "image_prompt",
    "image_model",
    "image_model_temperature",
    "image_description",
    "text_prompt",
    "text_model",
    "text_model_temperature",
    "danger_flag",
    "risk_level",
    "text_description",
]

def init_database() -> None:
    """Creates the database directory and images.csv if they do not exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        with open(DB_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=DB_COLUMNS)
            writer.writeheader()

def check_existing_entry(lat: float, lon: float, zoom: int) -> dict | None:
    """Checks if an entry for the given coordinates and zoom already exists in the database."""
    if not DB_PATH.exists():
        return None
    df = pd.read_csv(DB_PATH)
    match = df[(df["latitude"] == lat) & (df["longitude"] == lon) & (df["zoom"] == zoom)]
    if not match.empty:
        return match.iloc[-1].to_dict()
    return None

def append_to_database(row: dict) -> None:
    """Appends a new row to the images.csv database."""
    with open(DB_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DB_COLUMNS)
        writer.writerow(row)

def parse_assessment(assessment: str) -> tuple[str, str]:
    """Extracts danger flag (Y/N) and risk level (Low/Medium/High) from the assessment text."""
    danger_flag = "N"
    risk_level = "Unknown"

    for line in assessment.splitlines():
        line_lower = line.lower()
        if line_lower.startswith("danger:"):
            value = line.split(":", 1)[1].strip().upper()
            danger_flag = "Y" if "YES" in value or value == "Y" else "N"
        elif line_lower.startswith("risk level:"):
            value = line.split(":", 1)[1].strip()
            if any(level in value.lower() for level in ["low", "medium", "high"]):
                risk_level = value.strip()

    return danger_flag, risk_level


# --- COUNTRY LOOKUP ---
@st.cache_data
def load_environmental_data() -> EnvironmentalData:
    """Loads and caches the environmental data."""
    return EnvironmentalData(base_dir=Path(__file__).parent.parent.parent)

def get_country_from_coordinates(lat: float, lon: float, data: EnvironmentalData) -> str | None:
    """Returns the country name for the given coordinates using geopandas point-in-polygon."""
    point = Point(lon, lat)
    match = data.countries[data.countries.geometry.contains(point)]
    if not match.empty:
        return match.iloc[0]["NAME"]
    return None

def get_country_stats(country_name: str, data: EnvironmentalData) -> list[dict]:
    """Returns a list of dicts with stat, value and source for the given country."""
    stats = []

    fc = data.forest_change[data.forest_change["entity"] == country_name]
    if not fc.empty:
        latest = fc.sort_values("year").iloc[-1]
        stats.append({
            "label": f"Annual forest change ({int(latest['year'])})",
            "value": f"{latest['net_change_forest_area']:,.0f} hectares",
            "source": "ourworldindata.org/deforestation",
        })

    defor = data.deforestation[data.deforestation["entity"] == country_name]
    if not defor.empty:
        latest = defor.sort_values("year").iloc[-1]
        stats.append({
            "label": f"Annual deforestation ({int(latest['year'])})",
            "value": f"{latest['_1d_deforestation']:,.0f} hectares",
            "source": "ourworldindata.org/deforestation",
        })

    prot = data.protected_land[data.protected_land["entity"] == country_name]
    if not prot.empty:
        latest = prot.sort_values("year").iloc[-1]
        stats.append({
            "label": f"Protected land ({int(latest['year'])})",
            "value": f"{latest['er_lnd_ptld_zs']:.1f}% of land area",
            "source": "ourworldindata.org/sdgs/life-on-land",
        })

    degrad = data.degraded_land[data.degraded_land["entity"] == country_name]
    if not degrad.empty:
        latest = degrad.sort_values("year").iloc[-1]
        stats.append({
            "label": f"Degraded land ({int(latest['year'])})",
            "value": f"{latest['_15_3_1__ag_lnd_dgrd']:.1f}% of land area",
            "source": "ourworldindata.org/sdgs/life-on-land",
        })

    return stats

def format_stats_for_prompt(stats: list[dict]) -> str:
    """Formats the country stats list into a plain string for the AI prompt."""
    if not stats:
        return "No country-level statistics available."
    return "\n".join([f"{s['label']}: {s['value']}" for s in stats])


# --- IMAGE AVAILABILITY CHECK ---
def is_image_unavailable(image_desc: str) -> bool:
    """Checks if the vision model indicated that no imagery is available."""
    keywords = [
        "no data", "not available", "no image", "blank", "black",
        "no imagery", "unavailable", "map data not available",
        "no map data", "not yet available", "no satellite",
    ]
    return any(keyword in image_desc.lower() for keyword in keywords)


# --- HELPER FUNCTIONS ---
def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> tuple[int, int]:
    """Calculates ESRI map tile coordinates."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def get_esri_satellite_image(lat: float, lon: float, zoom: int) -> bytes:
    """Downloads the image tile from ESRI."""
    x, y = deg2num(lat, lon, zoom)
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
    headers = {"User-Agent": "Okavango-Hackathon-App/1.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.content

def pull_model_if_missing(model_name: str) -> None:
    """Checks if Ollama has the model downloaded, and pulls it if not."""
    try:
        models_info = ollama_client.list()
        existing_models = []

        if hasattr(models_info, "models"):
            for m in models_info.models:
                existing_models.append(m.model)
        else:
            for m in models_info.get("models", []):
                model_id = m.get("model", m.get("name", ""))
                existing_models.append(model_id)

        if model_name not in existing_models and f"{model_name}:latest" not in existing_models:
            with st.spinner(f"Downloading {model_name} from Ollama... (This might take a few minutes)"):
                ollama_client.pull(model_name)

    except Exception as e:
        st.error(f"Ollama Connection Error: {e}")
        st.info("Make sure you can see 'Ollama is running' when you visit http://127.0.0.1:11434 in your browser.")
        st.stop()


# --- DISPLAY RESULTS ---
def display_results(image_bytes: bytes, image_path: Path, image_desc: str, assessment: str, danger_flag: str, risk_level: str, country_name: str | None, stats: list[dict]) -> None:
    """Displays the AI description, country statistics and risk assessment."""
    st.markdown("---")
    st.subheader("AI Vision Description")
    st.write(image_desc)

    st.markdown("---")
    st.subheader(f"📊 Most Recent Country Statistics: {country_name if country_name else 'N/A'}")
    if stats:
        stats_text = "\n".join([f"{s['label']}: {s['value']}" for s in stats])
        st.code(stats_text)
        sources = sorted(set(s["source"] for s in stats))
        st.caption("Sources: " + " · ".join(sources))
    else:
        st.warning("No recent statistical data available from ourworldindata.org")

    st.markdown("---")
    st.subheader("Environmental Risk Assessment")

    # Parse assessment lines
    parsed = {}
    for line in assessment.splitlines():
        for key in ["Danger", "Risk level", "Main risks", "Explanation"]:
            if line.lower().startswith(key.lower() + ":"):
                parsed[key] = line.split(":", 1)[1].strip()

    # Overall indicator — color based on risk level
    risk_lower = risk_level.lower()
    if risk_lower == "high":
        st.error(f"🔴 **Risk Level: {risk_level}**")
    elif risk_lower == "medium":
        st.warning(f"🟡 **Risk Level: {risk_level}**")
    else:
        st.success(f"🟢 **Risk Level: {risk_level}**")

    # Main risks — triangle only if high
    main_risks = parsed.get("Main risks", "N/A")
    risks_prefix = "⚠️ " if risk_lower == "high" else ""
    st.markdown(f"**{risks_prefix}Main Risks:** {main_risks}")

    # Explanation
    explanation = parsed.get("Explanation", "")
    if explanation and not any(
        explanation.lower().startswith(k.lower())
        for k in ["danger:", "risk level:", "main risks:"]
    ):
        st.markdown(f"**Explanation:** {explanation}")
    else:
        st.markdown("**Explanation:** Not available for this assessment.")


# --- MAIN APP ---
def main():
    """AI Workflow page for satellite image analysis and environmental risk assessment."""
    st.title("🤖 AI Workflow: Environmental Analysis")

    init_database()

    env_data = load_environmental_data()

    vision_model = config["image_analysis"]["model"]
    vision_prompt = config["image_analysis"]["prompt"]
    vision_temperature = config["image_analysis"]["temperature"]
    text_model = config["risk_analysis"]["model"]
    text_prompt = config["risk_analysis"]["prompt"]
    text_temperature = config["risk_analysis"]["temperature"]

    # 1. WIDGETS
    col1, col2, col3 = st.columns(3)
    with col1:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=38.7169, step=0.01)
    with col2:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-9.1399, step=0.01)
    with col3:
        zoom = st.number_input("Zoom Level", min_value=0, max_value=19, value=15, step=1)

    # 2. STEP 1 — SHOW SATELLITE IMAGE
    if st.button("Preview Satellite Image", type="secondary"):
        with st.spinner("Downloading satellite image..."):
            try:
                image_bytes = get_esri_satellite_image(lat, lon, zoom)
                st.session_state["image_bytes"] = image_bytes
                st.session_state["image_lat"] = lat
                st.session_state["image_lon"] = lon
                st.session_state["image_zoom"] = zoom
                st.session_state["analysis_done"] = False
            except Exception as e:
                st.error(f"⚠️ No image available for these coordinates: {e}")
                st.session_state.pop("image_bytes", None)

    # 3. DISPLAY IMAGE IF AVAILABLE
    if "image_bytes" in st.session_state:
        image_bytes = st.session_state["image_bytes"]
        image = Image.open(BytesIO(image_bytes))

        images_dir = Path(__file__).parent.parent.parent / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        filename = f"esri_{st.session_state['image_lat']}_{st.session_state['image_lon']}_z{st.session_state['image_zoom']}.jpg"
        image_path = images_dir / filename

        # COUNTRY LOOKUP
        country_name = get_country_from_coordinates(
            st.session_state["image_lat"],
            st.session_state["image_lon"],
            env_data,
        )
        stats = get_country_stats(country_name, env_data) if country_name else []

        st.markdown("---")
        st.subheader("Satellite Imagery")
        st.image(image, caption=f"Lat: {st.session_state['image_lat']}, Lon: {st.session_state['image_lon']}, Zoom: {st.session_state['image_zoom']}", use_container_width=True)

        if country_name:
            st.info(f"📍 Detected country: **{country_name}**")

        # 4. CHECK DATABASE BEFORE SHOWING ANALYZE BUTTON
        existing = check_existing_entry(
            st.session_state["image_lat"],
            st.session_state["image_lon"],
            st.session_state["image_zoom"],
        )

        if existing and not st.session_state.get("analysis_done"):
            st.info("📦 Results loaded from database cache.")
            image_path = Path(existing["image_path"])
            if image_path.exists():
                cached_image_bytes = image_path.read_bytes()
            else:
                st.warning("Cached image file not found, re-downloading...")
                cached_image_bytes = get_esri_satellite_image(lat, lon, zoom)
                image_path.write_bytes(cached_image_bytes)
            display_results(
                cached_image_bytes,
                image_path,
                existing["image_description"],
                existing["text_description"],
                existing["danger_flag"],
                existing["risk_level"],
                country_name,
                stats,
            )

        elif not st.session_state.get("analysis_done"):
            # 5. STEP 2 — ANALYZE BUTTON
            if st.button("🔍 Analyze with AI", type="primary"):
                image_path.write_bytes(image_bytes)

                # VISION AI
                pull_model_if_missing(vision_model)
                with st.spinner(f"Analyzing image with {vision_model}..."):
                    vision_res = ollama_client.generate(
                        model=vision_model,
                        prompt=vision_prompt,
                        images=[image_bytes]
                    )
                    image_desc = vision_res.response

                # CHECK IF IMAGE IS UNAVAILABLE
                if is_image_unavailable(image_desc):
                    st.warning("🛰️ No satellite imagery available for these coordinates. Risk assessment cannot be performed.")
                    return

                # TEXT AI — with coordinates and country stats
                pull_model_if_missing(text_model)
                stats_for_prompt = format_stats_for_prompt(stats)
                full_prompt = (
                    f"{text_prompt}\n\n"
                    f"Coordinates: {st.session_state['image_lat']}, {st.session_state['image_lon']}\n"
                    f"Country: {country_name if country_name else 'Unknown'}\n"
                    f"Country statistics:\n{stats_for_prompt}\n\n"
                    f"Satellite image description:\n{image_desc}"
                )
                with st.spinner(f"Evaluating risk with {text_model}..."):
                    text_res = ollama_client.generate(model=text_model, prompt=full_prompt)
                    assessment = text_res.response.strip()

                # PARSE AND SAVE
                danger_flag, risk_level = parse_assessment(assessment)

                append_to_database({
                    "timestamp": datetime.now().isoformat(),
                    "latitude": st.session_state["image_lat"],
                    "longitude": st.session_state["image_lon"],
                    "zoom": st.session_state["image_zoom"],
                    "image_path": str(image_path),
                    "image_prompt": vision_prompt,
                    "image_model": vision_model,
                    "image_model_temperature": vision_temperature,
                    "image_description": image_desc,
                    "text_prompt": text_prompt,
                    "text_model": text_model,
                    "text_model_temperature": text_temperature,
                    "danger_flag": danger_flag,
                    "risk_level": risk_level,
                    "text_description": assessment,
                })

                st.session_state["analysis_done"] = True
                display_results(image_bytes, image_path, image_desc, assessment, danger_flag, risk_level, country_name, stats)


if __name__ == "__main__":
    main()