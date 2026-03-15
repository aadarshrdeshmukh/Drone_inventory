import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# Page Config & Custom Styling
# ---------------------------------------------------

st.set_page_config(page_title="Drone Inventory Dashboard", layout="wide")

# Inject Custom CSS for Monochrome Aesthetics
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Ensure all text inherits black color */
    [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #000000 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #fcfcfc !important;
        border-right: 1px solid #000000;
    }
    
    /* Metric Styling - Categorized Colors */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 2px solid #000000;
        padding: 15px;
        border-radius: 8px;
        box-shadow: none;
    }
    
    /* Category-specific borders (No gradients) */
    [data-testid="column"]:nth-child(1) div[data-testid="stMetric"] { border-color: #10b981 !important; } /* Emerald */
    [data-testid="column"]:nth-child(2) div[data-testid="stMetric"] { border-color: #3b82f6 !important; } /* Blue */
    [data-testid="column"]:nth-child(3) div[data-testid="stMetric"] { border-color: #f59e0b !important; } /* Amber */
    
    div[data-testid="stMetricValue"] > div {
        font-size: 32px !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] > div > p {
        font-size: 13px !important;
        color: #000000 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        opacity: 1 !important;
    }

    /* Input & MultiSelect */
    [data-baseweb="tag"] {
        background-color: #000000 !important;
    }
    [data-baseweb="tag"] span {
        color: #ffffff !important;
    }
    [data-baseweb="tag"] svg {
        fill: #ffffff !important;
    }
    [data-baseweb="select"] div {
        color: #000000 !important;
    }
    
    /* Header & Navigation Fixes */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid #000000;
    }
    header[data-testid="stHeader"] svg {
        fill: #000000 !important;
    }
    header[data-testid="stHeader"] button {
        color: #000000 !important;
    }

    /* Better Sidebar Border & Horizontal Rules */
    [data-testid="stSidebar"] {
        border-right: 2px solid #000000 !important;
    }
    [data-testid="stSidebar"] hr {
        border-top: 1px solid #000000 !important;
        opacity: 1 !important;
        margin: 20px 0 !important;
    }
    /* Fixed Table Headers & Index Visibility */
    [data-testid="stDataFrame"] thead th, 
    [data-testid="stDataFrame"] tbody th,
    [data-testid="stDataFrame"] [data-testid="corner"],
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Force visibility of header text and make it bold */
    [data-testid="stDataFrame"] th span, 
    [data-testid="stDataFrame"] [role="columnheader"] div {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    
    /* Global Divider Styling */
    hr {
        border: none !important;
        border-top: 2px solid #000000 !important;
        color: #000000 !important;
        background-color: #000000 !important;
        height: 2px !important;
        opacity: 1 !important;
        margin: 40px 0 !important;
    }
    
    /* Remove any grey masks/overlays */
    [data-testid="stDataFrame"] {
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⛐ DRONE INVENTORY MANAGEMENT")
st.markdown("---")

# ---------------------------------------------------
# Plotly Standard Theme
# ---------------------------------------------------

COLOR_PALETTE = ['#000000', '#10b981', '#3b82f6', '#f59e0b', '#ef4444']

def update_fig_layout(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family="Inter", size=13, color="#000000"),
        title=dict(font=dict(size=18, color="#000000")),
        margin=dict(t=80, b=50, l=60, r=50),
        legend=dict(
            font=dict(color="#000000"),
            title=dict(font=dict(color="#000000")),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor="#000000",
            borderwidth=0,
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1
        )
    )
    fig.update_xaxes(
        showgrid=False, 
        linecolor="#000000", 
        zeroline=False,
        tickfont=dict(color="#000000", size=12),
        title_font=dict(color="#000000", size=14),
        showline=True,
        linewidth=1
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor="#eeeeee", 
        linecolor="#000000", 
        zeroline=False,
        tickfont=dict(color="#000000", size=12),
        title_font=dict(color="#000000", size=14),
        showline=True,
        linewidth=1
    )
    return fig

# ---------------------------------------------------
# INR Formatter
# ---------------------------------------------------

def format_inr(num):
    if num >= 10000000:
        return f"₹{num/10000000:.2f} Cr"
    elif num >= 100000:
        return f"₹{num/100000:.2f} L"
    else:
        return f"₹{num:,.0f}"

# ---------------------------------------------------
# Table Styler Helper
# ---------------------------------------------------

def apply_table_style(df):
    """
    Applies white background, black text, and bold/large headers to a dataframe.
    """
    return df.style.set_properties(**{
        'background-color': '#FFFFFF',
        'color': '#000000',
        'border-color': '#000000',
        'font-family': 'Inter'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#FFFFFF'), 
            ('color', '#000000'), 
            ('font-weight', '800'), 
            ('font-size', '16px'),
            ('text-transform', 'uppercase')
        ]},
        {'selector': 'td', 'props': [
            ('background-color', '#FFFFFF'), 
            ('color', '#000000')
        ]}
    ])

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------

@st.cache_data
def load_data():
    inventory = pd.read_csv("warehouse_inventory_data.csv")
    financial = pd.read_csv("financial_summary.csv")
    cashflow = pd.read_csv("cashflow_table.csv")
    maintenance = pd.read_csv("maintenance_cost_table.csv")
    return inventory, financial, cashflow, maintenance

inventory, financial, cashflow, maintenance = load_data()

# ---------------------------------------------------
# Calculations (Core Logic Preserved)
# ---------------------------------------------------

inventory["Inventory_Value"] = inventory["Quantity"] * inventory["Price"]
total_inventory_value = inventory["Inventory_Value"].sum()
error_inventory_value = inventory[inventory["Stock_Error"] == 1]["Inventory_Value"].sum()

# Parameters
original_labor_cost = 5000000
labor_reduction_percent = 60
stock_reduction_percent = 50
investment = 2500000
discount_rate = 0.10
project_life = 5
annual_maintenance_cost = 200000

labor_savings = original_labor_cost * (labor_reduction_percent / 100)
stock_savings = error_inventory_value * (stock_reduction_percent / 100)
total_savings = labor_savings + stock_savings
npv_amount = financial.loc[financial["Metric"] == "NPV", "Amount (₹)"].values[0]
net_benefit = total_savings - investment
roi = (net_benefit / investment) * 100

# ---------------------------------------------------
# Sidebar Filter
# ---------------------------------------------------

st.sidebar.markdown("### FILTERS")
rack_filter = st.sidebar.multiselect(
    "SELECT RACK",
    options=inventory["Rack"].unique(),
    default=inventory["Rack"].unique()
)

filtered_inventory = inventory[inventory["Rack"].isin(rack_filter)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**TOTAL PRODUCTS:** {len(filtered_inventory)}")
st.sidebar.markdown(f"**INVENTORY VALUE:** {format_inr(filtered_inventory['Inventory_Value'].sum())}")

# ---------------------------------------------------
# BUSINESS ANALYSIS
# ---------------------------------------------------

st.header("⬢ BUSINESS ANALYSIS")

with st.container():
    st.subheader("Labor and Stock Optimization")
    c1, c2, c3 = st.columns(3)
    c1.metric("Original Labor", format_inr(original_labor_cost))
    c2.metric("Labor Savings", format_inr(labor_savings))
    c3.metric("Stock Savings", format_inr(stock_savings))

    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Annual Savings", format_inr(total_savings))
    c2.metric("ROI (%)", f"{roi:.2f}%")
    c3.metric("Net Benefit", format_inr(net_benefit))

st.markdown("---")

# ---------------------------------------------------
# FINANCIAL ANALYSIS
# ---------------------------------------------------

st.header("⊘ FINANCIAL ANALYSIS")

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("Key NPV Metrics")
    st.metric("Net Present Value (NPV)", format_inr(npv_amount))
    st.markdown("**Parameters**")
    st.write(f"Discount Rate: {discount_rate*100}%")
    st.write(f"Project Life: {project_life} Years")
    st.write(f"Maintenance: {format_inr(annual_maintenance_cost)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Financial Summary Table")
    st.dataframe(apply_table_style(financial), width='stretch', hide_index=True)

with c2:
    st.subheader("5-Year Financial Projection")
    projection_df = pd.DataFrame({
        "Year": cashflow["Year"],
        "Cash Inflow": cashflow["Cash Inflow"],
        "Maintenance Cost": maintenance["Maintenance Cost"]
    })
    
    fig = px.line(
        projection_df,
        x="Year",
        y=["Cash Inflow", "Maintenance Cost"],
        markers=True,
        color_discrete_sequence=['#10b981', '#ef4444']
    )
    update_fig_layout(fig)
    st.plotly_chart(fig, width='stretch', theme=None)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Cashflow Table")
    st.dataframe(apply_table_style(cashflow), width='stretch', hide_index=True)
with col_b:
    st.subheader("Maintenance Log")
    st.dataframe(apply_table_style(maintenance), width='stretch', hide_index=True)

st.markdown("---")

st.markdown("---")

# ---------------------------------------------------
# DATA ANALYSIS
# ---------------------------------------------------

st.header("▥ INVENTORY DATA ANALYSIS")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Rack Distribution")
    rack_chart = px.bar(
        filtered_inventory.groupby("Rack").size().reset_index(name='Count'),
        x="Rack",
        y="Count",
        color_discrete_sequence=['#3b82f6']
    )
    update_fig_layout(rack_chart)
    st.plotly_chart(rack_chart, width='stretch', theme=None)

with col2:
    st.subheader("Inventory Value Heatmap")
    heatmap_data = filtered_inventory.groupby("Rack")["Inventory_Value"].sum().reset_index()
    fig_heat = px.bar(
        heatmap_data,
        x="Rack",
        y="Inventory_Value",
        color_discrete_sequence=['#10b981']
    )
    update_fig_layout(fig_heat)
    st.plotly_chart(fig_heat, width='stretch', theme=None)

st.subheader("Stock Error Distribution")
error_chart = px.histogram(
    filtered_inventory,
    x="Stock_Error",
    color_discrete_sequence=['#ef4444'],
    nbins=2
)
update_fig_layout(error_chart)
# Force categorical x-axis for errors
error_chart.update_xaxes(tickvals=[0, 1], ticktext=["No Error", "Error"])
st.plotly_chart(error_chart, width='stretch', theme=None)

st.markdown("---")

# ---------------------------------------------------
# RAW DATA VIEW
# ---------------------------------------------------

st.header("▦ DATA EXPLORER")
st.write("Full inventory granularity for filtered racks.")
st.dataframe(apply_table_style(filtered_inventory), width='stretch')