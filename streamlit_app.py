import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="COVID-19 2020 Dashboard", layout="wide")

# --- Title ---
st.title("🦠 COVID-19 Global Dashboard — 2020 Snapshot")
st.markdown("""
This interactive dashboard explores the global spread of COVID-19 from **January to July 2020**. 
Use the sidebar to filter data and interact with visualizations.
""")

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("covid_19_clean_complete.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']
    return df

df = load_data()

# --- Sidebar Country Selector ---
st.sidebar.header("📍 Filters")
country = st.sidebar.selectbox("Choose a country to explore:", sorted(df['Country/Region'].unique()))

# Filtered country-specific data
country_df = df[df['Country/Region'] == country].sort_values('Date')

# --- Global Trend ---
st.subheader("📈 Global Case Trends")
global_df = df.groupby('Date')[['Confirmed', 'Deaths', 'Recovered']].sum().reset_index()
fig1 = px.line(global_df, x='Date', y=['Confirmed', 'Deaths', 'Recovered'], 
               title='🌍 Global COVID-19 Case Trends', labels={'value': 'Cases', 'variable': 'Type'})
fig1.update_layout(xaxis=dict(rangeslider_visible=True))
st.plotly_chart(fig1, use_container_width=True)

# --- Top 10 Countries Bar Chart ---
st.subheader("🏆 Top 10 Countries by Confirmed Cases")
latest = df[df['Date'] == df['Date'].max()]
top10 = latest.groupby('Country/Region')['Confirmed'].sum().sort_values(ascending=False).head(10).reset_index()
fig2 = px.bar(top10, x='Country/Region', y='Confirmed', text='Confirmed', color='Confirmed', 
              title='Top 10 Countries (as of latest date)', color_continuous_scale='Reds')
fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# --- Country Trend ---
st.subheader(f"📊 {country} COVID-19 Timeline")
fig3 = px.line(country_df, x='Date', y=['Confirmed', 'Deaths', 'Recovered'],
               title=f'{country} Case Progression', labels={'value': 'Cases', 'variable': 'Type'})
fig3.update_layout(xaxis=dict(rangeslider_visible=True))
st.plotly_chart(fig3, use_container_width=True)

# --- Global Active Case Animation ---
st.subheader("🌐 Animated Map: Global Active Cases Over Time")
# Prepare data
map_df = df.groupby(['Date', 'Country/Region'], as_index=False).agg({
    'Confirmed': 'sum',
    'Deaths': 'sum',
    'Recovered': 'sum',
    'Active': 'sum'
})

map_df['Active'] = map_df['Active'].clip(lower=0)


# Clip negative active values to 0

# Plot
fig4 = px.scatter_geo(
    map_df,
    locations="Country/Region",
    locationmode="country names",
    color="Active",
    size="Active",
    hover_name="Country/Region",
    animation_frame=map_df['Date'].dt.strftime('%Y-%m-%d'),
    projection="natural earth",
    color_continuous_scale="OrRd",
    title="🌍 Animated Spread of Active COVID-19 Cases (2020)",
    size_max=40
)

fig4.update_layout(geo=dict(showframe=False, showcoastlines=True), title_font_size=20)
st.plotly_chart(fig4, use_container_width=True)


# --- Footer ---
st.markdown("---")
st.markdown("Made  by Mila | Powered by Python, Streamlit & Plotly")
