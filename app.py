import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration must be the first Streamlit command
st.set_page_config(page_title="UNHCR Palestine Dashboard", layout="wide")

# Global UI Customization: Contrast, Shadows, and Prominent Headings
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background-color: #f5f7f9;
    }
    
    /* Elevated Sidebar effect */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 2px 0px 10px rgba(0,0,0,0.05);
    }
    
    /* Prominent Heading Typography */
    h1 {
        color: #0e2133; 
        font-size: 42px !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
    }
    h2, h3 {
        color: #1a365d; 
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* Floating Metric Card Styling */
    [data-testid="stMetricValue"] { 
        font-size: 32px !important; 
        color: #1e4620 !important; 
        font-weight: 700 !important;
    }
    
    /* Label color fix for metrics */
    [data-testid="stMetricLabel"] {
        color: #334155 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    /* Neumorphic "Pop-out" effect for boxes */
    .stMetric {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Title of the app
st.title("Palestine Displacement Data Dashboard (1976-2025)")

# Collapsible Information Section
with st.expander("ℹ️ Data Methodology & Definitions"):
    st.write("""
    This dashboard visualizes trends for displaced populations originating from the State of Palestine.
    - **Refugees:** Individuals recognized under the UNHCR mandate.
    - **Asylum Seekers:** Individuals awaiting status determination.
    - **Others of Concern:** Groups requiring protection who don't fit strict refugee definitions.
    """)
    
# Loading csv data
url = "https://github.com/mafaiziyas/palestine-displaced_population-insights-app/raw/refs/heads/main/palestine_displacement_1976_2025.csv"
df = pd.read_csv(url)

# Sidebar filter for Year
year_list = sorted(df['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select a Year", year_list)
filtered_df = df[df['Year'] == selected_year]

# Additional functional requirement: download button
st.sidebar.divider()
st.sidebar.subheader("Export Data")
st.sidebar.download_button(
    label="📥 Download Year Data",
    data=filtered_df.to_csv(index=False),
    file_name=f"palestine_displacement_{selected_year}.csv",
    mime="text/csv",
)

# Top metrics
df.columns = df.columns.str.strip()
st.markdown(f"### Key Figures for {selected_year}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Refugees", f"{filtered_df['Refugees'].sum():,}")
col2.metric("Asylum Seekers", f"{filtered_df['Asylum seekers'].sum():,}")
col3.metric("Stateless Persons", f"{filtered_df['Stateless Persons'].sum():,}")
st.divider()

# Trend line 
st.subheader("Historical Displacement Trend (1976-2025)")
trend_data = df.groupby('Year')['Refugees'].sum().reset_index()
fig_line = px.line(trend_data, x='Year', y='Refugees', markers=True, title="Refugee Growth Over Time")
current_year_val = trend_data[trend_data['Year'] == selected_year]
fig_line.add_scatter(x=current_year_val['Year'], y=current_year_val['Refugees'], 
                     mode='markers', name='Selected Year', marker=dict(color='orange', size=12))

st.plotly_chart(fig_line, use_container_width=True)
st.divider()

# Choropleth
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
    color_continuous_scale="Greens", 
    projection="natural earth",
    title=f"Refugee Density ({selected_year})"
)
fig_map.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Refugees: %{z:,.0f}"
)
st.plotly_chart(fig_map, use_container_width=True)
st.divider()

# Bar chart
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

st.subheader("Search Specific Country Data")
search_country = st.selectbox("Select a country to view its specific records:", 
                             options=[""] + sorted(filtered_df['Country of Asylum Name'].unique().tolist()))

if search_country:
    country_data = filtered_df[filtered_df['Country of Asylum Name'] == search_country]
    # Blue Informational banner for result clarity
    st.info(f"Summary for **{search_country}** in {selected_year}")
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Refugees", f"{int(country_data['Refugees'].sum()):,}")
    sc2.metric("Asylum Seekers", f"{int(country_data['Asylum seekers'].sum()):,}")
    sc3.metric("Others of Concern", f"{int(country_data['Others of concern to UNHCR'].sum()):,}")
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
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_pie, use_container_width=True)
st.divider()

st.caption("Data Source: UNHCR Population Statistics Database")
