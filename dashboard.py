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
            style={'width': '200px', 'margin': '0 auto', 'marginBottom': '10px'}
        ),
        
        # Chart News Filter
        html.Div([
            html.Label("Show News on Chart:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='chart-news-filter',
                options=[
                    {'label': 'All News', 'value': 'all'},
                    {'label': 'Positive Only', 'value': 'positive'},
                    {'label': 'Negative Only', 'value': 'negative'},
                    {'label': 'Neutral Only', 'value': 'neutral'},
                    {'label': 'No News', 'value': 'none'}
                ],
                value='all',
                style={'width': '150px', 'display': 'inline-block'}
            )
        ], style={'textAlign': 'center', 'marginBottom': '20px'})
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
                
                # News Filtering and Sorting Controls
                html.Div([
                    # Sentiment Filter
                    html.Div([
                        html.Label("Filter by Sentiment:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='sentiment-filter',
                            options=[
                                {'label': 'All Sentiments', 'value': 'all'},
                                {'label': 'Positive', 'value': 'positive'},
                                {'label': 'Negative', 'value': 'negative'},
                                {'label': 'Neutral', 'value': 'neutral'}
                            ],
                            value='all',
                            style={'width': '120px', 'fontSize': '12px'}
                        )
                    ], style={'display': 'inline-block', 'marginRight': '15px'}),
                    
                    # Sort Order
                    html.Div([
                        html.Label("Sort Order:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='sort-order',
                            options=[
                                {'label': 'Newest First', 'value': 'newest'},
                                {'label': 'Oldest First', 'value': 'oldest'},
                                {'label': 'Most Positive', 'value': 'positive'},
                                {'label': 'Most Negative', 'value': 'negative'}
                            ],
                            value='newest',
                            style={'width': '120px', 'fontSize': '12px'}
                        )
                    ], style={'display': 'inline-block', 'marginRight': '15px'}),
                    
                    # Refresh Button
                    html.Div([
                        html.Button(
                            '🔄 Refresh',
                            id='refresh-button',
                            n_clicks=0,
                            style={
                                'backgroundColor': '#2E86AB',
                                'color': 'white',
                                'border': 'none',
                                'padding': '8px 15px',
                                'borderRadius': '5px',
                                'cursor': 'pointer',
                                'fontSize': '12px'
                            }
                        )
                    ], style={'display': 'inline-block', 'marginRight': '15px'}),
                    
                    # News Refresh Button
                    html.Div([
                        html.Button(
                            '📰 Refresh News',
                            id='refresh-news-button',
                            n_clicks=0,
                            style={
                                'backgroundColor': '#28a745',
                                'color': 'white',
                                'border': 'none',
                                'padding': '8px 15px',
                                'borderRadius': '5px',
                                'cursor': 'pointer',
                                'fontSize': '12px'
                            }
                        )
                    ], style={'display': 'inline-block'})
                ], style={'textAlign': 'center', 'marginBottom': '15px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
                
                # News Refresh Status
                html.Div(id='news-refresh-status', style={'marginBottom': '10px'}),
                
                html.Div(id='recent-news-list', style={'maxHeight': '300px', 'overflowY': 'auto'})
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Trading Insights
            html.Div([
                html.H4("Trading Insights"),
                html.Div(id='insights-list')
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]),
    

    
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
     Input('interval-component', 'n_intervals'),
     Input('refresh-news-button', 'n_clicks'),
     Input('chart-news-filter', 'value')]
)
def update_stock_chart(days, n_clicks, n_intervals, news_clicks, news_filter):
    data = get_api_data(f'/stock/history?days={days}')
    if data and data.get('data'):
        df = pd.DataFrame(data['data'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        
        # Add stock price line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines+markers',
            name='Stock Price',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=4)
        ))
        
        # Add news markers (only if not filtered out)
        if news_filter != 'none':
            # Get news data for a wider range to ensure we have articles
            news_hours = max(days * 24, 168)  # At least 7 days of news
            news_data = get_api_data(f'/news/recent?hours={news_hours}')
            
            if news_data and news_data.get('articles'):
                articles = news_data['articles']
                logger.info(f"Found {len(articles)} articles for chart markers")
                
                # Filter articles based on sentiment
                if news_filter != 'all':
                    articles = [article for article in articles if article.get('sentiment_label') == news_filter]
                    logger.info(f"After sentiment filter: {len(articles)} articles")
                
                # Prepare news data for markers
                news_dates = []
                news_prices = []
                news_titles = []
                news_sentiments = []
                news_colors = []
                
                # Get stock date range for filtering
                stock_start_date = df['timestamp'].min()
                stock_end_date = df['timestamp'].max()
                
                # Group articles by date to avoid overlapping markers
                articles_by_date = {}
                
                for article in articles:
                    try:
                        # Convert timestamp to datetime and handle timezone
                        article_date = pd.to_datetime(article['timestamp'])
                        
                        # If article_date is naive (no timezone), localize it to match stock data
                        if article_date.tz is None:
                            # Assume the same timezone as stock data
                            article_date = article_date.tz_localize(stock_start_date.tz)
                        
                        # Only include articles within the stock chart date range
                        if stock_start_date <= article_date <= stock_end_date:
                            # Group by date (day only) to avoid overlapping markers
                            date_key = article_date.date()
                            if date_key not in articles_by_date:
                                articles_by_date[date_key] = []
                            articles_by_date[date_key].append(article)
                                
                    except Exception as e:
                        logger.error(f"Error processing news article for chart: {e}")
                        continue
                
                # Process one article per date to avoid overlapping markers
                for date_key, date_articles in articles_by_date.items():
                    # Take the first article from each date (or the most recent one)
                    article = date_articles[0]  # You could sort by timestamp here if needed
                    
                    try:
                        article_date = pd.to_datetime(article['timestamp'])
                        
                        # If article_date is naive (no timezone), localize it to match stock data
                        if article_date.tz is None:
                            # Assume the same timezone as stock data
                            article_date = article_date.tz_localize(stock_start_date.tz)
                        
                        # Find closest stock price for this date
                        closest_idx = (df['timestamp'] - article_date).abs().idxmin()
                        closest_price = df.loc[closest_idx, 'price']
                        
                        news_dates.append(article_date)
                        news_prices.append(closest_price)
                        
                        # Create a combined title for multiple articles on the same day
                        if len(date_articles) > 1:
                            title = f"{len(date_articles)} news articles on {date_key}"
                        else:
                            title = article['title']
                        news_titles.append(title)
                        
                        # Map sentiment to numeric value for color scale
                        sentiment = article.get('sentiment_label', 'neutral')
                        if sentiment == 'positive':
                            news_sentiments.append(1)
                            news_colors.append('#28a745')  # Green
                        elif sentiment == 'negative':
                            news_sentiments.append(-1)
                            news_colors.append('#dc3545')  # Red
                        else:
                            news_sentiments.append(0)
                            news_colors.append('#ffc107')  # Yellow
                            
                    except Exception as e:
                        logger.error(f"Error processing grouped article for chart: {e}")
                        continue
                
                logger.info(f"Added {len(news_dates)} news markers to chart")
                
                if news_dates:
                    # Add news markers
                    fig.add_trace(go.Scatter(
                        x=news_dates,
                        y=news_prices,
                        mode='markers',
                        name=f'News Events ({len(news_dates)})',
                        marker=dict(
                            size=16,  # Increased size for better visibility
                            color=news_colors,
                            symbol='diamond',
                            line=dict(color='white', width=2),
                            opacity=0.8
                        ),
                        text=news_titles,
                        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Price: €%{y:.2f}<extra></extra>',
                        showlegend=True
                    ))
                    
                    logger.info(f"Added {len(news_dates)} news markers at dates: {[d.strftime('%Y-%m-%d') for d in news_dates]}")
                else:
                    logger.info("No news markers added - no articles in date range")
            else:
                logger.info("No news data available for chart markers")
        
        fig.update_layout(
            title=f"Brøndby IF Stock Price - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Price (€)",
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
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

# Combined callback to update recent news and handle refresh
@app.callback(
    [Output('news-refresh-status', 'children'),
     Output('recent-news-list', 'children')],
    [Input('global-timeframe-dropdown', 'value'),
     Input('sentiment-filter', 'value'),
     Input('sort-order', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('refresh-news-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    prevent_initial_call=False
)
def update_recent_news_and_refresh(days, sentiment_filter, sort_order, refresh_clicks, news_refresh_clicks, n_intervals):
    # Check if this was triggered by the news refresh button
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    status = ""
    
    # If news refresh button was clicked, try to refresh news
    if triggered_id == 'refresh-news-button' and news_refresh_clicks:
        try:
            # Call the news update API
            response = requests.post(f"{API_BASE_URL}/update/news")
            
            if response.status_code == 200:
                data = response.json()
                articles_saved = data.get('articles_saved', 0)
                status = html.Div([
                    html.P(f"✅ News refreshed successfully! {articles_saved} new articles saved.", 
                          style={'color': '#28a745', 'fontSize': '12px', 'fontWeight': 'bold'})
                ])
            else:
                status = html.Div([
                    html.P(f"❌ Failed to refresh news. Status: {response.status_code}", 
                          style={'color': '#dc3545', 'fontSize': '12px', 'fontWeight': 'bold'})
                ])
        except Exception as e:
            status = html.Div([
                html.P(f"❌ Error refreshing news: {str(e)}", 
                      style={'color': '#dc3545', 'fontSize': '12px', 'fontWeight': 'bold'})
            ])
    
    # Convert days to hours for news API
    hours = days * 24
    data = get_api_data(f'/news/recent?hours={hours}')
    if data and data.get('articles'):
        articles = data['articles']
        
        # Apply sentiment filter
        if sentiment_filter != 'all':
            articles = [article for article in articles if article.get('sentiment_label') == sentiment_filter]
        
        # Apply sorting
        if sort_order == 'newest':
            articles = sorted(articles, key=lambda x: x.get('timestamp', ''), reverse=True)
        elif sort_order == 'oldest':
            articles = sorted(articles, key=lambda x: x.get('timestamp', ''))
        elif sort_order == 'positive':
            articles = sorted(articles, key=lambda x: x.get('sentiment_score', 0), reverse=True)
        elif sort_order == 'negative':
            articles = sorted(articles, key=lambda x: x.get('sentiment_score', 0))
        
        # Limit to 15 articles for display
        articles = articles[:15]
        
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
            
            # Add sentiment score display
            sentiment_score = article.get('sentiment_score', 0)
            sentiment_display = f"{article['sentiment_label'].title()} ({sentiment_score:.3f})"
            
            news_items.append(html.Div([
                html.H6(title_link, style={'margin': '5px 0'}),
                html.P(f"Source: {article['source']}", style={'fontSize': '12px', 'color': '#666'}),
                html.Span(f"Sentiment: {sentiment_display}", 
                         style={'color': sentiment_color, 'fontSize': '12px'}),
                html.Br(),
                html.Small(f"Published: {article['timestamp'][:10] if article.get('timestamp') else 'Unknown'}", 
                          style={'color': '#999', 'fontSize': '10px'}),
                html.Hr(style={'margin': '10px 0'})
            ]))
        
        # Add summary of filtered results
        if sentiment_filter != 'all':
            summary = html.Div([
                html.P(f"Showing {len(articles)} {sentiment_filter} articles", 
                      style={'fontSize': '12px', 'color': '#666', 'fontStyle': 'italic'})
            ])
            return status, [summary] + news_items
        
        return status, news_items
    
    return status, [html.P("No recent news available")]

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
