import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt

from data import OkavangoData, merge_world_with_data


def main():
    st.title("🌍 Environmental Data Explorer")
    st.markdown("Explore global environmental indicators using country-level maps and targeted visual summaries for a selected year")

    # ---------------- DATA LOAD ----------------
    data = OkavangoData(base_dir=Path("."))

    # ---------------- DATASET SELECTOR ----------------
    dataset_option = st.selectbox(
        "Which indicator would you like to explore?",
        (
            "Forest change",
            "Deforestation",
            "Protected land",
            "Degraded land",
            "Biodiversity conservation",
        ),
    )

    # ---------------- DATASET CONFIG ----------------
    if dataset_option == "Forest change":
        df = data.forest_change
        value_col = "net_change_forest_area"
        title = "Net Change in Forest Area"
        unit = "hectares"
        cmap = "RdYlGn"

    elif dataset_option == "Deforestation":
        df = data.deforestation
        value_col = "_1d_deforestation"
        title = "Annual Deforestation"
        unit = "hectares"
        cmap = "Reds"

    elif dataset_option == "Protected land":
        df = data.protected_land
        value_col = "er_lnd_ptld_zs"
        title = "Protected Land Share"
        unit = "% of land area"
        cmap = "Greens"

    elif dataset_option == "Degraded land":
        df = data.degraded_land
        value_col = "_15_3_1__ag_lnd_dgrd"
        title = "Degraded Land Share"
        unit = "% of land area"
        cmap = "YlOrRd"

    else:
        df = data.biodiversity_conservation
        value_col = "_15_a_1__dc_oda_bdvl"
        title = "ODA for Biodiversity Conservation"
        unit = "USD"
        cmap = "Blues"

    # ---------------- YEAR HANDLING ----------------
    years = sorted(df["year"].dropna().unique())
    if "year" not in st.session_state or st.session_state.year not in years:
        st.session_state.year = max(years)

    year = st.session_state.year
    year_data = df[df["year"] == year]

    # ---------------- MERGE WITH MAP ----------------
    world = merge_world_with_data(
        world=data.countries,
        data=year_data,
        world_key="NAME",
        data_key="entity",
    )

    # ================= MAP =================
    st.subheader(f"{title} ({year})")

    fig, ax = plt.subplots(figsize=(16, 8), dpi=120)
    world_plot = world.to_crs("ESRI:54030")

    world_plot.plot(
        column=value_col,
        ax=ax,
        cmap=cmap,
        legend=True,
        missing_kwds={"color": "#eeeeee", "label": "No data"},
    )

    ax.set_axis_off()
    plt.tight_layout()
    st.pyplot(fig)

    # ---------------- YEAR SLIDER ----------------
    st.session_state.year = st.slider(
        "Move the marker to explore different years:",
        min_value=min(years),
        max_value=max(years),
        value=year,
        step=1,
    )

    # ================= SECONDARY PLOT =================
    st.subheader(f"Key Insights of {year}")

    values = (
        world[["NAME", value_col]]
        .dropna()
        .sort_values(value_col)
    )

    fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=120)

    # -------- Forest change: gains vs losses --------
    if dataset_option == "Forest change":
        losses = values.head(5)
        gains = values.tail(5)

        ax2.barh(losses["NAME"], losses[value_col], color="#d73027")
        ax2.barh(gains["NAME"], gains[value_col], color="#1a9850")
        ax2.axvline(0, color="black", linewidth=0.8)

        ax2.set_title("Largest Forest Losses and Gains")
        ax2.set_xlabel(unit)

    # -------- Deforestation: top contributors --------
    elif dataset_option == "Deforestation":
        top = values.sort_values(value_col, ascending=False).head(10).iloc[::-1]

        ax2.barh(top["NAME"], top[value_col], color="#b2182b")
        ax2.set_title("Top Deforesting Countries")
        ax2.set_xlabel(unit)

    # -------- Protected land: top protectors --------
    elif dataset_option == "Protected land":
        top = values.sort_values(value_col, ascending=False).head(10).iloc[::-1]

        ax2.barh(top["NAME"], top[value_col], color="#238b45")
        ax2.set_title("Countries with Highest Protected Land Share")
        ax2.set_xlabel(unit)

    # -------- Degraded land: most affected --------
    elif dataset_option == "Degraded land":
        top = values.sort_values(value_col, ascending=False).head(10).iloc[::-1]

        ax2.barh(top["NAME"], top[value_col], color="#d7301f")
        ax2.set_title("Countries with Highest Land Degradation")
        ax2.set_xlabel(unit)

    # -------- Biodiversity funding: top recipients --------
    else:
        top = values.sort_values(value_col, ascending=False).head(10).iloc[::-1]

        ax2.barh(top["NAME"], top[value_col], color="#2171b5")
        ax2.set_title("Top Recipients of Biodiversity Conservation Funding")
        ax2.set_xlabel(unit)

    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig2)


if __name__ == "__main__":
    main()