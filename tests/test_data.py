from app.data import download_data
import geopandas as gpd
import pandas as pd
from app.data import merge_world_with_data

def test_download_data_creates_files(tmp_path):
    """Tests that download_data creates the expected files in the specified directory."""
    download_dir = tmp_path / "downloads"

    download_data(download_dir)

    expected_files = [
        "forest_change.csv",
        "deforestation.csv",
        "protected_land.csv",
        "degraded_land.csv",
        "biodiversity_conservation.csv",
        "countries.zip",
    ]

    for file_name in expected_files:
        assert (download_dir / file_name).exists()

def test_merge_world_with_data_basic():
    """Tests that merge_world_with_data correctly merges a simple world GeoDataFrame with a data DataFrame."""
    world = gpd.GeoDataFrame(
        {"name": ["Portugal", "Spain"],
        "geometry": [None, None],})

    data = pd.DataFrame(
        {
            "country": ["Portugal", "Spain"],
            "value": [10.0, 20.0],
        }
    )

    merged = merge_world_with_data(
        world=world,
        data=data,
        world_key="name",
        data_key="country",
    )

    assert "value" in merged.columns
    assert merged.loc[merged["name"] == "Portugal", "value"].iloc[0] == 10.0