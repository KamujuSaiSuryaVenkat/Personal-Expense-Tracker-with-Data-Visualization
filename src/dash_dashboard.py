"""
Plotly Dash Interactive Dashboard - Professional Version
Upgraded from Streamlit with enhanced interactivity and styling
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
import os
import sys
import base64
import io
from datetime import datetime

# Add src directory to path so source modules can be imported directly
sys.path.insert(0, os.path.dirname(__file__))

from budget_tracker import BudgetTracker
from recurring_detector import RecurringDetector
from anomaly_detector import AnomalyDetector
from forecasting import SpendingForecaster
from ml_categorizer import MLCategorizer

# ==================== DATA LOADING ====================
def load_data():
    """Load expense data from CSV or database."""
    try:
        # Try CSV first (most reliable)
        csv_path = "data/sample_expenses.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
    except Exception as e:
        print(f"CSV Error: {e}")
    
    try:
        # Try database
        db_path = "db/expenses.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM expenses", conn)
            conn.close()
            df['Date'] = pd.to_datetime(df['Date'])
            return df
    except Exception as e:
        print(f"Database Error: {e}")
    
    return None


def normalize_dataframe(frame):
    """Normalize a dataframe so the dashboard can safely render it."""
    if frame is None or frame.empty:
        return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'PaymentMethod', 'Category'])

    normalized = frame.copy()

    if 'Date' in normalized.columns:
        normalized['Date'] = pd.to_datetime(normalized['Date'], errors='coerce')
    else:
        normalized['Date'] = pd.NaT

    if 'Description' not in normalized.columns:
        normalized['Description'] = ''
    if 'Amount' not in normalized.columns:
        normalized['Amount'] = 0
    if 'PaymentMethod' not in normalized.columns:
        normalized['PaymentMethod'] = 'Unknown'
    if 'Category' not in normalized.columns:
        normalized['Category'] = 'Other'

    normalized = normalized.dropna(subset=['Date'])
    normalized['Amount'] = pd.to_numeric(normalized['Amount'], errors='coerce').fillna(0)
    normalized['Description'] = normalized['Description'].astype(str)
    normalized['PaymentMethod'] = normalized['PaymentMethod'].astype(str)
    normalized['Category'] = normalized['Category'].astype(str)
    return normalized


def dataframe_to_store(frame):
    """Serialize a dataframe for dcc.Store."""
    return frame.to_json(date_format='iso', orient='split')


def dataframe_from_store(data):
    """Deserialize a dataframe from dcc.Store."""
    if not data:
        return normalize_dataframe(df)
    try:
        restored = pd.read_json(io.StringIO(data), orient='split')
        return normalize_dataframe(restored)
    except Exception:
        return normalize_dataframe(df)


def apply_date_range(frame, start_date, end_date):
    """Filter a dataframe by an optional date range."""
    filtered = normalize_dataframe(frame)
    if start_date:
        filtered = filtered[filtered['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered['Date'] <= pd.to_datetime(end_date)]
    return filtered


def parse_uploaded_dataframe(contents, filename):
    """Parse an uploaded CSV or Excel file into a normalized dataframe."""
    if not contents:
        return None

    try:
        _, content_string = contents.split(',', 1)
        decoded = base64.b64decode(content_string)

        if filename and filename.lower().endswith(('.xls', '.xlsx')):
            uploaded = pd.read_excel(io.BytesIO(decoded))
        else:
            uploaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        return normalize_dataframe(uploaded)
    except Exception as exc:
        print(f"Upload Error: {exc}")
        return None


def build_upload_summary(frame, source_label):
    """Create a compact real-time summary for the uploaded dataset."""
    if frame is None or frame.empty:
        return html.Div("No dataset loaded yet.", style={'color': '#666'})

    min_date = frame['Date'].min().date()
    max_date = frame['Date'].max().date()
    return html.Div([
        html.P(f"Source: {source_label}", style={'margin': '0 0 6px 0', 'fontWeight': '600'}),
        html.P(f"Rows: {len(frame)}", style={'margin': '0 0 6px 0'}),
        html.P(f"Columns: {len(frame.columns)}", style={'margin': '0 0 6px 0'}),
        html.P(f"Date Range: {min_date} → {max_date}", style={'margin': '0'}),
    ], style={
        'padding': '12px',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '10px',
        'border': '1px solid #e5e7eb'
    })

# Load data
df = normalize_dataframe(load_data())

manual_budget_overrides = {}

if df is None or df.empty:
    print("❌ No data found! Please run `python main.py` first.")
    # Create empty dataframe for app to still run
    df = pd.DataFrame(columns=['Date', 'Description', 'Amount', 'PaymentMethod', 'Category'])

# Ensure required columns
if 'Category' not in df.columns:
    df['Category'] = 'Other'

initial_store_data = dataframe_to_store(df)
date_min = df['Date'].min().date() if not df.empty else datetime.today().date()
date_max = df['Date'].max().date() if not df.empty else datetime.today().date()

# ==================== PLOTLY COLORS ====================
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# ==================== INITIALIZE DASH APP ====================
app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
app.title = "💰 Expense Tracker - Advanced Dash"
app.config.suppress_callback_exceptions = True

# ==================== APP LAYOUT ====================
app.layout = html.Div([
    dcc.Store(id='data-store', data=initial_store_data),
    dcc.Store(id='budget-store', data={}),
    # Header hero
    html.Div([
        html.Div([
            html.H1("Finance Command Center", style={'margin': '0', 'fontSize': '42px', 'fontWeight': '800', 'color': '#111111'}),
            html.P("Advanced expense intelligence with forecasting, anomaly detection, and budget control.",
                   style={'margin': '14px 0 0 0', 'color': '#444444', 'fontSize': '16px', 'maxWidth': '760px'}),
            html.Div([
                html.Div([
                    html.P("Data Range", style={'margin': '0', 'color': '#555555', 'fontSize': '12px', 'letterSpacing': '1px', 'textTransform': 'uppercase'}),
                    html.H4(f"{df['Date'].min().date()} → {df['Date'].max().date()}", style={'margin': '8px 0 0 0', 'color': '#111111'})
                ], style={'marginRight': '36px'}),
                html.Div([
                    html.P("Categories", style={'margin': '0', 'color': '#555555', 'fontSize': '12px', 'letterSpacing': '1px', 'textTransform': 'uppercase'}),
                    html.H4(f"{df['Category'].nunique()}", style={'margin': '8px 0 0 0', 'color': '#111111'})
                ], style={'marginRight': '36px'}),
                html.Div([
                    html.P("Transactions", style={'margin': '0', 'color': '#555555', 'fontSize': '12px', 'letterSpacing': '1px', 'textTransform': 'uppercase'}),
                    html.H4(f"{len(df)}", style={'margin': '8px 0 0 0', 'color': '#111111'})
                ])
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '28px', 'marginTop': '28px'})
        ], style={'maxWidth': '860px'})
    ], style={
        'padding': '40px',
        'borderRadius': '28px',
        'backgroundImage': 'none',
        'backgroundColor': '#ffffff',
        'marginBottom': '28px',
        'boxShadow': '0 16px 40px rgba(0, 0, 0, 0.06)'
    }),
    
    # Main container
    html.Div([
        # Sidebar with navigation
        html.Div([
            html.H3("📑 Navigation", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#111111'}),
            dcc.Dropdown(
                id='page-selector',
                options=[
                    {'label': '📊 Overview', 'value': 'overview'},
                    {'label': '🔍 Analysis', 'value': 'analysis'},
                    {'label': '💳 Budget', 'value': 'budget'},
                    {'label': '🔄 Recurring', 'value': 'recurring'},
                    {'label': '🔮 Forecast', 'value': 'forecast'},
                    {'label': '⚠️ Anomalies', 'value': 'anomaly'},
                    {'label': '📅 Transactions', 'value': 'transactions'}
                ],
                value='overview',
                style={'width': '100%', 'color': '#111111'}
            ),
            html.Div([
                html.Label("Date Range", style={'display': 'block', 'margin': '18px 0 8px', 'fontWeight': '600'}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    min_date_allowed=date_min,
                    max_date_allowed=date_max,
                    start_date=date_min,
                    end_date=date_max,
                    display_format='YYYY-MM-DD',
                    style={'width': '100%'}
                )
            ]),
            html.Div([
                html.Label("Upload Dataset", style={'display': 'block', 'margin': '18px 0 8px', 'fontWeight': '600'}),
                dcc.Upload(
                    id='dataset-upload',
                    children=html.Div(['Drag and drop or ', html.A('select a CSV/XLSX file')]),
                    style={
                        'width': '100%',
                        'padding': '14px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '12px',
                        'textAlign': 'center',
                        'backgroundColor': '#f8f9fa',
                        'cursor': 'pointer'
                    },
                    multiple=False
                ),
                html.Div(id='upload-status', style={'marginTop': '12px'})
            ])
        ], style={
            'width': '22%',
            'padding': '28px',
            'backgroundColor': '#ffffff',
            'borderRadius': '32px',
            'boxShadow': '0 16px 40px rgba(0, 0, 0, 0.06)',
            'minHeight': 'calc(100vh - 92px)',
            'boxSizing': 'border-box',
            'color': '#111111'
        }),
        
        # Main content
        html.Div(id='page-content', style={
            'width': '78%',
            'paddingLeft': '28px',
            'boxSizing': 'border-box',
            'color': '#111111'
        })
    ], style={'display': 'flex', 'gap': '26px', 'alignItems': 'flex-start'})
], style={'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#ffffff', 'color': '#111111', 'padding': '18px 24px 34px'})

# ==================== PAGE CALLBACKS ====================
@callback(
    Output('data-store', 'data'),
    Output('upload-status', 'children'),
    Output('date-range-picker', 'min_date_allowed'),
    Output('date-range-picker', 'max_date_allowed'),
    Output('date-range-picker', 'start_date'),
    Output('date-range-picker', 'end_date'),
    Input('dataset-upload', 'contents'),
    State('dataset-upload', 'filename')
)
def update_uploaded_dataset(contents, filename):
    """Update the stored dataset and upload summary when the user uploads a file."""
    uploaded_df = parse_uploaded_dataframe(contents, filename) if contents else df.copy()
    if uploaded_df is None or uploaded_df.empty:
        uploaded_df = df.copy()

    summary = build_upload_summary(uploaded_df, filename or 'Built-in dataset')
    min_date = uploaded_df['Date'].min().date() if not uploaded_df.empty else datetime.today().date()
    max_date = uploaded_df['Date'].max().date() if not uploaded_df.empty else datetime.today().date()
    return dataframe_to_store(uploaded_df), summary, min_date, max_date, min_date, max_date


@callback(
    Output('page-content', 'children'),
    Input('page-selector', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('data-store', 'data'),
    Input('budget-store', 'data')
)
def display_page(selected_page, start_date, end_date, data_store, budget_store):
    """Render selected page content."""
    global df, manual_budget_overrides
    manual_budget_overrides = budget_store or {}
    df = apply_date_range(dataframe_from_store(data_store), start_date, end_date)
    
    if df.empty:
        return html.Div([
            html.Div([
                html.H2("❌ No data found!", style={'color': '#d62728'}),
                html.P("Please run `python main.py` first to generate data."),
                html.Code("cd d:\\IIT DELHI\\Projects\\Python\\Project-1", 
                         style={'display': 'block', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'marginTop': '10px'})
            ], style={'padding': '20px', 'textAlign': 'center'})
        ])
    
    if selected_page == 'overview':
        return create_overview_page()
    elif selected_page == 'analysis':
        return create_analysis_page()
    elif selected_page == 'budget':
        return create_budget_page()
    elif selected_page == 'recurring':
        return create_recurring_page()
    elif selected_page == 'forecast':
        return create_forecast_page()
    elif selected_page == 'anomaly':
        return create_anomaly_page()
    elif selected_page == 'transactions':
        return create_transactions_page()
    else:
        return create_overview_page()


@callback(
    Output('budget-store', 'data'),
    Output('budget-status', 'children'),
    Input('save-budget-button', 'n_clicks'),
    State('budget-category-input', 'value'),
    State('budget-amount-input', 'value'),
    State('budget-store', 'data')
)
def save_manual_budget(n_clicks, category, amount, budget_store):
    """Save a manually entered budget amount."""
    current_store = budget_store or {}
    if not n_clicks:
        return current_store, ""

    if not category or amount is None:
        return current_store, html.Div("Select a category and enter a budget amount.", style={'color': '#d62728'})

    updated_store = dict(current_store)
    updated_store[category] = float(amount)
    global manual_budget_overrides
    manual_budget_overrides = updated_store
    return updated_store, html.Div(f"Saved budget for {category}: ₹{float(amount):,.0f}", style={'color': '#2ca02c', 'fontWeight': '600'})

# ==================== PAGE: OVERVIEW ====================
def create_overview_page():
    """Create Overview page with key metrics and charts."""
    total_spent = df['Amount'].sum()
    avg_transaction = df['Amount'].mean()
    max_transaction = df['Amount'].max()
    total_transactions = len(df)
    
    # Category breakdown
    category_totals = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    
    # Monthly trend
    monthly = df.set_index('Date').resample('ME')['Amount'].sum()
    
    top_category = category_totals.index[0] if len(category_totals) > 0 else 'N/A'
    highest_category_value = category_totals.max() if not category_totals.empty else 0
    avg_daily = df.groupby(df['Date'].dt.date)['Amount'].sum().mean() if not df.empty else 0

    return html.Div([
        html.H2("📊 Overview"),
        html.P("High-level spending intelligence with performance indicators, category concentration, and trend visibility.",
    style={'color': '#444444', 'marginBottom': '24px', 'fontSize': '15px'}),
        
        html.Div([
            create_metric_card("Total Spent", f"₹{total_spent:,.0f}", COLORS['primary']),
            create_metric_card("Avg Transaction", f"₹{avg_transaction:,.0f}", COLORS['success']),
            create_metric_card("Top Category", f"{top_category}", COLORS['warning']),
            create_metric_card("Daily Avg", f"₹{avg_daily:,.0f}", COLORS['info'])
        ], style={
            'display': 'flex',
            'gap': '24px',
            'marginBottom': '32px',
            'flexWrap': 'wrap'
        }),
        
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=create_category_bar_chart(category_totals),
                    style={'height': '420px'}
                )
            ], style={'width': '58%', 'display': 'inline-block', 'marginRight': '2%', 'boxSizing': 'border-box'}),
            
            html.Div([
                dcc.Graph(
                    figure=create_category_pie_chart(category_totals),
                    style={'height': '420px'}
                )
            ], style={'width': '40%', 'display': 'inline-block', 'boxSizing': 'border-box'})
        ], style={'marginBottom': '28px', 'borderRadius': '22px', 'backgroundColor': '#ffffff', 'padding': '18px', 'boxShadow': '0 20px 50px rgba(0, 0, 0, 0.06)'}),
        
        html.Div([
            dcc.Graph(
                figure=create_monthly_trend_chart(monthly),
                style={'height': '400px'}
            )
        ])
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })

def create_metric_card(title, value, color):
    """Create a metric card."""
    return html.Div([
        html.P(title, style={'margin': '0', 'color': '#555555', 'fontSize': '12px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
        html.H3(value, style={'margin': '10px 0 0 0', 'color': '#111111', 'fontSize': '30px', 'fontWeight': '700'})
    ], className='metric-card', style={
        'flex': '1',
        'minWidth': '240px',
        'padding': '24px',
        'backgroundColor': '#ffffff',
        'borderRadius': '22px',
        'boxShadow': '0 20px 35px rgba(0, 0, 0, 0.06)',
        'border': '1px solid rgba(0, 0, 0, 0.06)'
    })

# ==================== PAGE: ANALYSIS ====================
def create_analysis_page():
    """Create Analysis page with detailed charts."""
    payment_totals = df.groupby('PaymentMethod')['Amount'].sum().sort_values(ascending=False)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    day_totals = df.groupby('DayOfWeek')['Amount'].mean()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_totals = day_totals.reindex(day_order)
    
    top_10 = df.nlargest(10, 'Amount')[['Date', 'Description', 'Amount', 'PaymentMethod']]
    
    stats = {
        'Median': f"₹{df['Amount'].median():,.0f}",
        'Std Dev': f"₹{df['Amount'].std():,.0f}",
        'Min': f"₹{df['Amount'].min():,.0f}",
        'Max': f"₹{df['Amount'].max():,.0f}"
    }
    
    return html.Div([
        html.H2("🔍 Detailed Analysis"),
        
        # Charts row 1
        html.Div([
            html.Div([
                dcc.Graph(figure=create_payment_bar_chart(payment_totals), style={'height': '400px'})
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'boxSizing': 'border-box'}),
            
            html.Div([
                dcc.Graph(figure=create_day_of_week_chart(day_totals), style={'height': '400px'})
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'boxSizing': 'border-box'})
        ], style={'marginBottom': '30px'}),
        
        # Top 10 transactions
        html.H3("🏆 Top 10 Transactions"),
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Date", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th("Description", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th("Amount", style={'padding': '10px', 'textAlign': 'right', 'borderBottom': '2px solid #ddd'}),
                    html.Th("Payment", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'})
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(row['Date'].strftime('%Y-%m-%d'), style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                    html.Td(row['Description'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                    html.Td(f"₹{row['Amount']:,.0f}", style={'padding': '10px', 'textAlign': 'right', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold'}),
                    html.Td(row['PaymentMethod'], style={'padding': '10px', 'borderBottom': '1px solid #eee'})
                ]) for _, row in top_10.iterrows()
            ])
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '20px'}),
        
        # Statistics
        html.H3("📊 Statistics"),
        html.Div([
            create_metric_card(key, value, COLORS['info']) for key, value in stats.items()
        ], style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'})
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })

# ==================== PAGE: BUDGET ====================
def create_budget_page():
    """Create Budget management page."""
    default_budgets = {
        'Food & Dining': 10000,
        'Transportation': 8000,
        'Utilities': 5000,
        'Health & Medical': 3000,
        'Entertainment': 5000,
        'Shopping': 15000,
        'Education': 2000,
        'Personal Care': 1000,
        'Subscriptions': 2000,
        'Other': 5000
    }
    
    categories = sorted(df['Category'].unique())
    spending = df.groupby('Category')['Amount'].sum()
    effective_budgets = {**default_budgets, **manual_budget_overrides}
    
    budget_rows = []
    for category in categories:
        budget = effective_budgets.get(category, 5000)
        spent = spending.get(category, 0)
        percentage = (spent / budget * 100) if budget > 0 else 0
        
        if percentage >= 100:
            status_color = COLORS['danger']
            status_text = f"❌ OVER: {percentage:.0f}%"
        elif percentage >= 80:
            status_color = COLORS['warning']
            status_text = f"⚠️ {percentage:.0f}%"
        else:
            status_color = COLORS['success']
            status_text = f"✓ {percentage:.0f}%"
        
        budget_rows.append(
            html.Tr([
                html.Td(category, style={'padding': '12px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold'}),
                html.Td(f"₹{spent:,.0f}", style={'padding': '12px', 'borderBottom': '1px solid #eee', 'textAlign': 'right'}),
                html.Td(f"₹{budget:,.0f}", style={'padding': '12px', 'borderBottom': '1px solid #eee', 'textAlign': 'right'}),
                html.Td(html.Div(
                    style={
                        'width': '100%',
                        'height': '20px',
                        'backgroundColor': '#e9ecef',
                        'borderRadius': '10px',
                        'overflow': 'hidden',
                        'position': 'relative'
                    },
                    children=[
                        html.Div(
                            style={
                                'height': '100%',
                                'width': f'{min(percentage, 100)}%',
                                'backgroundColor': status_color,
                                'transition': 'width 0.3s ease'
                            }
                        )
                    ]
                ), style={'padding': '12px', 'borderBottom': '1px solid #eee'}),
                html.Td(status_text, style={'padding': '12px', 'borderBottom': '1px solid #eee', 'color': status_color, 'fontWeight': 'bold'})
            ])
        )
    
    return html.Div([
        html.H2("💳 Budget Management"),
        html.Div([
            html.Div([
                html.Label("Category", style={'fontWeight': 'bold', 'marginBottom': '6px', 'display': 'block'}),
                dcc.Dropdown(
                    id='budget-category-input',
                    options=[{'label': category, 'value': category} for category in categories],
                    value=categories[0] if categories else None,
                    placeholder='Select a category'
                )
            ], style={'width': '38%', 'display': 'inline-block', 'marginRight': '2%', 'boxSizing': 'border-box'}),
            html.Div([
                html.Label("Budget Amount (₹)", style={'fontWeight': 'bold', 'marginBottom': '6px', 'display': 'block'}),
                dcc.Input(
                    id='budget-amount-input',
                    type='number',
                    min=0,
                    step=100,
                    placeholder='Enter budget amount',
                    style={'width': '100%', 'padding': '10px', 'border': '1px solid #ccc', 'borderRadius': '6px'}
                )
            ], style={'width': '38%', 'display': 'inline-block', 'marginRight': '2%', 'boxSizing': 'border-box'}),
            html.Div([
                html.Button('Save Budget', id='save-budget-button', style={
                    'padding': '12px 18px',
                    'backgroundColor': COLORS['primary'],
                    'color': '#ffffff',
                    'border': 'none',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'width': '100%'
                }),
                html.Div(id='budget-status', style={'marginTop': '10px'})
            ], style={'width': '20%', 'display': 'inline-block', 'boxSizing': 'border-box', 'verticalAlign': 'bottom'})
        ], style={'marginBottom': '24px', 'padding': '18px', 'backgroundColor': '#f8f9fa', 'borderRadius': '12px', 'border': '1px solid #e5e7eb'}),
        html.H3("Monthly Budget Status"),
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Category", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Spent", style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Budget", style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Progress", style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Status", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'})
                ])
            ),
            html.Tbody(budget_rows)
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '20px'})
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })

# ==================== PAGE: RECURRING ====================
def create_recurring_page():
    """Create Recurring expenses page."""
    desc_counts = df['Description'].value_counts()
    recurring = desc_counts[desc_counts >= 2]
    
    if len(recurring) == 0:
        return html.Div([
            html.H2("🔄 Recurring Expenses"),
            html.Div([
                html.P("ℹ️ No recurring transactions found", style={'fontSize': '16px', 'color': '#666'})
            ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '4px'})
        ], style={
            'padding': '20px',
            'backgroundColor': '#ffffff',
            'borderRadius': '20px',
            'boxShadow': '0 20px 40px rgba(0, 0, 0, 0.06)',
            'color': '#111111'
        })
    
    recurring_rows = []
    for description, count in recurring.items():
        transactions = df[df['Description'] == description]
        avg_amount = transactions['Amount'].mean()
        dates = transactions['Date'].sort_values()
        
        if len(dates) > 1:
            gap_days = (dates.iloc[-1] - dates.iloc[0]).days / (len(dates) - 1)
            frequency = determine_frequency(gap_days)
        else:
            frequency = "Unknown"
        
        recurring_rows.append(
            html.Tr([
                html.Td(description, style={'padding': '12px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold'}),
                html.Td(f"{count}x", style={'padding': '12px', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
                html.Td(f"₹{avg_amount:,.0f}", style={'padding': '12px', 'borderBottom': '1px solid #eee', 'textAlign': 'right'}),
                html.Td(frequency, style={'padding': '12px', 'borderBottom': '1px solid #eee', 'textAlign': 'center'})
            ])
        )
    
    return html.Div([
        html.H2("🔄 Recurring Expenses"),
        html.P(f"Found {len(recurring)} recurring transactions:", style={'fontSize': '14px', 'color': '#444444', 'marginBottom': '20px'}),
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Description", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Count", style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Avg Amount", style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Frequency", style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'})
                ])
            ),
            html.Tbody(recurring_rows)
        ], style={'width': '100%', 'borderCollapse': 'collapse'})
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })

def create_forecast_page():
    """Create Forecast page for future spending insights."""
    forecaster = SpendingForecaster(df)
    forecast_df = forecaster.forecast_monthly_spending(months_ahead=6)
    trends = forecaster.detect_spending_trends()

    actual_monthly = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum()
    actual_x = actual_monthly.index.astype(str).tolist()
    actual_y = actual_monthly.values.tolist()

    forecast_x = forecast_df['Month'].astype(str).tolist()
    forecast_y = forecast_df['Forecasted Amount'].tolist()
    total_forecast = sum(forecast_y)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual_x,
        y=actual_y,
        mode='lines+markers',
        name='Historical',
        line={'color': COLORS['primary'], 'width': 3},
        marker={'size': 8}
    ))
    fig.add_trace(go.Scatter(
        x=forecast_x,
        y=forecast_y,
        mode='lines+markers',
        name='Forecast',
        line={'dash': 'dash', 'color': COLORS['warning'], 'width': 3},
        marker={'size': 8}
    ))
    fig.update_layout(
        title='🔮 Spending Forecast (Next 6 Months)',
        xaxis_title='Month',
        yaxis_title='Amount (₹)',
        height=450,
        hovermode='x unified',
        template='plotly_white'
    )

    return html.Div([
        html.H2("🔮 Spending Forecast"),
        html.Div([create_metric_card("Forecast Horizon", "6 months", COLORS['info']),
                  create_metric_card("Projected Spend", f"₹{total_forecast:,.0f}", COLORS['warning']),
                  create_metric_card("Trend", f"{trends.get('Direction', 'Unknown')}", COLORS['primary']),
                  create_metric_card("Forecast Confidence", f"{trends.get('R-squared', 0):.2f}", COLORS['success'])],
                 style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap', 'marginBottom': '30px'}),
        html.Div([dcc.Graph(figure=fig, style={'height': '500px'})]),
        html.Div([
            html.H3("📈 Trend Summary"),
            html.Ul([
                html.Li(f"Overall direction: {trends.get('Direction', 'Unknown')}", style={'marginBottom': '8px'}),
                html.Li(f"Monthly change estimate: ₹{trends.get('Monthly Change', 0):.2f}", style={'marginBottom': '8px'}),
                html.Li(f"Model score: {trends.get('R-squared', 0):.2%}", style={'marginBottom': '8px'})
            ])
        ], style={'marginTop': '20px'})
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })


def create_anomaly_page():
    """Create Anomaly page highlighting unusual spending."""
    detector = AnomalyDetector(df)
    outliers = detector.detect_outliers(method='iqr')
    patterns = detector.detect_unusual_patterns()
    surges = detector.detect_spending_surge(threshold_increase=50)

    outlier_rows = []
    for _, row in outliers.iterrows():
        severity = detector._calculate_severity(row['Amount'], df['Amount'].values)
        outlier_rows.append(html.Tr([
            html.Td(row['Date'].strftime('%Y-%m-%d'), style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
            html.Td(row['Description'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
            html.Td(f"₹{row['Amount']:,.0f}", style={'padding': '10px', 'borderBottom': '1px solid #eee', 'textAlign': 'right'}),
            html.Td(row['Category'], style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
            html.Td(severity, style={'padding': '10px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold'})
        ]))

    return html.Div([
        html.H2("⚠️ Anomaly Detection"),
        html.Div([create_metric_card("Detected Outliers", str(len(outlier_rows)), COLORS['danger']),
                  create_metric_card("Pattern Alerts", str(len(patterns)), COLORS['warning']),
                  create_metric_card("Spending Surges", str(len(surges)), COLORS['primary'])],
                 style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap', 'marginBottom': '30px'}),
        html.Div([
            html.H3("Outlier Transactions"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Date", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Description", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Amount", style={'padding': '12px', 'textAlign': 'right', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Category", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Th("Severity", style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'})
                ])),
                html.Tbody(outlier_rows)
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '30px'})
        ]) if outlier_rows else html.Div([html.P("No significant outliers detected.", style={'color': '#666'})]),
        html.Div([
            html.H3("Anomaly Patterns"),
            html.Ul([html.Li(pattern) for pattern in patterns]) if patterns else html.P("No unusual patterns detected.", style={'color': '#666'})
        ], style={'marginBottom': '32px'}),
        html.Div([
            html.H3("Spending Surges"),
            html.Ul([html.Li(f"{surge['Month']}: ₹{surge['Increase']:.1f}% increase") for surge in surges]) if surges else html.P("No spending surges detected.", style={'color': '#666'})
        ], style={'marginBottom': '12px'})
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })


def determine_frequency(gap_days):
    """Determine frequency from gap days."""
    if gap_days < 1.5:
        return "Daily"
    elif gap_days < 7:
        return "Weekly"
    elif gap_days < 15:
        return "Bi-weekly"
    elif gap_days < 45:
        return "Monthly"
    elif gap_days < 120:
        return "Quarterly"
    else:
        return "Annually"

# ==================== PAGE: TRANSACTIONS ====================
def create_transactions_page():
    """Create Transactions page with filters."""
    return html.Div([
        html.H2("📅 Transactions"),
        
        # Filters
        html.Div([
            html.Div([
                html.Label("Categories:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='category-filter',
                    options=[{'label': 'All', 'value': 'all'}] + [{'label': cat, 'value': cat} for cat in df['Category'].unique()],
                    value='all',
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%', 'boxSizing': 'border-box'}),
            
            html.Div([
                html.Label("Payment Methods:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='payment-filter',
                    options=[{'label': 'All', 'value': 'all'}] + [{'label': pm, 'value': pm} for pm in df['PaymentMethod'].unique()],
                    value='all',
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%', 'boxSizing': 'border-box'}),
            
            html.Div([
                html.Label(f"Amount Range: ₹{int(df['Amount'].min())} - ₹{int(df['Amount'].max())}", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.RangeSlider(
                    id='amount-slider',
                    min=int(df['Amount'].min()),
                    max=int(df['Amount'].max()),
                    value=[int(df['Amount'].min()), int(df['Amount'].max())],
                    marks={int(df['Amount'].min()): f"₹{int(df['Amount'].min())}", 
                           int(df['Amount'].max()): f"₹{int(df['Amount'].max())}"},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'boxSizing': 'border-box'})
        ], style={'marginBottom': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '4px'}),
        
        # Results
        html.Div(id='transactions-output', children=[
            create_transactions_table(df)
        ]),
        
        # Download button
        html.Div([
            html.A(
                html.Button('📥 Download CSV', style={
                    'padding': '10px 20px',
                    'backgroundColor': COLORS['success'],
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer',
                    'fontSize': '14px',
                    'fontWeight': 'bold'
                }),
                href=f"data:text/csv;charset=utf8,{df.to_csv(index=False)}",
                download=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"
            )
        ], style={'marginTop': '20px'})
    ], style={
        'padding': '28px',
        'backgroundColor': '#ffffff',
        'borderRadius': '28px',
        'boxShadow': '0 30px 80px rgba(0, 0, 0, 0.06)',
        'color': '#111111'
    })

def create_transactions_table(data):
    """Create transactions table."""
    if data.empty:
        return html.P("No transactions found")
    
    display_df = data[['Date', 'Description', 'Amount', 'PaymentMethod', 'Category']].sort_values('Date', ascending=False)
    
    rows = []
    for _, row in display_df.iterrows():
        rows.append(
            html.Tr([
                html.Td(row['Date'].strftime('%Y-%m-%d'), style={'padding': '10px', 'borderBottom': '1px solid #eee', 'fontSize': '13px'}),
                html.Td(row['Description'], style={'padding': '10px', 'borderBottom': '1px solid #eee', 'fontSize': '13px'}),
                html.Td(f"₹{row['Amount']:,.0f}", style={'padding': '10px', 'borderBottom': '1px solid #eee', 'textAlign': 'right', 'fontWeight': 'bold', 'fontSize': '13px'}),
                html.Td(row['PaymentMethod'], style={'padding': '10px', 'borderBottom': '1px solid #eee', 'fontSize': '13px'}),
                html.Td(row['Category'], style={'padding': '10px', 'borderBottom': '1px solid #eee', 'fontSize': '13px'})
            ])
        )
    
    return html.Table([
        html.Thead(
            html.Tr([
                html.Th("Date", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa', 'fontSize': '13px', 'fontWeight': 'bold'}),
                html.Th("Description", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa', 'fontSize': '13px', 'fontWeight': 'bold'}),
                html.Th("Amount", style={'padding': '10px', 'textAlign': 'right', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa', 'fontSize': '13px', 'fontWeight': 'bold'}),
                html.Th("Payment", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa', 'fontSize': '13px', 'fontWeight': 'bold'}),
                html.Th("Category", style={'padding': '10px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa', 'fontSize': '13px', 'fontWeight': 'bold'})
            ])
        ),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': '#ffffff', 'color': '#111111'})

# ==================== CHART FUNCTIONS ====================
def create_category_bar_chart(category_totals):
    """Create category bar chart."""
    fig = go.Figure(data=[
        go.Bar(
            y=category_totals.index,
            x=category_totals.values,
            orientation='h',
            marker={'color': COLORS['primary']},
            text=[f"₹{x:,.0f}" for x in category_totals.values],
            textposition='auto'
        )
    ])
    fig.update_layout(
        title="💳 Spending by Category",
        xaxis_title="Amount (₹)",
        yaxis_title="Category",
        height=400,
        showlegend=False,
        hovermode='y unified',
        template='plotly_white'
    )
    return fig

def create_category_pie_chart(category_totals):
    """Create category pie chart."""
    fig = go.Figure(data=[
        go.Pie(
            labels=category_totals.index,
            values=category_totals.values,
            marker={'colors': px.colors.qualitative.Set2},
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>'
        )
    ])
    fig.update_layout(
        title="📊 Category Distribution",
        height=400,
        showlegend=True
    )
    return fig

def create_monthly_trend_chart(monthly):
    """Create monthly trend chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly.index,
        y=monthly.values,
        mode='lines+markers',
        name='Monthly Spending',
        line={'color': COLORS['success'], 'width': 3},
        marker={'size': 8},
        fill='tozeroy',
        fillcolor=f'rgba(44, 160, 44, 0.2)',
        hovertemplate='<b>%{x|%B %Y}</b><br>₹%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title="📈 Monthly Spending Trend",
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    return fig

