import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UNHCR Palestine Dashboard", layout="wide")

# Global UI Customization: Deeper Background & High-Contrast Text
st.markdown("""
    <style>
    /* Darker Background: Slate Grey for better contrast */
    .stApp {
        background-color: #cbd5e1;
    }
    
    /* Sidebar styling with depth */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 2px 0px 15px rgba(0,0,0,0.15);
    }
    
    /* High-Contrast Typography: Forcing all text to be very dark */
    h1, h2, h3, p, span, label {
        color: #0f172a !important; /* Deep Navy/Charcoal */
        font-family: 'Helvetica Neue', sans-serif;
    }

    h1 {
        font-size: 52px !important;
        font-weight: 900 !important;
    }

    /* Floating Graph Cards: Dark Charcoal with "Lifting" Shadow */
    [data-testid="stMetric"], .stPlotlyChart {
        background-color: #1e293b !important; 
        padding: 25px !important;
        border-radius: 24px !important; /* Extra rounded for modern feel */
        box-shadow: 0 20px 40px rgba(0,0,0,0.3) !important; /* Stronger lift effect */
        border: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Metric text colors: Neon for stats, White for labels */
    [data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        color: #22c55e !important; /* Bright Green */
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #f8fafc !important; /* Off-white for labels inside dark boxes */
        font-weight: 700 !important;
        font-size: 18px !important;
    }

    /* Sidebar text visibility fix */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p {
        color: #1e293b !important;
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

# Plotly styling helper
def style_graph(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#f8fafc", # Off-white for chart text against dark cards
        margin=dict(l=20, r=20, t=50, b=20),
        title_font_size=24,
        title_font_color="#f8fafc"
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    return fig

# Trend line 
st.subheader("Historical Displacement Trend")
trend_data = df.groupby('Year')['Refugees'].sum().reset_index()
fig_line = px.line(trend_data, x='Year', y='Refugees', markers=True, title="Refugee Growth Over Time")
current_year_val = trend_data[trend_data['Year'] == selected_year]
fig_line.add_scatter(x=current_year_val['Year'], y=current_year_val['Refugees'], 
                     mode='markers', name='Selected Year', marker=dict(color='#fbbf24', size=15))
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
