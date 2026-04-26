import streamlit as st
import pandas as pd
import plotly.express as px

# Title of the app
st.title("Palestine Displacement Data Dashboard (1976-2025)")

# Loading csv data
url = "https://raw.githubusercontent.com/mafaiziyas/mafaiziyas/palestine-displaced_population-insights-app/main/palestine_displacement_1976_2025.csv"
df = pd.read_csv(url)
