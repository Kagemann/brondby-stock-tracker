import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, title="Brøndby IF Stock Tracker Dashboard")
app.config.suppress_callback_exceptions = True

# API base URL
API_BASE_URL = "http://localhost:8000"

def get_api_data(endpoint):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Brøndby IF Stock Tracker", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': '20px'}),
        html.Hr()
    ]),
    
    # Current Stock Price Card
    html.Div([
        html.Div([
            html.H3("Current Stock Price", style={'textAlign': 'center'}),
            html.Div(id='current-price-display', style={'textAlign': 'center', 'fontSize': '24px'})
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px'})
    ]),
    
    # Global Timeframe Selector
    html.Div([
        html.H3("Dashboard Timeframe", style={'textAlign': 'center', 'marginBottom': '10px'}),
        dcc.Dropdown(
            id='global-timeframe-dropdown',
            options=[
                {'label': '1 Day', 'value': 1},
                {'label': '7 Days', 'value': 7},
                {'label': '30 Days', 'value': 30},
                {'label': '90 Days', 'value': 90}
            ],
            value=7,
            style={'width': '200px', 'margin': '0 auto', 'marginBottom': '20px'}
        )
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    # Main Content Grid
    html.Div([
        # Left Column
        html.Div([
            # Stock Price Chart
            html.Div([
                html.H4("Stock Price History"),
                dcc.Graph(id='stock-price-chart')
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Volume Chart
            html.Div([
                html.H4("Trading Volume"),
                dcc.Graph(id='volume-chart')
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Right Column
        html.Div([
            # Sentiment Analysis
            html.Div([
                html.H4("News Sentiment Analysis"),
                dcc.Graph(id='sentiment-chart')
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Recent News
            html.Div([
                html.H4("Recent News"),
                html.Div(id='recent-news-list', style={'maxHeight': '300px', 'overflowY': 'auto'})
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Trading Insights
            html.Div([
                html.H4("Trading Insights"),
                html.Div(id='insights-list')
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]),
    
    # Refresh Button
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0,
                   style={'backgroundColor': '#2E86AB', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    # Hidden div for storing data
    html.Div(id='data-store', style={'display': 'none'}),
    
    # Interval component for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=300000,  # 5 minutes
        n_intervals=0
    )
])

# Callback to update current price
@app.callback(
    Output('current-price-display', 'children'),
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_current_price(n_clicks, n_intervals):
    data = get_api_data('/stock/current')
    if data:
        price = data.get('price', 0)
        change = data.get('change_percent', 0)
        change_color = 'green' if change >= 0 else 'red'
        change_symbol = '+' if change >= 0 else ''
        
        return [
            html.Span(f"€{price:.2f}", style={'fontSize': '32px', 'fontWeight': 'bold'}),
            html.Br(),
            html.Span(f"{change_symbol}{change:.2f}%", 
                     style={'color': change_color, 'fontSize': '18px'})
        ]
    return "Loading..."

# Callback to update stock price chart
@app.callback(
    Output('stock-price-chart', 'figure'),
    [Input('global-timeframe-dropdown', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_stock_chart(days, n_clicks, n_intervals):
    data = get_api_data(f'/stock/history?days={days}')
    if data and data.get('data'):
        df = pd.DataFrame(data['data'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines+markers',
            name='Stock Price',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title=f"Brøndby IF Stock Price - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Price (€)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    return go.Figure()

# Callback to update volume chart
@app.callback(
    Output('volume-chart', 'figure'),
    [Input('global-timeframe-dropdown', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_volume_chart(days, n_clicks, n_intervals):
    data = get_api_data(f'/stock/history?days={days}')
    if data and data.get('data'):
        df = pd.DataFrame(data['data'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            marker_color='#A23B72'
        ))
        
        fig.update_layout(
            title=f"Trading Volume - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Volume",
            template='plotly_white'
        )
        
        return fig
    
    return go.Figure()

# Callback to update sentiment chart
@app.callback(
    Output('sentiment-chart', 'figure'),
    [Input('global-timeframe-dropdown', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_sentiment_chart(days, n_clicks, n_intervals):
    # Convert days to hours for news API
    hours = days * 24
    data = get_api_data(f'/news/sentiment?hours={hours}')
    if data and data.get('sentiment_summary'):
        summary = data['sentiment_summary']
        
        # Sentiment distribution pie chart
        labels = ['Positive', 'Negative', 'Neutral']
        values = [
            summary.get('positive_articles', 0),
            summary.get('negative_articles', 0),
            summary.get('neutral_articles', 0)
        ]
        colors = ['#28a745', '#dc3545', '#ffc107']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title=f"News Sentiment Distribution ({days} days)",
            template='plotly_white'
        )
        
        return fig
    
    return go.Figure()

# Callback to update recent news
@app.callback(
    Output('recent-news-list', 'children'),
    [Input('global-timeframe-dropdown', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_recent_news(days, n_clicks, n_intervals):
    # Convert days to hours for news API
    hours = days * 24
    data = get_api_data(f'/news/recent?hours={hours}')
    if data and data.get('articles'):
        articles = data['articles'][:15]  # Show more articles
        
        news_items = []
        for article in articles:
            sentiment_color = {
                'positive': '#28a745',
                'negative': '#dc3545',
                'neutral': '#ffc107'
            }.get(article['sentiment_label'], '#6c757d')
            
            # Create clickable link
            title_text = article['title'][:80] + "..." if len(article['title']) > 80 else article['title']
            title_link = html.A(
                title_text,
                href=article['url'],
                target='_blank',
                style={'color': '#2E86AB', 'textDecoration': 'none', 'fontWeight': 'bold'}
            )
            
            news_items.append(html.Div([
                html.H6(title_link, style={'margin': '5px 0'}),
                html.P(f"Source: {article['source']}", style={'fontSize': '12px', 'color': '#666'}),
                html.Span(f"Sentiment: {article['sentiment_label']}", 
                         style={'color': sentiment_color, 'fontSize': '12px'}),
                html.Br(),
                html.Small(f"Published: {article['timestamp'][:10] if article.get('timestamp') else 'Unknown'}", 
                          style={'color': '#999', 'fontSize': '10px'}),
                html.Hr(style={'margin': '10px 0'})
            ]))
        
        return news_items
    
    return [html.P("No recent news available")]

# Callback to update insights
@app.callback(
    Output('insights-list', 'children'),
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_insights(n_clicks, n_intervals):
    data = get_api_data('/analysis/insights')
    if data and data.get('insights'):
        insights = data['insights']
        
        insight_items = []
        for insight in insights:
            insight_items.append(html.Div([
                html.H6(insight['message'], style={'margin': '5px 0'}),
                html.P(f"Recommendation: {insight['recommendation']}", 
                      style={'fontSize': '12px', 'color': '#666'}),
                html.P(f"Confidence: {insight['confidence']:.2f}", 
                      style={'fontSize': '12px', 'color': '#2E86AB'}),
                html.Hr(style={'margin': '10px 0'})
            ]))
        
        return insight_items
    
    return [html.P("No insights available")]

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
