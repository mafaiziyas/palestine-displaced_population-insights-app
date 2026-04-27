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

#Trend and Distribution
left_col, right_col = st.columns(2)

with left_col:
    # Historical Trend Line
    st.subheader("Displacement Trend (1976-2025)")
    trend_data = df.groupby('Year')['Refugees'].sum().reset_index()
    fig_line = px.line(trend_data, x='Year', y='Refugees', markers=True)
    # Highlighting the selected year on the line
    current_year_val = trend_data[trend_data['Year'] == selected_year]
    fig_line.add_scatter(x=current_year_val['Year'], y=current_year_val['Refugees'], 
                         mode='markers', name='Selected Year', marker=dict(color='yellow', size=12))
    st.plotly_chart(fig_line, use_container_width=True)

with right_col:
    # Population Breakdown Pie Chart
    st.subheader("Population Type Breakdown")
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


