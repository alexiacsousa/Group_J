import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt

from data import OkavangoData, merge_world_with_data

def main():
    st.title("Okavango – Environmental Data Explorer")

    data = OkavangoData(base_dir=Path("."))

    dataset_option = st.selectbox(
        "Select dataset",
        (
            "Forest change",
            "Deforestation",
            "Protected land",
            "Degraded land",
            "Biodiversity conservation",
        ),
    )
    if dataset_option == "Forest change":
        df = data.forest_change
        value_col = "net_change_forest_area"

    elif dataset_option == "Deforestation":
        df = data.deforestation
        value_col = "_1d_deforestation"

    elif dataset_option == "Protected land":
        df = data.protected_land
        value_col = "er_lnd_ptld_zs"

    elif dataset_option == "Degraded land":
        df = data.degraded_land
        value_col = "_15_3_1__ag_lnd_dgrd"

    else:
        df = data.biodiversity_conservation
        value_col = "_15_a_1__dc_oda_bdvl"

    world_merged = merge_world_with_data(
    world=data.countries,
    data=df,
    world_key="NAME",
    data_key= "entity",
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    world_merged.plot(
        column=value_col,
        ax=ax,
        legend=True,
        missing_kwds={"color": "lightgrey"},
    )
    ax.set_axis_off()
    st.pyplot(fig)

    st.subheader("Top and Bottom Countries")

    latest_year = df["year"].max()
    latest_data = df[df["year"] == latest_year]

    ranked = latest_data.sort_values(value_col)
    bottom_5 = ranked.head(5)
    top_5 = ranked.tail(5)

    fig2, ax2 = plt.subplots()
    ax2.barh(bottom_5["entity"], bottom_5[value_col])
    ax2.barh(top_5["entity"], top_5[value_col])
    st.pyplot(fig2)

if __name__ == "__main__":
    main()