def create_payment_bar_chart(payment_totals):
    """Create payment method bar chart."""
    fig = go.Figure(data=[
        go.Bar(
            x=payment_totals.index,
            y=payment_totals.values,
            marker={'color': COLORS['secondary']},
            text=[f"₹{x:,.0f}" for x in payment_totals.values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>'
        )
    ])
    fig.update_layout(
        title="💰 Payment Methods",
        xaxis_title="Payment Method",
        yaxis_title="Amount (₹)",
        height=400,
        showlegend=False,
        template='plotly_white'
    )
    fig.update_xaxes(tickangle=-45)
    return fig

def create_day_of_week_chart(day_totals):
    """Create day of week average chart."""
    fig = go.Figure(data=[
        go.Bar(
            x=day_totals.index,
            y=day_totals.values,
            marker={'color': COLORS['info']},
            text=[f"₹{x:,.0f}" for x in day_totals.values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Avg: ₹%{y:,.0f}<extra></extra>'
        )
    ])
    fig.update_layout(
        title="📅 Average Spending by Day of Week",
        xaxis_title="Day",
        yaxis_title="Avg Amount (₹)",
        height=400,
        showlegend=False,
        template='plotly_white'
    )
    return fig

# ==================== TRANSACTION FILTER CALLBACK ====================
@callback(
    Output('transactions-output', 'children'),
    [Input('category-filter', 'value'),
     Input('payment-filter', 'value'),
     Input('amount-slider', 'value'),
     Input('data-store', 'data'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_transactions(category, payment, amount_range, data_store, start_date, end_date):
    """Update transactions table based on filters."""
    filtered_df = apply_date_range(dataframe_from_store(data_store), start_date, end_date)
    
    if category != 'all':
        filtered_df = filtered_df[filtered_df['Category'] == category]
    if payment != 'all':
        filtered_df = filtered_df[filtered_df['PaymentMethod'] == payment]
    
    filtered_df = filtered_df[
        (filtered_df['Amount'] >= amount_range[0]) & 
        (filtered_df['Amount'] <= amount_range[1])
    ]
    
    return html.Div([
        html.P(f"📊 Showing {len(filtered_df)} transactions", style={'fontSize': '14px', 'color': '#666', 'marginBottom': '10px'}),
        create_transactions_table(filtered_df)
    ])

# ==================== RUN SERVER ====================
if __name__ == '__main__':
    print("🚀 Dash Dashboard Starting...")
    print("📊 Open your browser to: http://localhost:8051")
    print("💾 Data: ", "Loaded from CSV" if not df.empty else "No data")
    app.run_server(debug=False, host='0.0.0.0', port=8051)
