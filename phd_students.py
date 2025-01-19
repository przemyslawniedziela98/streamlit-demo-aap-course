import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import filter_data, calculate_metrics, metrics_filtration_range, filter_by_key


phd_students_df = pd.read_csv("data/phd_students.csv", sep=";", decimal=",")


def display_metrics(
    max_year: int,
    general_nr_of_phd_students: pd.DataFrame,
    men_nr_of_phd_students: pd.DataFrame,
    women_nr_of_phd_students: pd.DataFrame,
) -> None:
    """Displays the calculated metrics for the selected year for PhD students by gender."""
    nr_phd_students = calculate_metrics(general_nr_of_phd_students, max_year, mean=False)
    nr_men_phd_students = calculate_metrics(men_nr_of_phd_students, max_year, mean=False)
    nr_women_phd_students = calculate_metrics(women_nr_of_phd_students, max_year, mean=False)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=f"PhD students in {max_year}",
            value=f"{int(nr_phd_students['sum'])}",
            delta=f"{nr_phd_students['growth']:.2f}%",
        )
        st.metric(
            label=f"PhD male students in {max_year}",
            value=f"{int(nr_men_phd_students['sum'])}",
            delta=f"{nr_men_phd_students['growth']:.2f}%",
        )
    with col2:
        st.metric(
            label=f"PhD female students in {max_year}",
            value=f"{int(nr_women_phd_students['sum'])}",
            delta=f"{nr_women_phd_students['growth']:.2f}%",
        )


def bar_chart(
    year_range: tuple[int, int],
    men_nr_of_phd_students: pd.DataFrame,
    women_nr_of_phd_students: pd.DataFrame,
) -> None:
    """Generates and displays a bar chart comparing male and female PhD students for each year. """
    years = list(range(max(year_range[0], 2019), year_range[1] + 1))
    men_counts = metrics_filtration_range(men_nr_of_phd_students, year_range).sum()
    women_counts = metrics_filtration_range(women_nr_of_phd_students, year_range).sum()

    fig = go.Figure(
        data=[
            go.Bar(name="Men", x=years, y=men_counts),
            go.Bar(name="Women", x=years, y=women_counts),
        ]
    )

    fig.update_layout(
        barmode="group",
        title="PhD Students by Gender YoY",
        xaxis_title="Year",
        yaxis_title="Number of PhD Students",
    )

    st.plotly_chart(fig)


def display_phd_students_tab(
    selected_regions: list[str], year_range: tuple[int, int]
) -> None:
    """Displays the metrics and bar chart for PhD students in the selected regions and year range."""
    phd_students_filtered = filter_data(phd_students_df, selected_regions)
    phd_students_data = {
        "general": filter_by_key(phd_students_filtered, "ogółem;uc"),
        "men": filter_by_key(phd_students_filtered, "mężczyźni"),
        "women": filter_by_key(phd_students_filtered, "kobiety"),
    }

    if phd_students_filtered.shape[0] > 0:
        display_metrics(
            year_range[1],
            phd_students_data["general"],
            phd_students_data["men"],
            phd_students_data["women"],
        )
        st.divider()
        bar_chart(year_range, phd_students_data["men"], phd_students_data["women"])

