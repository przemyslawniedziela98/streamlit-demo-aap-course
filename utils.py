import pandas as pd 


# ==== const ==== 
CACHE_REGIONS = [
    "Dolnośląskie", "Kujawsko-Pomorskie", "Lubelskie", "Lubuskie",
    "Łódzkie", "Małopolskie", "Mazowieckie", "Opolskie",
    "Podkarpackie", "Podlaskie", "Pomorskie", "Śląskie",
    "Świętokrzyskie", "Warmińsko-Mazurskie", "Wielkopolskie", "Zachodniopomorskie"
]

METRICS_DROPDOWN = {
        'Master’s Graduates': 'masters_graduates',
        'Students per 10k citizens': 'students_per_10k',
        'Graduates per 10k citizens': 'graduates_per_10k',
        'Foreigners (%)': 'foreigners'
}


# ==== utils ==== 
def filter_data(df: pd.DataFrame, regions: list[str]) -> pd.DataFrame:
    """Filters the DataFrame by selected regions."""
    return df[df['Nazwa'].str.lower().isin([region.lower() for region in regions])]


def metrics_filtration_year(df: pd.DataFrame, year: int) -> float:
    """Filters the DataFrame for a specific year and calculates the mean value."""
    return df[[col for col in df.columns if str(year) in col]].astype(float).values

def calculate_metrics(df: pd.DataFrame, year: int, mean: bool = True) -> dict[str, float]:
    """Calculates the average or sum value and growth percentage for the given year."""
    statistics = {}
    if mean: 
        current_year = metrics_filtration_year(df, year).mean()
        previous_year = metrics_filtration_year(df, year - 1).mean()
        statistics['average'] = current_year
    else: 
        current_year = metrics_filtration_year(df, year).sum()
        previous_year = metrics_filtration_year(df, year - 1).sum()
        statistics['sum'] = current_year
    statistics['growth'] = ((current_year - previous_year) / previous_year) * 100 if previous_year != 0 else 0

    return statistics

def metrics_filtration_range(df: pd.DataFrame, year_range: tuple[int, int]) -> pd.DataFrame:
    """Filters the DataFrame to include only columns within the specified year range."""
    df = df[[col for col in df.columns if ";20" in col]]
    df.columns = [2000 + int(col.split(";20")[1][:2]) for col in df.columns]
    return df[[col for col in df.columns if year_range[0] <= col <= year_range[1]]]

def filter_by_key(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Filters the dataset by key column names."""
    return df[[col for col in df.columns if key in col]]