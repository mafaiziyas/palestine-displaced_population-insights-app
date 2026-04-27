import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UNHCR Palestine Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #f1f5f9;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    
    h1, h2, h3, p, span, label {
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }

    h1 {
        font-size: 42px !important;
        font-weight: 800 !important;
        padding-bottom: 20px;
    }

    [data-testid="stMetric"], .stPlotlyChart {
        background-color: #1e293b !important; 
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    [data-testid="stMetricValue"] { 
        color: #4ade80 !important; 
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }

    .stDivider {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def style_graph(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#f8fafc",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    fig.update_xaxes(gridcolor='#334155', zeroline=False)
    fig.update_yaxes(gridcolor='#334155', zeroline=False)
    return fig

st.title("Palestine Displacement Data Dashboard (1976-2025)")

with st.expander("ℹ️ Data Methodology & Definitions"):
    st.write("""
    - **Refugees:** Individuals recognized under the UNHCR mandate.
    - **Asylum Seekers:** Individuals awaiting status determination.
    - **Others of Concern:** Groups requiring protection who don't fit strict refugee definitions.
    """)

url = "https://github.com/mafaiziyas/palestine-displaced_population-insights-app/raw/refs/heads/main/palestine_displacement_1976_2025.csv"
df = pd.read_csv(url)
df.columns = df.columns.str.strip()

year_list = sorted(df['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select a Year", year_list)
filtered_df = df[df['Year'] == selected_year]

st.sidebar.divider()
st.sidebar.subheader("Export Data")
st.sidebar.download_button(
    label="📥 Download Year Data",
    data=filtered_df.to_csv(index=False),
    file_name=f"palestine_displacement_{selected_year}.csv",
    mime="text/csv",
)

st.subheader(f"Key Figures for {selected_year}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Refugees", f"{filtered_df['Refugees'].sum():,}")
col2.metric("Asylum Seekers", f"{filtered_df['Asylum seekers'].sum():,}")
col3.metric("Stateless Persons", f"{filtered_df['Stateless Persons'].sum():,}")

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Historical Trend")
    trend_data = df.groupby('Year')['Refugees'].sum().reset_index()
    fig_line = px.line(trend_data, x='Year', y='Refugees', markers=True)
    fig_line.update_traces(line_color='#22c55e')
    st.plotly_chart(style_graph(fig_line), use_container_width=True)

with col_b:
    st.subheader("Population Breakdown")
    pie_values = [
        filtered_df['Refugees'].sum(), 
        filtered_df['Asylum seekers'].sum(), 
        filtered_df['Others of concern to UNHCR'].sum()
    ]
    pie_labels = ['Refugees', 'Asylum Seekers', 'Others of Concern']
    fig_pie = px.pie(values=pie_values, names=pie_labels, hole=0.4,
                     color_discrete_sequence=["#14532d", "#22c55e", "#86efac"])
    st.plotly_chart(style_graph(fig_pie), use_container_width=True)

st.divider()

st.subheader(f"Top 5 Host Countries ({selected_year})")
top_5 = filtered_df.nlargest(5, 'Refugees')
fig_bar = px.bar(
    top_5, 
    x='Country of Asylum Name', 
    y=['Refugees', 'Asylum seekers'],
    barmode='group',
    color_discrete_sequence=["#22c55e", "#94a3b8"]
)
st.plotly_chart(style_graph(fig_bar), use_container_width=True)

st.divider()

st.subheader("Search Specific Country Data")
search_country = st.selectbox("Select a country:", 
                             options=[""] + sorted(filtered_df['Country of Asylum Name'].unique().tolist()))

if search_country:
    c_data = filtered_df[filtered_df['Country of Asylum Name'] == search_country]
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Refugees", f"{int(c_data['Refugees'].sum()):,}")
    sc2.metric("Asylum Seekers", f"{int(c_data['Asylum seekers'].sum()):,}")
    sc3.metric("Others of Concern", f"{int(c_data['Others of concern to UNHCR'].sum()):,}")

st.caption("Data Source: UNHCR Population Statistics Database")
