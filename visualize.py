import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv('UygunData.csv')

cities = df['CITY_NAME'].unique().tolist()
months = df['DATE'].sort_values().unique().tolist()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='city-dropdown-amount-line',
            options=[{'label': city, 'value': city} for city in ['CITY_NAME'] + cities],
            value='CITY_NAME',
            style={'width': '40%', 'height': '30%', 'font-size': '12px', 'color': 'black'}
        ),
        dcc.Graph(id='amount-line-chart')
    ],style={'display': 'inline-block', 'width': '48%'}),

    html.Div([
        dcc.Dropdown(
            id='month-dropdown-top-10-cities',
            options=[{'label': month, 'value': month} for month in ['DATE'] + months],
            value='DATE',
            style={'width': '40%', 'height': '30%', 'font-size': '12px', 'color': 'black'}
        ),
        dcc.Graph(id='top-10-cities-bar-chart')
    ],style={'display': 'inline-block', 'width': '48%'})
])

@app.callback(
    Output('amount-line-chart', 'figure'),
    [Input('city-dropdown-amount-line', 'value')]
)
def update_chart(selected_cities):
    filtered_df = df if 'CITY_NAME' in [selected_cities] or not selected_cities else df[df['CITY_NAME'].isin([selected_cities])]
    avg_amount = filtered_df.groupby(['CUSTOMER_SEGMENT', 'DATE'])['REVENUE_AMOUNT'].mean().reset_index()
    fig = px.line(avg_amount, x='DATE', y='REVENUE_AMOUNT', color='CUSTOMER_SEGMENT', markers=True,
                  text=avg_amount["REVENUE_AMOUNT"].round(),
                  labels={'DATE': 'DATE', 'CUSTOMER_SEGMENT': 'Segment'},
                  title='Average of REVENUE_AMOUNT',
                  category_orders={'CUSTOMER_SEGMENT': ['Corporate', 'Individual']},
                  color_discrete_map={'Individual': 'orange', 'Corporate': 'blue'})
    fig.update_layout(xaxis_type='category', yaxis=dict(showgrid=True, gridcolor='#D3D3D3'), plot_bgcolor='white')
    fig.update_traces(textposition="top center")
    return fig

@app.callback(
    Output('top-10-cities-bar-chart', 'figure'),
    [Input('month-dropdown-top-10-cities', 'value')]
)
def update_top_10_cities(selected_months):
    if 'DATE' in [selected_months] or not selected_months:
        top_10_cities = df.groupby('CITY_NAME')['REVENUE_AMOUNT'].mean().nlargest(10).reset_index()
        fig_1 = px.bar(top_10_cities, x='REVENUE_AMOUNT', y='CITY_NAME', orientation='h', text=top_10_cities['REVENUE_AMOUNT'].round(1),
            labels={'REVENUE_AMOUNT': 'Total REVENUE_AMOUNT', 'CITY_NAME': 'City'},
            title='Top 10 Cities by Total REVENUE_AMOUNT',
            category_orders={"CITY_NAME": top_10_cities.sort_values("REVENUE_AMOUNT", ascending=False)["CITY_NAME"].tolist()}
        )
    else:
        filtered_df = df[df['DATE'].isin([selected_months])]
        avg_month = filtered_df.groupby('CITY_NAME')['REVENUE_AMOUNT'].mean().nlargest(10).reset_index()
        avg_month = avg_month.sort_values('REVENUE_AMOUNT', ascending=False)
        fig_1 = px.bar(avg_month, x='REVENUE_AMOUNT', y='CITY_NAME', orientation='h', text=avg_month["REVENUE_AMOUNT"].round(1),
            labels={'REVENUE_AMOUNT': 'Average REVENUE_AMOUNT', 'CITY_NAME': 'City'},
            title=f'REVENUE_AMOUNT by City in {", ".join(map(str, [selected_months]))}',
            category_orders={"CITY_NAME": avg_month.sort_values("REVENUE_AMOUNT", ascending=False)["CITY_NAME"].tolist()}
        )
    return fig_1

if __name__ == '__main__':
    app.run_server(debug=True)
