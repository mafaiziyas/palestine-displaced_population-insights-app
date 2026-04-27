import streamlit as st
import pandas as pd
import plotly.express as px

# Title of the app
st.title("Palestine Displacement Data Dashboard (1976-2025)")

# Loading csv data
url = "https://github.com/mafaiziyas/palestine-displaced_population-insights-app/raw/refs/heads/main/palestine_displacement_1976_2025.csv"
df = pd.read_csv(url)

# Sidebar filter for Year
year_list = sorted(df['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select a Year", year_list)
# Filter the data based on the selection
filtered_df = df[df['Year'] == selected_year]

#TOP METRICS
st.markdown(f"### Key Figures for {selected_year}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Refugees", f"{filtered_df['Refugees'].sum():,}")
col2.metric("Asylum Seekers", f"{filtered_df['Asylum seekers'].sum():,}")
col3.metric("Stateless Persons", f"{filtered_df['Stateless Persons'].sum():,}")
st.divider()

#Top 10 Countries of Asylum Bar chart
st.subheader(f"Top 10 Countries of Asylum in {selected_year}")
top_10 = filtered_df.nlargest(10, 'Refugees')
fig = px.bar(top_10, x='Country of Asylum Name', y='Refugees', color='Refugees')
st.plotly_chart(fig)

st.divider()


