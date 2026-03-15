from pathlib import Path
from pydantic import BaseModel
import requests
import geopandas as gpd
import pandas as pd


def download_data(download_dir: Path) -> None:
    """Downloads most recent data files into the downloads directory"""
    download_dir.mkdir(parents=True, exist_ok=True)

    urls = {
        "forest_change": "https://ourworldindata.org/grapher/annual-change-forest-area.csv?v=1&csvType=full&useColumnShortNames=true",
        "deforestation": "https://ourworldindata.org/grapher/annual-deforestation.csv?v=1&csvType=full&useColumnShortNames=true",
        "protected_land": "https://ourworldindata.org/grapher/terrestrial-protected-areas.csv?v=1&csvType=full&useColumnShortNames=true",
        "degraded_land": "https://ourworldindata.org/grapher/share-degraded-land.csv?v=1&csvType=full&useColumnShortNames=true",
        "biodiversity_conservation": "https://ourworldindata.org/grapher/total-oda-for-biodiversity-by-recipient.csv?v=1&csvType=full&useColumnShortNames=true",
        "countries": "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip",
    }

    for name, url in urls.items():
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        file_path = download_dir / f"{name}.csv"
        if url.endswith(".zip"):
            file_path = download_dir / f"{name}.zip"

        file_path.write_bytes(response.content)


def merge_world_with_data(world: gpd.GeoDataFrame, data: pd.DataFrame, world_key: str, data_key: str) -> gpd.GeoDataFrame:
    """Merges map data with the provided dataset."""

    if world_key not in world.columns:
        raise KeyError(f"'{world_key}' not found in world columns: {list(world.columns)}")

    if data_key not in data.columns:
        raise KeyError(f"'{data_key}' not found in data columns: {list(data.columns)}")

    return world.merge(data, how="left", left_on=world_key, right_on=data_key)

class _Config(BaseModel):
    """Internal pydantic model for validating EnvironmentalData input parameters."""
    base_dir: Path

class EnvironmentalData:
    """Handles downloading, loading and merging of environmental datasets from Our World in Data."""
    def __init__(self, base_dir: Path) -> None:
        config = _Config(base_dir=base_dir)
        self.download_dir = config.base_dir / "downloads"

        download_data(self.download_dir)

        self.forest_change = pd.read_csv(self.download_dir / "forest_change.csv")
        self.deforestation = pd.read_csv(self.download_dir / "deforestation.csv")
        self.protected_land = pd.read_csv(self.download_dir / "protected_land.csv")
        self.degraded_land = pd.read_csv(self.download_dir / "degraded_land.csv")
        self.biodiversity_conservation = pd.read_csv(self.download_dir / "biodiversity_conservation.csv")
        self.countries = gpd.read_file(self.download_dir / "countries.zip")

        self.world_forest_change = merge_world_with_data(self.countries, self.forest_change, "NAME", "entity")
        self.world_deforestation = merge_world_with_data(self.countries, self.deforestation, "NAME", "entity")
        self.world_protected_land = merge_world_with_data(self.countries, self.protected_land, "NAME", "entity")
        self.world_degraded_land = merge_world_with_data(self.countries, self.degraded_land, "NAME", "entity")
        self.world_biodiversity = merge_world_with_data(self.countries, self.biodiversity_conservation, "NAME", "entity")