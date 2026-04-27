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

#Top metrics
df.columns = df.columns.str.strip()
st.markdown(f"### Key Figures for {selected_year}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Refugees", f"{filtered_df['Refugees'].sum():,}")
col2.metric("Asylum Seekers", f"{filtered_df['Asylum seekers'].sum():,}")
col3.metric("Stateless Persons", f"{filtered_df['Stateless Persons'].sum():,}")
st.divider()

#Trend line 
st.subheader("Historical Displacement Trend (1976-2025)")
trend_data = df.groupby('Year')['Refugees'].sum().reset_index()
fig_line = px.line(trend_data, x='Year', y='Refugees', markers=True, title="Refugee Growth Over Time")
# Highlighting selected year with a yellow dot
current_year_val = trend_data[trend_data['Year'] == selected_year]
fig_line.add_scatter(x=current_year_val['Year'], y=current_year_val['Refugees'], 
                     mode='markers', name='Selected Year', marker=dict(color='yellow', size=12))

st.plotly_chart(fig_line, use_container_width=True)
st.divider()

#choropleth
st.subheader(f"Global Distribution of Refugees in {selected_year}")
fig_map = px.choropleth(
    filtered_df, 
    locations="Country of Asylum Code", 
    color="Refugees", 
    hover_name="Country of Asylum Name",
    color_continuous_scale="Reds",
    projection="natural earth",
    title=f"Worldwide Refugee Distribution ({selected_year})"
)
st.plotly_chart(fig_map, use_container_width=True)
st.divider()

#Bar chart
st.subheader(f"Breakdown of Population Types by Country ({selected_year})")
top_5_countries = filtered_df.nlargest(5, 'Refugees')
fig_grouped = px.bar(
    top_5_countries, 
    x='Country of Asylum Name', 
    y=['Refugees', 'Asylum seekers', 'Others of concern to UNHCR'],
    barmode='group',
    title="Comparison of Legal Statuses in Top Host Countries",
    labels={'value': 'Number of People', 'variable': 'Status'}
)
st.plotly_chart(fig_grouped, use_container_width=True)
st.divider()

#Pie chart
st.subheader(f"Population Type Breakdown ({selected_year})")
pie_data = {
    'Category': ['Refugees', 'Asylum Seekers', 'Stateless', 'IDPs'],
    'Count': [
        filtered_df['Refugees'].sum(),
        filtered_df['Asylum seekers'].sum(),
        filtered_df['Stateless Persons'].sum(),
        filtered_df['Internally displaced persons'].sum()
    ]
}
fig_pie = px.pie(pie_data, values='Count', names='Category', hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

st.caption("Data Source: UNHCR Population Statistics Database")

