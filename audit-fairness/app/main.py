"""Main Dash application for AuditFairness dashboard."""
from datetime import datetime
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flask import Flask, jsonify

from app.config import get_settings
from app.database import get_db_session
from app.fairness_service import FairnessService

settings = get_settings()

# Create Flask server
server = Flask(__name__)

# Create Dash app
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.CYBORG,  # Dark professional theme
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="HealthFlow-MS | Fairness Dashboard"
)

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'JetBrains Mono', monospace;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                min-height: 100vh;
            }
            .metric-card {
                background: linear-gradient(145deg, #1e1e2f 0%, #2d2d44 100%);
                border: 1px solid #3d3d5c;
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: 600;
                background: linear-gradient(90deg, #00f5d4, #00bbf9);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .metric-label {
                color: #8b8ba7;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .alert-high {
                border-left: 4px solid #ff6b6b;
            }
            .alert-medium {
                border-left: 4px solid #ffd93d;
            }
            .alert-low {
                border-left: 4px solid #6bcb77;
            }
            .status-good {
                color: #00f5d4;
            }
            .status-warning {
                color: #ffd93d;
            }
            .status-critical {
                color: #ff6b6b;
            }
            .header-gradient {
                background: linear-gradient(90deg, #00f5d4 0%, #00bbf9 50%, #9b5de5 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def create_metric_card(title, value, status="good", subtitle=""):
    """Create a styled metric card."""
    status_class = f"status-{status}"
    return html.Div([
        html.P(title, className="metric-label"),
        html.P(value, className=f"metric-value {status_class}"),
        html.P(subtitle, style={"color": "#6c6c8a", "fontSize": "0.8rem"}) if subtitle else None
    ], className="metric-card")


def create_alert_card(alert):
    """Create an alert card."""
    severity_class = f"alert-{alert.severity}"
    return html.Div([
        html.Div([
            html.Span(alert.alert_type.upper(), style={"fontWeight": "600"}),
            html.Span(f" | {alert.severity.upper()}", 
                     style={"color": "#ff6b6b" if alert.severity == "high" else "#ffd93d"})
        ]),
        html.P(alert.description, style={"margin": "10px 0", "color": "#a0a0b8"}),
        html.P(f"Recommendation: {alert.recommendations}", 
               style={"fontSize": "0.8rem", "color": "#6c6c8a"})
    ], className=f"metric-card {severity_class}")


# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("HealthFlow-MS", className="header-gradient", 
                   style={"fontSize": "2.5rem", "marginBottom": "0"}),
            html.P("Fairness & Bias Monitoring Dashboard", 
                  style={"color": "#8b8ba7", "fontSize": "1rem"})
        ], width=8),
        dbc.Col([
            html.Div([
                html.P("Last Updated", className="metric-label"),
                html.P(id="last-updated", style={"color": "#00f5d4"})
            ], style={"textAlign": "right"})
        ], width=4)
    ], className="mb-4 mt-3"),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col([
            html.Div(id="metric-demographic-parity")
        ], width=3),
        dbc.Col([
            html.Div(id="metric-equalized-odds")
        ], width=3),
        dbc.Col([
            html.Div(id="metric-model-auc")
        ], width=3),
        dbc.Col([
            html.Div(id="metric-predictions")
        ], width=3)
    ]),
    
    # Charts Row
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Fairness Metrics Over Time", style={"color": "#e0e0e0"}),
                dcc.Graph(id="fairness-trend-chart")
            ], className="metric-card")
        ], width=6),
        dbc.Col([
            html.Div([
                html.H5("Risk Distribution by Group", style={"color": "#e0e0e0"}),
                dcc.Graph(id="group-distribution-chart")
            ], className="metric-card")
        ], width=6)
    ], className="mb-4"),
    
    # Detailed Analysis Row
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Performance by Gender", style={"color": "#e0e0e0"}),
                dcc.Graph(id="gender-metrics-chart")
            ], className="metric-card")
        ], width=6),
        dbc.Col([
            html.Div([
                html.H5("Performance by Age Group", style={"color": "#e0e0e0"}),
                dcc.Graph(id="age-metrics-chart")
            ], className="metric-card")
        ], width=6)
    ], className="mb-4"),
    
    # Alerts Section
    dbc.Row([
        dbc.Col([
            html.H5("Active Alerts", style={"color": "#e0e0e0", "marginBottom": "20px"}),
            html.Div(id="alerts-container")
        ], width=12)
    ]),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    ),
    
    # Store for data
    dcc.Store(id='metrics-store')
    
], fluid=True, style={"maxWidth": "1600px"})


