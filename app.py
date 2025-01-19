import streamlit as st
from students import display_students_tab
from phd_students import display_phd_students_tab
from universities import display_universities_tab
from utils import CACHE_REGIONS

st.set_page_config(page_title="University Statistics in Poland", layout="wide")

@st.cache_data
def load_regions():
    return CACHE_REGIONS

st.logo('static/logo.png')

st.title("Higher education in Poland")
st.sidebar.markdown("""
     Powered by [GUS Local Data Bank](https://bdl.stat.gov.pl/bdl/start)  
""")
year_range = st.sidebar.slider(
    'Select Year Range',
    min_value=2003,
    max_value=2023,
    value=(2003, 2023),
    step=1
)
regions = load_regions()
selected_regions = st.sidebar.multiselect("Select voivodeships", regions, default=regions)

tab1, tab2, tab3 = st.tabs(["Students", "Doctoral Students", "Universities and Staff"])

with tab1:
    display_students_tab(selected_regions, year_range)

with tab2:
    display_phd_students_tab(selected_regions, year_range)

with tab3:
    display_universities_tab(selected_regions, year_range)
