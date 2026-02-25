from pathlib import Path
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
        response = requests.get(url)
        response.raise_for_status()

        file_path = download_dir / f"{name}.csv"
        if url.endswith(".zip"):
            file_path = download_dir / f"{name}.zip"

        file_path.write_bytes(response.content)


def merge_world_with_data(world: gpd.GeoDataFrame, data: pd.DataFrame, world_key: str, data_key: str) -> gpd.GeoDataFrame:
    data = data[~data[data_key].isin(["World", "Europe", "Asia", "Africa", "Oceania", "North America", "South America", "European Union", "High-income countries", "Low-income countries"])]
    return world.merge(data, how="left", left_on=world_key, right_on=data_key)


class OkavangoData:
    def __init__(self, base_dir: Path) -> None:
        self.download_dir = base_dir / "downloads"

        download_data(self.download_dir)

        self.forest_change = pd.read_csv(self.download_dir / "forest_change.csv")
        self.deforestation = pd.read_csv(self.download_dir / "deforestation.csv")
        self.protected_land = pd.read_csv(self.download_dir / "protected_land.csv")
        self.degraded_land = pd.read_csv(self.download_dir / "degraded_land.csv")
        self.biodiversity_conservation = pd.read_csv(self.download_dir / "biodiversity_conservation.csv")
        self.countries = gpd.read_file(self.download_dir / "countries.zip")