@callback(
    [Output('metrics-store', 'data'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    """Fetch latest data from database."""
    db = get_db_session()
    try:
        service = FairnessService(db)
        
        # Get latest metrics
        latest = service.get_latest_metrics()
        history = service.get_metrics_history(30)
        alerts = service.get_active_alerts()
        
        data = {
            'latest': {
                'demographic_parity': latest.demographic_parity_ratio if latest else 0.85,
                'equalized_odds': latest.equalized_odds_ratio if latest else 0.82,
                'auc': latest.overall_auc if latest else 0.82,
                'total_predictions': latest.total_predictions if latest else 0,
                'metrics_by_gender': latest.metrics_by_gender if latest else {},
                'metrics_by_age': latest.metrics_by_age_group if latest else {}
            },
            'history': [
                {
                    'date': str(m.metric_date),
                    'demographic_parity': m.demographic_parity_ratio,
                    'equalized_odds': m.equalized_odds_ratio,
                    'auc': m.overall_auc
                }
                for m in history
            ],
            'alerts': [
                {
                    'id': str(a.id),
                    'alert_type': a.alert_type,
                    'severity': a.severity,
                    'description': a.description,
                    'recommendations': a.recommendations
                }
                for a in alerts
            ]
        }
        
        return data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finally:
        db.close()


@callback(
    Output('metric-demographic-parity', 'children'),
    [Input('metrics-store', 'data')]
)
def update_dp_metric(data):
    if not data:
        return create_metric_card("Demographic Parity", "N/A")
    
    value = data['latest']['demographic_parity']
    status = "good" if value >= 0.8 else "warning" if value >= 0.6 else "critical"
    return create_metric_card(
        "Demographic Parity", 
        f"{value:.2f}",
        status,
        "Ratio ≥ 0.8 is fair"
    )


@callback(
    Output('metric-equalized-odds', 'children'),
    [Input('metrics-store', 'data')]
)
def update_eo_metric(data):
    if not data:
        return create_metric_card("Equalized Odds", "N/A")
    
    value = data['latest']['equalized_odds']
    status = "good" if value >= 0.8 else "warning" if value >= 0.6 else "critical"
    return create_metric_card(
        "Equalized Odds",
        f"{value:.2f}",
        status,
        "Ratio ≥ 0.8 is fair"
    )


@callback(
    Output('metric-model-auc', 'children'),
    [Input('metrics-store', 'data')]
)
def update_auc_metric(data):
    if not data:
        return create_metric_card("Model AUC", "N/A")
    
    value = data['latest']['auc']
    status = "good" if value >= 0.75 else "warning" if value >= 0.6 else "critical"
    return create_metric_card(
        "Model AUC-ROC",
        f"{value:.2f}",
        status,
        "Target ≥ 0.75"
    )


@callback(
    Output('metric-predictions', 'children'),
    [Input('metrics-store', 'data')]
)
def update_predictions_metric(data):
    if not data:
        return create_metric_card("Total Predictions", "N/A")
    
    value = data['latest']['total_predictions']
    return create_metric_card(
        "Total Predictions",
        f"{value:,}",
        "good"
    )


@callback(
    Output('fairness-trend-chart', 'figure'),
    [Input('metrics-store', 'data')]
)
def update_trend_chart(data):
    if not data or not data['history']:
        return go.Figure()
    
    df = pd.DataFrame(data['history'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['demographic_parity'],
        mode='lines+markers',
        name='Demographic Parity',
        line=dict(color='#00f5d4', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['equalized_odds'],
        mode='lines+markers',
        name='Equalized Odds',
        line=dict(color='#00bbf9', width=2),
        marker=dict(size=6)
    ))
    
    # Threshold line
    fig.add_hline(y=0.8, line_dash="dash", line_color="#ffd93d", 
                  annotation_text="Fairness Threshold")
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b8'),
        xaxis=dict(gridcolor='#2d2d44'),
        yaxis=dict(gridcolor='#2d2d44', range=[0, 1.1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


@callback(
    Output('group-distribution-chart', 'figure'),
    [Input('metrics-store', 'data')]
)
def update_distribution_chart(data):
    if not data:
        return go.Figure()
    
    gender_data = data['latest'].get('metrics_by_gender', {})
    
    if not gender_data:
        # Sample data for demo
        gender_data = {
            'male': {'high_risk_rate': 0.35, 'average_risk_score': 0.45},
            'female': {'high_risk_rate': 0.32, 'average_risk_score': 0.42}
        }
    
    groups = list(gender_data.keys())
    high_risk_rates = [gender_data[g].get('high_risk_rate', 0) for g in groups]
    
    fig = go.Figure(data=[
        go.Bar(
            x=groups,
            y=high_risk_rates,
            marker_color=['#00f5d4', '#00bbf9', '#9b5de5', '#f15bb5'][:len(groups)]
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b8'),
        xaxis=dict(gridcolor='#2d2d44'),
        yaxis=dict(gridcolor='#2d2d44', title='High Risk Rate'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


@callback(
    Output('gender-metrics-chart', 'figure'),
    [Input('metrics-store', 'data')]
)
def update_gender_chart(data):
    if not data:
        return go.Figure()
    
    gender_data = data['latest'].get('metrics_by_gender', {})
    
    if not gender_data:
        gender_data = {
            'male': {'precision': 0.78, 'recall': 0.74},
            'female': {'precision': 0.76, 'recall': 0.72}
        }
    
    groups = list(gender_data.keys())
    
    fig = go.Figure(data=[
        go.Bar(name='Precision', x=groups, 
               y=[gender_data[g].get('precision', 0) for g in groups],
               marker_color='#00f5d4'),
        go.Bar(name='Recall', x=groups,
               y=[gender_data[g].get('recall', 0) for g in groups],
               marker_color='#00bbf9')
    ])
    
    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b8'),
        xaxis=dict(gridcolor='#2d2d44'),
        yaxis=dict(gridcolor='#2d2d44', range=[0, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


@callback(
    Output('age-metrics-chart', 'figure'),
    [Input('metrics-store', 'data')]
)
def update_age_chart(data):
    if not data:
        return go.Figure()
    
    age_data = data['latest'].get('metrics_by_age', {})
    
    if not age_data:
        age_data = {
            '18-30': {'high_risk_rate': 0.15, 'average_risk_score': 0.25},
            '30-45': {'high_risk_rate': 0.28, 'average_risk_score': 0.38},
            '45-60': {'high_risk_rate': 0.42, 'average_risk_score': 0.52},
            '60-75': {'high_risk_rate': 0.55, 'average_risk_score': 0.62},
            '75+': {'high_risk_rate': 0.68, 'average_risk_score': 0.72}
        }
    
    groups = list(age_data.keys())
    
    fig = go.Figure(data=[
        go.Scatter(
            x=groups,
            y=[age_data[g].get('high_risk_rate', 0) for g in groups],
            mode='lines+markers',
            name='High Risk Rate',
            line=dict(color='#00f5d4', width=3),
            marker=dict(size=10)
        ),
        go.Scatter(
            x=groups,
            y=[age_data[g].get('average_risk_score', 0) for g in groups],
            mode='lines+markers',
            name='Avg Risk Score',
            line=dict(color='#9b5de5', width=3),
            marker=dict(size=10)
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b8'),
        xaxis=dict(gridcolor='#2d2d44', title='Age Group'),
        yaxis=dict(gridcolor='#2d2d44', range=[0, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


@callback(
    Output('alerts-container', 'children'),
    [Input('metrics-store', 'data')]
)
def update_alerts(data):
    if not data or not data['alerts']:
        return html.Div([
            html.P("✓ No active alerts", 
                  style={"color": "#00f5d4", "textAlign": "center", "padding": "40px"})
        ], className="metric-card")
    
    alert_cards = []
    for alert in data['alerts']:
        alert_obj = type('Alert', (), alert)()
        alert_cards.append(create_alert_card(alert_obj))
    
    return html.Div(alert_cards)


# Flask health endpoint
@server.route('/health')
def health():
    return jsonify({
        "status": "UP",
        "service": "audit-fairness",
        "timestamp": datetime.now().isoformat()
    })


# Run fairness analysis endpoint
@server.route('/api/analyze', methods=['POST'])
def run_analysis():
    db = get_db_session()
    try:
        service = FairnessService(db)
        metrics = service.run_fairness_analysis()
        return jsonify({
            "status": "completed",
            "metric_date": str(metrics.metric_date),
            "demographic_parity": metrics.demographic_parity_ratio,
            "equalized_odds": metrics.equalized_odds_ratio
        })
    finally:
        db.close()


if __name__ == '__main__':
    app.run_server(debug=settings.dash_debug, host='0.0.0.0', port=settings.service_port)


