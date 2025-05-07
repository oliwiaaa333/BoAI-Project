import streamlit as st
import pandas as pd
import pickle
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

# załadowanie modelu
with open("xgb_model.pkl", "rb") as f:
    model = pickle.load(f)

# załadowanie kolumn
with open("xgb_columns.pkl", "rb") as f:
    model_columns = pickle.load(f)

st.title("Przewidywanie wynagrodzenia na podstawie oferty pracy")

# formularz
st.header("Wprowadź dane dotyczące oferty:")

work_type = st.selectbox("Rodzaj pracy", [
    'full_time', 'part_time', 'internship', 'temporary', 'volunteer', 'other'
])

experience_level = st.selectbox("Poziom doświadczenia", [
    'internship', 'entry', 'mid-senior', 'director', 'executive'
])

size = st.selectbox("Wielkość firmy", ['micro', 'small', 'medium', 'large'])

pay_period = st.selectbox("Okres płatności", [
    'hourly', 'weekly', 'biweekly', 'monthly', 'yearly'
])

category = st.selectbox("Branża", [
    'administration', 'education', 'finance', 'healthcare',
    'industry', 'it', 'law', 'services'
])

remote_flag = st.checkbox("Czy praca może być zdalna?", value=True)

location_input = st.text_input("Podaj lokalizację (np. Los Angeles, CA)")
geolocator = Nominatim(user_agent="job_salary_app")

latitude = 39.0
longitude = -98.0

if location_input:
    try:
        location = geolocator.geocode(location_input, country_codes="us")
        if location:
            latitude = location.latitude
            longitude = location.longitude
            st.success(f"Znaleziono lokalizację: {location.address}")
        else:
            st.warning("Nie znaleziono lokalizacji. Użyto domyślnych współrzędnych.")
    except (GeocoderUnavailable, GeocoderTimedOut):
        st.warning("Błąd łączeniz z usługą geokodowania. Użyto domyślnych współrzędnych")



input_dict = {
    'remote_flag': int(remote_flag),
    'latitude_minmax': (latitude - 24.5) / (49.4 - 24.5),
    'longitude_minmax': (longitude + 125) / (67 - (-125))  # znormalizowane USA
}

# one-hot encoding dla cech kategorycznych
for val in ['full_time', 'internship', 'other', 'part_time', 'temporary', 'volunteer']:
    input_dict[f'work_type_{val}'] = int(work_type == val)

for val in ['director', 'entry', 'executive', 'internship', 'mid-senior']:
    input_dict[f'experience_level_{val}'] = int(experience_level == val)

for val in ['large', 'medium', 'micro', 'small']:
    input_dict[f'size_{val}'] = int(size == val)

for val in ['biweekly', 'hourly', 'monthly', 'weekly', 'yearly']:
    input_dict[f'pay_period_{val}'] = int(pay_period == val)

for val in ['administration', 'education', 'finance', 'healthcare',
            'industry', 'it', 'law', 'services']:
    input_dict[f'category_{val}'] = int(category == val)

# konwersja do DataFrame
input_df = pd.DataFrame([input_dict])

# ustawienie odpowiedniej kolejności kolumn
input_df = input_df[model_columns]

# predykcja
prediction_scaled = model.predict(input_df)[0]

# wartości min, max salary - potrzebne do przeliczenia przewidywanej pensji na wartość w USD
min_salary = 0.0
max_salary = 234500.0

# wyswietlenie wyniku
st.subheader("Wynik modelu:")
# st.write(f"Znormalizowana przewidywana pensja: **{prediction_scaled:.4f}**")

salary_usd = prediction_scaled * (max_salary - min_salary) + min_salary
st.success(f"Przewidywane wynagrodzenie roczne: ${salary_usd:,.2f}")