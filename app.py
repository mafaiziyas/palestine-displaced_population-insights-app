import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UNHCR Palestine Dashboard", layout="wide")

# Global UI Customization: Pale Grey Background & Floating Dark Graph Cards
st.markdown("""
    <style>
    /* Main Background: Pale Grey */
    .stApp {
        background-color: #e5e7eb;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 2px 0px 10px rgba(0,0,0,0.1);
    }
    
    /* Prominent Headings */
    h1 {
        color: #111827 !important; 
        font-size: 48px !important;
        font-weight: 800 !important;
    }
    h2, h3 {
        color: #1f2937 !important; 
        font-size: 28px !important;
    }

    /* Floating Metric & Graph Containers: Dark Grey Background with lifting shadow */
    [data-testid="stMetric"], .stPlotlyChart {
        background-color: #1f2937 !important; /* Dark Grey */
        padding: 20px !important;
        border-radius: 20px !important; /* Rounded corners */
        box-shadow: 0 10px 25px rgba(0,0,0,0.2) !important; /* Lifting shadow */
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* Metric text colors for dark background */
    [data-testid="stMetricValue"] { 
        font-size: 36px !important; 
        color: #4ade80 !important; /* Neon Green for visibility */
    }
    [data-testid="stMetricLabel"] {
        color: #f3f4f6 !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Title of the app
st.title("Palestine Displacement Data Dashboard (1976-2025)")

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

# Export Data Tool
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

# Plotly styling helper: Ensures graph text is visible against dark background
def style_graph(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#f3f4f6",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Trend line 
st.subheader("Historical Displacement Trend")
trend_data = df.groupby('Year')['Refugees'].sum().reset_index()
fig_line = px.line(trend_data, x='Year', y='Refugees', markers=True, title="Refugee Growth Over Time")
current_year_val = trend_data[trend_data['Year'] == selected_year]
fig_line.add_scatter(x=current_year_val['Year'], y=current_year_val['Refugees'], 
                     mode='markers', name='Selected Year', marker=dict(color='yellow', size=12))
st.plotly_chart(style_graph(fig_line), use_container_width=True)
st.divider()

# Choropleth
st.subheader(f"Global Distribution in {selected_year}")
fig_map = px.choropleth(
    filtered_df, 
    locations="Country of Asylum Code", 
    color="Refugees", 
    hover_name="Country of Asylum Name", 
    color_continuous_scale="Greens", 
    projection="natural earth"
)
st.plotly_chart(style_graph(fig_map), use_container_width=True)
st.divider()

# Bar chart
st.subheader(f"Top 5 Host Countries ({selected_year})")
top_5_countries = filtered_df.nlargest(5, 'Refugees')
fig_grouped = px.bar(
    top_5_countries, 
    x='Country of Asylum Name', 
    y=['Refugees', 'Asylum seekers', 'Others of concern to UNHCR'],
    barmode='group'
)
st.plotly_chart(style_graph(fig_grouped), use_container_width=True)
st.divider()

st.subheader("Search Specific Country Data")
search_country = st.selectbox("Select a country:", 
                             options=[""] + sorted(filtered_df['Country of Asylum Name'].unique().tolist()))

if search_country:
    country_data = filtered_df[filtered_df['Country of Asylum Name'] == search_country]
    st.info(f"Summary for **{search_country}** in {selected_year}")
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Refugees", f"{int(country_data['Refugees'].sum()):,}")
    sc2.metric("Asylum Seekers", f"{int(country_data['Asylum seekers'].sum()):,}")
    sc3.metric("Others of Concern", f"{int(country_data['Others of concern to UNHCR'].sum()):,}")
st.divider()

# Pie chart
st.subheader("Population Breakdown")
pie_data = {
    'Category': ['Refugees', 'Asylum Seekers', 'Others of Concern'],
    'Count': [filtered_df['Refugees'].sum(), filtered_df['Asylum seekers'].sum(), filtered_df['Others of concern to UNHCR'].sum()]
}
fig_pie = px.pie(pie_data, values='Count', names='Category', hole=0.4,
                 color_discrete_sequence=px.colors.sequential.Greens_r)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(style_graph(fig_pie), use_container_width=True)
st.divider()

st.caption("Data Source: UNHCR Population Statistics Database")
