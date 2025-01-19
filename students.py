import json
import pandas as pd
import plotly.express as px
import streamlit as st
from unidecode import unidecode
from utils import METRICS_DROPDOWN, filter_data, calculate_metrics, metrics_filtration_range


data = {
    'stem_data': pd.read_csv('data/percent_stem_students.csv', sep=';', decimal=','),
    'students_per_10k': pd.read_csv('data/students_per_10k.csv', sep=';', decimal=','),
    'graduates_per_10k': pd.read_csv('data/graduates_per_10k.csv', sep=';', decimal=','),
    'masters_graduates': pd.read_csv('data/masters_graduates.csv', sep=';', decimal=','),
    'foreigners': pd.read_csv('data/foreigners.csv', sep=';', decimal=','),
    'scholarships': pd.read_csv('data/scholarships.csv', sep=';', decimal=',')
}


def display_metrics(
    max_year: int,
    stem_data_filtered: pd.DataFrame,
    students_per_10k_filtered: pd.DataFrame,
    graduates_per_10k_filtered: pd.DataFrame,
    masters_graduates_filtered: pd.DataFrame,
    foreigners_filtered: pd.DataFrame,
    scholarships_filtered: pd.DataFrame
) -> None:
    """Displays the calculated metrics for the selected year."""
    stem_metrics = calculate_metrics(stem_data_filtered, max_year)
    students_metrics = calculate_metrics(students_per_10k_filtered, max_year)
    graduates_metrics = calculate_metrics(graduates_per_10k_filtered, max_year)
    masters_metrics = calculate_metrics(masters_graduates_filtered, max_year, mean = False)
    foreigners_metrics = calculate_metrics(foreigners_filtered, max_year)
    scholarships_metrics = calculate_metrics(scholarships_filtered, max_year, mean = False)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=f"Master graduates in {max_year}",
            value=f"{int(masters_metrics['sum'])}",
            delta=f"{masters_metrics['growth']:.2f}%"
        )
        st.metric(
            label=f"STEM Students (%) in {max_year}",
            value=f"{stem_metrics['average']:.2f}%",
            delta=f"{stem_metrics['growth']:.2f}%"
        )
        st.metric(
            label=f"Students with scholarship in {max_year}",
            value=f"{int(scholarships_metrics['sum'])}",
            delta=f"{scholarships_metrics['growth']:.2f}%"
        )
    with col2:
        st.metric(
            label=f"Students per 10k citizens in {max_year}",
            value=f"{students_metrics['average']:.2f}",
            delta=f"{students_metrics['growth']:.2f}%"
        )
        st.metric(
            label=f"Graduates per 10k citizens in {max_year}",
            value=f"{graduates_metrics['average']:.2f}",
            delta=f"{graduates_metrics['growth']:.2f}%"
        )
        st.metric(
            label=f"International students (%) in {max_year}",
            value=f"{int(foreigners_metrics['average'])}%",
            delta=f"{int(foreigners_metrics['growth'])}%"
        )

def masters_graph(df: pd.DataFrame, year_range: tuple[int, int]) -> None:
    """Displays a line chart of master's graduates per year within the specified year range."""
    filtered_df = metrics_filtration_range(df, year_range)
    display = filtered_df.mean()
    display.index = display.index.astype(str)
    st.subheader('Number of masters graduates YoY')
    st.line_chart(display)

def students_per_10k_graph(
    students_df: pd.DataFrame,
    graduates_df: pd.DataFrame,
    year_range: tuple[int, int]
) -> None:
    """Creates a line plot with two series: students per 10k and graduates per 10k."""
    students_filtered = metrics_filtration_range(students_df, year_range)
    graduates_filtered = metrics_filtration_range(graduates_df, year_range)

    students_mean = students_filtered.mean()
    graduates_mean = graduates_filtered.mean()

    combined_df = pd.DataFrame({
        'Students per 10k citizens': students_mean,
        'Graduates per 10k citizens': graduates_mean
    })

    combined_df.index = combined_df.index.astype(str) 
    st.subheader('Comparison of Students and Graduates per 10k Citizens')
    st.line_chart(combined_df)

def bar_charts(
    stem_df: pd.DataFrame,
    foreigners_df: pd.DataFrame,
    year_range: tuple[int, int]
) -> None:
    """Displays bar charts for STEM students and foreigners as percentages in two columns."""
    stem_filtered = metrics_filtration_range(stem_df, year_range).mean()
    stem_filtered = stem_filtered.groupby(stem_filtered.index).mean()
    foreigners_filtered = metrics_filtration_range(foreigners_df, year_range).mean()
    stem_filtered.index = stem_filtered.index.astype(str)
    foreigners_filtered.index = foreigners_filtered.index.astype(str)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("STEM Students (%) YoY")
        st.bar_chart(stem_filtered)

    with col2:
        st.subheader("Foreigners (%) YoY")
        st.bar_chart(foreigners_filtered)

def plot_metrics_map(
    df: pd.DataFrame,
    geojson_path: str,
    year: int, 
    selected_metric: str
) -> None:
    """Creates choropleth map of Poland showing the metric per voivodeship."""
    aggregated_data = df.groupby('Nazwa').sum()
    aggregated_data = aggregated_data[
        [col for col in aggregated_data.columns if str(year) in col]
    ].reset_index()
    aggregated_data.columns = ['Voivodeship', selected_metric]
    aggregated_data['Voivodeship'] = aggregated_data['Voivodeship'].apply(str.title)
    aggregated_data['Voivodeship'] = aggregated_data['Voivodeship'].apply(unidecode)

    with open(geojson_path, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    fig = px.choropleth(
        aggregated_data,
        geojson=geojson_data,
        locations='Voivodeship',  
        featureidkey='properties.name', 
        color=selected_metric,
        color_continuous_scale='Blues',
        title=f'{selected_metric} per Voivodeship in {year}'
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    st.plotly_chart(fig)


def display_students_tab(
    selected_regions: list[str],
    year_range: tuple[int, int]
) -> None:
    """Displays data and visualizations for the 'Students' tab."""
    data_filtered = {
        'stem_data': filter_data(data['stem_data'], selected_regions),
        'students_per_10k': filter_data(data['students_per_10k'], selected_regions),
        'graduates_per_10k': filter_data(data['graduates_per_10k'], selected_regions),
        'masters_graduates': filter_data(data['masters_graduates'], selected_regions),
        'foreigners': filter_data(data['foreigners'], selected_regions), 
        'scholarships': filter_data(data['scholarships'], selected_regions), 
    }
    

    if data_filtered['stem_data'].shape[0] > 0:
        display_metrics(
            year_range[1], 
            data_filtered['stem_data'], 
            data_filtered['students_per_10k'], 
            data_filtered['graduates_per_10k'], 
            data_filtered['masters_graduates'], 
            data_filtered['foreigners'], 
            data_filtered['scholarships'] 
        )
        st.divider()
        masters_graph(data_filtered['masters_graduates'], year_range)
        students_per_10k_graph(data_filtered['students_per_10k'], data_filtered['graduates_per_10k'], year_range)
        bar_charts(data_filtered['stem_data'], data_filtered['foreigners'], year_range)

        st.divider()
        st.subheader('Geo visualization')
        selected_metric = st.selectbox('Select a metric to visualize:', list(METRICS_DROPDOWN.keys()))
        metric_key = METRICS_DROPDOWN[selected_metric]
    
        plot_metrics_map(
            data_filtered[metric_key], 
            'poland_geojson/polska-wojewodztwa.geojson', 
            year_range[1],
            selected_metric
        )