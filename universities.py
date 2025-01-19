import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import filter_data, calculate_metrics, metrics_filtration_range, filter_by_key


universities_df = pd.read_csv("data/universities.csv", sep=";", decimal=",")
teachers_df = pd.read_csv("data/academic_teachers.csv", sep=";", decimal=",")


def display_metrics(
    max_year: int,
    universities_df: pd.DataFrame,
    teachers_df: pd.DataFrame
) -> None:
    """Displays metrics for the number of universities and academic teachers in the selected year."""
    max_year = min(max_year, 2018)
    nr_universities = calculate_metrics(universities_df, max_year, mean=False)
    nr_teachers = calculate_metrics(teachers_df, max_year, mean=False)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=f"Number of academic teachers in {max_year}",
            value=f"{int(nr_teachers['sum'])}",
            delta=f"{nr_teachers['growth']:.2f}%",
        )
    with col2:
        st.metric(
            label=f"Number of universities in {max_year}",
            value=f"{int(nr_universities['sum'])}",
            delta=f"{nr_universities['growth']:.2f}%",
        )


def pie_chart(max_year: int, teachers_data: dict) -> None:
    """Displays a pie chart showing the percentage distribution of academic professors by type."""
    year = min(max_year, 2018)
    total_teachers = sum([
        len(teachers_data["assistant professor"]),
        len(teachers_data["associate professor"]),
        len(teachers_data["professor"]),
    ])

    assistant_professor_percentage = (len(teachers_data["assistant professor"]) / total_teachers) * 100
    associate_professor_percentage = (len(teachers_data["associate professor"]) / total_teachers) * 100
    professor_percentage = (len(teachers_data["professor"]) / total_teachers) * 100

    labels = ["Assistant Professor", "Associate Professor", "Professor"]
    values = [assistant_professor_percentage, associate_professor_percentage, professor_percentage]
    colors = ["royalblue", "orange", "green"]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])

    fig.update_layout(
        title=f"Percentage Distribution of Professor Types for {year}",
        showlegend=True,
    )

    st.plotly_chart(fig)


def teachers_graph(df: pd.DataFrame, year_range: tuple[int, int]) -> None:
    """Displays a line chart showing the number of academic teachers for each year in the given range."""
    filtered_df = metrics_filtration_range(df, year_range)
    display = filtered_df.sum()
    display.index = display.index.astype(str)

    st.subheader("Number of academic teachers YoY")
    st.line_chart(display)


def display_universities_tab(
    selected_regions: list[str], year_range: tuple[int, int]
) -> None:
    """Displays metrics, a pie chart, and a line chart for universities and academic teachers
    in the selected regions and year range."""
    teachers_filtered = filter_data(teachers_df, selected_regions)
    universities_data = {
        "universities": filter_data(universities_df, selected_regions),
        "academic teacher": filter_by_key(teachers_filtered, "nauczyciele akademiccy"),
        "assistant professor": filter_by_key(teachers_filtered, "asystenci"),
        "associate professor": pd.concat(
            [filter_by_key(teachers_filtered, "docenci"), filter_by_key(teachers_filtered, "adiunkci")]
        ),
        "professor": filter_by_key(teachers_filtered, "profesorowie"),
    }

    if teachers_filtered.shape[0] > 0:
        display_metrics(
            year_range[1],
            universities_data["universities"],
            universities_data["academic teacher"]
        )
        st.divider()
        pie_chart(year_range[1], universities_data)
        teachers_graph(universities_data["academic teacher"], year_range)
