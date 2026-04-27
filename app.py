import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UNHCR Palestine Dashboard", layout="wide")

# Custom CSS for UI Enhancement
st.markdown("""
    <style>
    /* Background and global font */
    .stApp {
        background-color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Card Styling for Metrics and Charts */
    div[data-testid="stMetric"], .stPlotlyChart {
        background-color: #1e293b !important; 
        padding: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* Metric text colors */
    [data-testid="stMetricValue"] { 
        color: #10b981 !important; 
        font-weight: 800 !important;
        font-size: 32px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* Sidebar adjustments */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper to sync Plotly colors with the UI cards
def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#f8fafc",
        margin=dict(l=15, r=15, t=50, b=15),
        title_font_color="#f8fafc",
        legend_font_color="#f8fafc"
    )
    fig.update_xaxes(gridcolor='#334155', zeroline=False)
    fig.update_yaxes(gridcolor='#334155', zeroline=False)
    return fig

st.title("Palestine Displacement Data Dashboard (1976-2025)")

url = "https://github.com/mafaiziyas/palestine-displaced_population-insights-app/raw/refs/heads/main/palestine_displacement_1976_2025.csv"
df = pd.read_csv(url)
df.columns = df.columns.str.strip()

year_list = sorted(df['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select a Year", year_list)
filtered_df = df[df['Year'] == selected_year]

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
                     mode='markers', name='Selected Year', marker=dict(color='#fbbf24', size=12))
fig_line.update_traces(line_color='#10b981')
st.plotly_chart(apply_theme(fig_line), use_container_width=True)
st.divider()

# Choropleth
st.subheader(f"Global Distribution of Refugees in {selected_year}")
fig_map = px.choropleth(
    filtered_df, 
    locations="Country of Asylum Code", 
    color="Refugees", 
    hover_name="Country of Asylum Name",
    color_continuous_scale="Viridis",
    projection="natural earth",
    title=f"Refugee Hotspots ({selected_year})"
)
st.plotly_chart(apply_theme(fig_map), use_container_width=True)
st.divider()

# Bar chart
st.subheader(f"Breakdown by Country ({selected_year})")
top_5_countries = filtered_df.nlargest(5, 'Refugees')
fig_grouped = px.bar(
    top_5_countries, 
    x='Country of Asylum Name', 
    y=['Refugees', 'Asylum seekers', 'Others of concern to UNHCR'],
    barmode='group',
    title="Top 5 Host Countries",
    color_discrete_sequence=["#10b981", "#3b82f6", "#94a3b8"]
)
st.plotly_chart(apply_theme(fig_grouped), use_container_width=True)
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
    pie_data, values='Count', names='Category', hole=0.4,
    color_discrete_sequence=["#064e3b", "#10b981", "#6ee7b7"]
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(apply_theme(fig_pie), use_container_width=True)
st.divider()

st.caption("Data Source: UNHCR Population Statistics Database")
