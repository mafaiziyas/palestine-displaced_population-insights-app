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
#Additional functional requirement: download button
st.sidebar.divider()
st.sidebar.subheader("Export Data")
st.sidebar.download_button(
    label="📥 Download Year Data",
    data=filtered_df.to_csv(index=False),
    file_name=f"palestine_displacement_{selected_year}.csv",
    mime="text/csv",
)

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
    hover_data={
        "Country of Asylum Code": False, 
        "Refugees": ":,",               
        "Asylum seekers": ":,"          
    },
    #Green: make high values dark green and low values lighter/white
    color_continuous_scale="Greens", 
    projection="natural earth",
    title=f"Refugee Density ({selected_year})"
)
# Customizing the hover label for clarity
fig_map.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Refugees: %{z:,.0f}"
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
st.subheader("Search Specific Country Data")
search_country = st.selectbox("Select a country to view its specific records:", 
                             options=[""] + sorted(filtered_df['Country of Asylum Name'].unique().tolist()))

if search_country:
    country_data = filtered_df[filtered_df['Country of Asylum Name'] == search_country]
    st.write(f"In {selected_year}, **{search_country}** hosted:")
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Refugees:** {int(country_data['Refugees'].sum()):,}")
    c2.write(f"**Asylum Seekers:** {int(country_data['Asylum seekers'].sum()):,}")
    c3.write(f"**Others of Concern:** {int(country_data['Others of concern to UNHCR'].sum()):,}")
st.divider()

# Pie chart
st.subheader(f"Population Type Breakdown ({selected_year})")
pie_data = {
    'Category': ['Refugees', 'Asylum Seekers', 'Others of Concern'],
    'Count': [
        filtered_df['Refugees'].sum(),
        filtered_df['Asylum seekers'].sum(),
        filtered_df['Others of concern to UNHCR'].sum()
    ]
}
fig_pie = px.pie(
    pie_data, 
    values='Count', 
    names='Category', 
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.RdBu 
)
#Adding lables and % for clarity
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_pie, use_container_width=True)
st.divider()

st.caption("Data Source: UNHCR Population Statistics Database")

