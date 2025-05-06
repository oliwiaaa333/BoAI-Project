import streamlit as st
import pandas as pd
import numpy as np
import pickle

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

latitude = st.number_input("Szerokość geograficzna (latitude)", value=39.0)
longitude = st.number_input("Długość geograficzna (longitude)", value=-98.0)

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
st.write(f"Znormalizowana przewidywana pensja: **{prediction_scaled:.4f}**")

salary_usd = prediction_scaled * (max_salary - min_salary) + min_salary
st.success(f"Przewidywane wynagrodzenie: ${salary_usd:,.2f}")