import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
import plotly.express as px
import pandas as pd

# Load your pre-processed master data
master_df = pd.read_csv('master_cleaned_reduced.csv.gz', 
                        parse_dates=['transfer_date', 'date_of_birth'], 
                        compression='gzip')

master_df['transfer_year'] = master_df['transfer_date'].dt.year
master_df['player_age'] = master_df['transfer_date'].dt.year - master_df['date_of_birth'].dt.year

master_df['transfer_fee_b'] = master_df['transfer_fee'] / 1e9
master_df['transfer_fee_m'] = master_df['transfer_fee'] / 1e6
master_df['transfer_fee_t'] = master_df['transfer_fee'] / 1e3

# Standardize league names for the destination club by replacing hyphens and applying title case
if 'league_name_to' in master_df.columns:
    master_df['league_name_to'] = master_df['league_name_to'].str.replace('-', ' ').str.title()
else:
    print("Warning: 'league_name_to' column not found in master_df.")
    
# Full list of recognized country names for mapping and merging
country_names = ['Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 'Bosnia and Herzegovina', 'Barbados', 'Wallis and Futuna', 'Saint Barthelemy', 'Bermuda', 'Brunei', 'Bolivia', 'Bahrain', 'Burundi', 'Benin', 'Bhutan', 'Jamaica', 'Bouvet Island', 'Botswana', 'Samoa', 'Bonaire, Saint Eustatius and Saba', 'Brazil', 'Bahamas', 'Jersey', 'Belarus', 'Belize', 'Russia', 'Rwanda', 'Serbia', 'East Timor', 'Reunion', 'Turkmenistan', 'Tajikistan', 'Romania', 'Tokelau', 'Guinea-Bissau', 'Guam', 'Guatemala', 'South Georgia and the South Sandwich Islands', 'Greece', 'Equatorial Guinea', 'Guadeloupe', 'Japan', 'Guyana', 'Guernsey', 'French Guiana', 'Georgia', 'Grenada', 'United Kingdom', 'Gabon', 'El Salvador', 'Guinea', 'Gambia', 'Greenland', 'Gibraltar', 'Ghana', 'Oman', 'Tunisia', 'Jordan', 'Croatia', 'Haiti', 'Hungary', 'Hong Kong', 'Honduras', 'Heard Island and McDonald Islands', 'Venezuela', 'Puerto Rico', 'Palestinian Territory', 'Palau', 'Portugal', 'Svalbard and Jan Mayen', 'Paraguay', 'Iraq', 'Panama', 'French Polynesia', 'Papua New Guinea', 'Peru', 'Pakistan', 'Philippines', 'Pitcairn', 'Poland', 'Saint Pierre and Miquelon', 'Zambia', 'Western Sahara', 'Estonia', 'Egypt', 'South Africa', 'Ecuador', 'Italy', 'Vietnam', 'Solomon Islands', 'Ethiopia', 'Somalia', 'Zimbabwe', 'Saudi Arabia', 'Spain', 'Eritrea', 'Montenegro', 'Moldova', 'Madagascar', 'Saint Martin', 'Morocco', 'Monaco', 'Uzbekistan', 'Myanmar', 'Mali', 'Macao', 'Mongolia', 'Marshall Islands', 'Macedonia', 'Mauritius', 'Malta', 'Malawi', 'Maldives', 'Martinique', 'Northern Mariana Islands', 'Montserrat', 'Mauritania', 'Isle of Man', 'Uganda', 'Tanzania', 'Malaysia', 'Mexico', 'Israel', 'France', 'British Indian Ocean Territory', 'Saint Helena', 'Finland', 'Fiji', 'Falkland Islands', 'Micronesia', 'Faroe Islands', 'Nicaragua', 'Netherlands', 'Norway', 'Namibia', 'Vanuatu', 'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria', 'New Zealand', 'Nepal', 'Nauru', 'Niue', 'Cook Islands', 'Kosovo', 'Ivory Coast', 'Switzerland', 'Colombia', 'China', 'Cameroon', 'Chile', 'Cocos Islands', 'Canada', 'Republic of the Congo', 'Central African Republic', 'Democratic Republic of the Congo', 'Czech Republic', 'Cyprus', 'Christmas Island', 'Costa Rica', 'Curacao', 'Cape Verde', 'Cuba', 'Swaziland', 'Syria', 'Sint Maarten', 'Kyrgyzstan', 'Kenya', 'South Sudan', 'Suriname', 'Kiribati', 'Cambodia', 'Saint Kitts and Nevis', 'Comoros', 'Sao Tome and Principe', 'Slovakia', 'South Korea', 'Slovenia', 'North Korea', 'Kuwait', 'Senegal', 'San Marino', 'Sierra Leone', 'Seychelles', 'Kazakhstan', 'Cayman Islands', 'Singapore', 'Sweden', 'Sudan', 'Dominican Republic', 'Dominica', 'Djibouti', 'Denmark', 'British Virgin Islands', 'Germany', 'Yemen', 'Algeria', 'United States', 'Uruguay', 'Mayotte', 'United States Minor Outlying Islands', 'Lebanon', 'Saint Lucia', 'Laos', 'Tuvalu', 'Taiwan', 'Trinidad and Tobago', 'Turkey', 'Sri Lanka', 'Liechtenstein', 'Latvia', 'Tonga', 'Lithuania', 'Luxembourg', 'Liberia', 'Lesotho', 'Thailand', 'French Southern Territories', 'Togo', 'Chad', 'Turks and Caicos Islands', 'Libya', 'Vatican', 'Saint Vincent and the Grenadines', 'United Arab Emirates', 'Andorra', 'Antigua and Barbuda', 'Afghanistan', 'Anguilla', 'U.S. Virgin Islands', 'Iceland', 'Iran', 'Armenia', 'Albania', 'Angola', 'Antarctica', 'American Samoa', 'Argentina', 'Australia', 'Austria', 'Aruba', 'India', 'Aland Islands', 'Azerbaijan', 'Ireland', 'Indonesia', 'Ukraine', 'Qatar', 'Mozambique']

# Map for non-standard country names found in the dataset
name_map = {
    "Cote d'Ivoire": "Ivory Coast",
    "England": "United Kingdom",
    "Scotland": "United Kingdom",
    "Wales": "United Kingdom",
    "Northern Ireland": "United Kingdom",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Congo": "Republic of the Congo",
    "Korea, South": "South Korea",
    "DR Congo": "Democratic Republic of the Congo",
    "North Macedonia": "Macedonia",
    "The Gambia": "Gambia",
    "Türkiye": "Turkey",
    "Bonaire": "Bonaire, Saint Eustatius and Saba",
    "St. Kitts & Nevis": "Saint Kitts and Nevis",
    "Palestine": "Palestinian Territory"
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Time Based", tab_id="tab-time"),
                dbc.Tab(label="Leagues", tab_id="tab-leagues"),
                dbc.Tab(label="Clubs", tab_id="tab-clubs"),
                dbc.Tab(label="Players", tab_id="tab-players"),
            ],
            id="tabs",
            active_tab="tab-time",
            className="mb-3"  # margin bottom for spacing
        ),
        html.Div(id="tab-content")
    ],
    fluid=True  # ensures the container scales nicely on all devices
)

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "tab-time":
        return dbc.Container([
                html.H4("Time Based Analysis"),
                html.P("Use the slider to select a year range. The charts below display the highest transfer fee per year, the top 5 spending leagues, and trends over time in transfer fees versus player age, as well as a choropleth map of transfer fees by country."),


                # Year Range Slider at the top
                dcc.RangeSlider(
                    id='year-slider',
                    min=master_df['transfer_year'].min(),
                    max=master_df['transfer_year'].max(),
                    value=[2014, master_df['transfer_year'].max()],
                    marks={str(year): str(year) for year in range(master_df['transfer_year'].min(), master_df['transfer_year'].max()+1)},
                    step=1
                ),

                html.Br(),

                # 1st Row: Two side-by-side charts (max fee and top 5 league line)
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(id='graph-max-fee')
                            ),
                            className="mb-3"
                        ),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(id='top5-league-line')
                            ),
                            className="mb-3"
                        ),
                        width=6
                    )
                ]),

                # 2nd Row: A full-width scatter plot (transfer fee vs. age)
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(id='transfer-fee-vs-age')
                            ),
                            className="mb-3"
                        ),
                        width=12
                    )
                ]),

                # 3rd Row: A full-width choropleth map (transfer fees by country)
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(id='transfer-fee-choropleth')
                            ),
                            className="mb-3"
                        ),
                        width=12
                    )
                ])
        ], fluid=True)
    elif active_tab == "tab-leagues":
        return dbc.Container([

            html.H4("Leagues Analysis"),
            html.P("Explore league spending trends over time. Use the filters below to adjust the age range, player positions, and preferred foot criteria."),

            
            # Age range slider
            html.Label("Age Range"),
            dcc.RangeSlider(
                id='age-range-slider',
                min=master_df['player_age'].min(),
                max=master_df['player_age'].max(),
                value=[18, 30],
                marks={str(a): str(a) for a in range(15, 41, 2)},  # Adjust this if necessary
                step=1
            ),

            # Position checklist
            html.Label("Positions"),
            dcc.Checklist(
                id='position-checklist',
                options=[
                    {'label': 'Attacker', 'value': 'Attacker'},
                    {'label': 'Midfielder', 'value': 'Midfielder'},
                    {'label': 'Defender', 'value': 'Defender'},
                    {'label': 'Goalkeeper', 'value': 'Goalkeeper'}
                ],
                value=['Attacker', 'Midfielder', 'Defender', 'Goalkeeper']  # default all selected
            ),

            # Preferred foot dropdown
            html.Label("Preferred Foot"),
            dcc.Dropdown(
                id='foot-dropdown',
                options=[
                    {'label': 'Left', 'value': 'left'},
                    {'label': 'Right', 'value': 'right'},
                    {'label': 'Both', 'value': 'both'},
                    {'label': 'Unknown', 'value': 'Unknown'}
                ],
                value=['left', 'right', 'both', 'Unknown'],  # default all
                multi=True
            ),

            html.Br(),

            # Static Bar Chart
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='league-total-fees-bar')
                ),
                className="mb-3"
            ),

            html.Br(),

            # Animated Race Chart
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='leagues-race')
                ),
                className="mb-3"
            )
        ], fluid=True)
    elif active_tab == "tab-clubs":
        return dbc.Container([
            html.H4("Clubs Analysis"),
            html.P("Explore club spending trends over time. Use the slider to choose a year range and filter by league. Then, view an animated race chart of clubs' cumulative transfer fees and a static bar chart of total fees per year for selected clubs."),


            # Year Range Slider
            html.Label("Year Range"),
            dcc.RangeSlider(
                id='clubs-year-slider',
                min=master_df['transfer_year'].min(),
                max=master_df['transfer_year'].max(),
                value=[2014, master_df['transfer_year'].max()],
                marks={str(y): str(y) for y in range(master_df['transfer_year'].min(), master_df['transfer_year'].max()+1)},
                step=1
            ),

            html.Br(),

            # League Filter
            html.Label("Select League(s)"),
            dcc.Dropdown(
                id='league-dropdown',
                options=[{'label': x, 'value': x} for x in sorted(master_df['league_name_to'].dropna().unique())],
                value=sorted(master_df['league_name_to'].dropna().unique())[:3],  # default selection (first three, for example)
                multi=True,
                placeholder="Select one or more leagues..."
            ),


            html.Br(),

            # Race Chart (Animated)
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='clubs-race')
                ),
                className="mb-3"
            ),

            html.Br(),

            # Static Bar Chart
            html.Label("Select Club"),
            dcc.Dropdown(
                id='club-dropdown',
                multi=True,
                placeholder="Pick one or more clubs..."
            ),
            
            html.Br(),
            
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='clubs-bar')
                ),
                className="mb-3"
            )
        ], fluid=True)
    elif active_tab == "tab-players":
        return dbc.Container([
            html.H4("Players Analysis"),
            html.P("Explore players' transfer fee trends over time. The animated race chart below displays cumulative transfer fees by player, and the bar chart shows the median transfer fee by preferred foot."),
            
            # Year Range Slider for Players Race Chart
            html.Label("Year Range for Players Race Chart"),
            dcc.RangeSlider(
                id='players-year-slider',
                min=master_df['transfer_year'].min(),
                max=master_df['transfer_year'].max(),
                value=[2014, master_df['transfer_year'].max()],
                marks={str(year): str(year) for year in range(master_df['transfer_year'].min(), master_df['transfer_year'].max()+1)},
                step=1
            ),
            html.Br(),
            
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='players-race')
                ),
                className="mb-3"
            ),
            
            html.Br(),
            html.Hr(),
            html.Br(),
            
            # Header for Preferred Foot Bar Chart
            html.H4("Median Transfer Fee by Preferred Foot"),
            html.P("This chart shows the median transfer fee for players based on their preferred foot."),
            
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='players-foot-bar')
                ),
                className="mb-3"
            )
        ], fluid=True)

    return "No tab selected"

# Max Transfer Fee per Year Bar Chart
@app.callback(
    Output('graph-max-fee', 'figure'),
    Input('year-slider', 'value')
)
def update_max_fee_bar(year_range):
    # Filter
    filtered = master_df[
        (master_df['transfer_year'] >= year_range[0]) &
        (master_df['transfer_year'] <= year_range[1])
    ]

    # 2. Aggregate raw fees (max)
    max_fee_year = filtered.groupby('transfer_year')['transfer_fee'].max().reset_index(name='raw_fee')

    # 3. Decide on a single scale for the entire chart based on the maximum bar
    overall_max = max_fee_year['raw_fee'].max()
    scale_col, scale_suffix = pick_scale_column(overall_max)

    # If scale_col == 'transfer_fee_b', we divide by 1e9; if 'transfer_fee_m', we divide by 1e6, etc.
    if scale_col == 'transfer_fee_b':
        max_fee_year['scaled_fee'] = max_fee_year['raw_fee'] / 1e9
    elif scale_col == 'transfer_fee_m':
        max_fee_year['scaled_fee'] = max_fee_year['raw_fee'] / 1e6
    elif scale_col == 'transfer_fee_t':
        max_fee_year['scaled_fee'] = max_fee_year['raw_fee'] / 1e3
    else:
        max_fee_year['scaled_fee'] = max_fee_year['raw_fee']

    # 4. Format each bar's fee individually for hover
    max_fee_year['formatted_fee'] = max_fee_year['raw_fee'].apply(format_fee)

    # 5. Build the bar chart using scaled_fee as the y-axis
    fig = px.bar(
        max_fee_year,
        x='transfer_year',
        y='scaled_fee',
        title=f"Highest Transfer Fee Each Year ({year_range[0]}-{year_range[1]}) {scale_suffix}",
        labels={'scaled_fee': f"Transfer Fee {scale_suffix}", 'transfer_year': 'Year'},
        custom_data=['transfer_year', 'formatted_fee']
    )

    # 6. Use a custom hovertemplate to show the individually scaled fee
    fig.update_traces(
        hovertemplate=(
            "Year: %{customdata[0]}<br>"
            "Highest Transfer Fee: %{customdata[1]}<br>"
            "<extra></extra>"
        )
    )

    return fig

# Top 5 Spending Leagues Every Year
@app.callback(
    Output('top5-league-line', 'figure'),
    Input('year-slider', 'value')
)
def update_top5_league_line(year_range):
    # Filter
    filtered = master_df[
        (master_df['transfer_year'] >= year_range[0]) &
        (master_df['transfer_year'] <= year_range[1])
    ]
    
    # Sum raw fees by league/year
    league_year = filtered.groupby(['transfer_year','league_name_to'])['transfer_fee'].sum().reset_index(name='raw_fee')
    
    # Possibly pick top 5 leagues
    top5 = league_year.groupby('league_name_to')['raw_fee'].sum().nlargest(5).index
    league_year = league_year[league_year['league_name_to'].isin(top5)]
    
    # Determine overall max to pick scale
    overall_max = league_year['raw_fee'].max()
    scale_col, scale_suffix = pick_scale_column(overall_max)
    
    # Create scaled_fee
    if scale_col == 'transfer_fee_b':
        league_year['scaled_fee'] = league_year['raw_fee'] / 1e9
    elif scale_col == 'transfer_fee_m':
        league_year['scaled_fee'] = league_year['raw_fee'] / 1e6
    elif scale_col == 'transfer_fee_t':
        league_year['scaled_fee'] = league_year['raw_fee'] / 1e3
    else:
        league_year['scaled_fee'] = league_year['raw_fee']
    
    # Format each row’s raw fee
    league_year['formatted_fee'] = league_year['raw_fee'].apply(format_fee)

    fig = px.line(
        league_year,
        x='transfer_year',
        y='scaled_fee',
        color='league_name_to',
        title=f"Top 5 Spending Leagues Every Year {scale_suffix}",
        labels={'scaled_fee': f"Fees {scale_suffix}", 'transfer_year': 'Year', 'league_name_to': 'League'},
        custom_data=['transfer_year', 'league_name_to', 'formatted_fee']
    )

    fig.update_traces(
        hovertemplate=(
            "Year: %{customdata[0]}<br>"
            "League: %{customdata[1]}<br>"
            "Fees: %{customdata[2]}<br>"
            "<extra></extra>"
        )
    )

    return fig

# Transfer Fee vs Age over Time
@app.callback(
    Output('transfer-fee-vs-age', 'figure'),
    Input('year-slider', 'value')
)
def update_scatter_age(year_range):
    # Filter data for the selected range
    filtered = master_df[
        (master_df['transfer_year'] >= year_range[0]) &
        (master_df['transfer_year'] <= year_range[1])
    ].copy()

    # Decide on a scale based on overall maximum fee in the filtered data
    overall_max = filtered['transfer_fee'].max()
    scale_col, scale_suffix = pick_scale_column(overall_max)

    # Create scaled_fee
    if scale_col == 'transfer_fee_b':
        filtered['scaled_fee'] = filtered['transfer_fee'] / 1e9
    elif scale_col == 'transfer_fee_m':
        filtered['scaled_fee'] = filtered['transfer_fee'] / 1e6
    elif scale_col == 'transfer_fee_t':
        filtered['scaled_fee'] = filtered['transfer_fee'] / 1e3
    else:
        filtered['scaled_fee'] = filtered['transfer_fee']

    # Format each point’s raw fee
    filtered['formatted_fee'] = filtered['transfer_fee'].apply(format_fee)

    fig = px.scatter(
        filtered,
        x='player_age',
        y='scaled_fee',
        color='transfer_year',
        title=f"Transfer Fees vs. Age {scale_suffix}",
        labels={'scaled_fee': f"Fees {scale_suffix}", 'transfer_year': 'Year', 'player_age': 'Age'},
        custom_data=['player_name', 'formatted_fee', 'club_name_from', 'club_name_to', 'position']
    )

     # 4. Customize hovertemplate to display these fields
    fig.update_traces(
        hovertemplate=(
            "Player: %{customdata[0]}<br>"
            "Fee: %{customdata[1]}<br>"
            "From: %{customdata[2]}<br>"
            "To: %{customdata[3]}<br>"
            "Position: %{customdata[4]}<br>"
            "Age: %{x}<br>"
            "Year: %{marker.color}<extra></extra>"
        )
    )
    
    return fig

# Total Transfer Fees by Country
@app.callback(
    Output('transfer-fee-choropleth', 'figure'),
    Input('year-slider', 'value')
)
def update_choropleth(year_range):
    # 1. Filter data within the selected year range and only transfers > 0
    filtered = master_df[
        (master_df['transfer_year'] >= year_range[0]) &
        (master_df['transfer_year'] <= year_range[1]) &
        (master_df['transfer_fee'] > 0)
    ].copy()

     # 2. Map country names
    filtered['country_plotly'] = filtered['country_of_citizenship'].replace(name_map)
    filtered.loc[
        filtered['country_plotly'].isin(["England", "Scotland", "Wales", "Northern Ireland"]), 
        'country_plotly'
    ] = "United Kingdom"
    
    # 3. Group by raw fees for the tooltip, rename transfer_fee to raw_fee
    grouped = filtered.groupby('country_plotly')['transfer_fee'].sum().reset_index().rename(columns={'transfer_fee': 'raw_fee'})

    grouped['fee_m'] = grouped['raw_fee'] / 1e6  # store millions for the color scale

    # 4. Merge with all countries
    all_countries = pd.DataFrame({'country_plotly': country_names})
    merged_countries = all_countries.merge(grouped, on='country_plotly', how='left')
    merged_countries[['raw_fee','fee_m']] = merged_countries[['raw_fee','fee_m']].fillna(0)

    # 5. Create a formatted fee using format_fee function
    merged_countries['fee_str'] = merged_countries['raw_fee'].apply(format_fee)

    # 6. Define color scale (0 -> grey, positive -> range of blues)
    custom_colorscale = [
        [0.0, '#f0f0f0'],   # Zero fee -> grey
        [0.00001, 'lightblue'],
        [1.0, 'blue']
    ]

    # 7. Build the choropleth
    fig = px.choropleth(
        merged_countries,
        locations='country_plotly',
        locationmode='country names',
        color='fee_m',
        title='Total Transfer Fees by Country (M)',
        color_continuous_scale=custom_colorscale,
        range_color=(0, merged_countries['fee_m'].max() if merged_countries['fee_m'].max() > 0 else 1),
        labels={'fee_m': 'Fees (M)', 'country_plotly': 'Country'},
        hover_name='country_plotly',
        custom_data=['country_plotly', 'fee_str']
    )

    # 8. Geo styling
    fig.update_geos(
        scope='world',
        showcountries=True,
        countrycolor="black",
        showocean=True,
        oceancolor="#dfe9f3"
    )

    # 9. Annotation
    fig.add_annotation(
        x=0.5, y=-0.1,
        xref='paper', yref='paper',
        text="Grey indicates no data available.",
        showarrow=False,
        xanchor='center'
    )

    # 10. Custom hovertemplate
    fig.update_traces(
        hovertemplate=(
            "%{customdata[0]}<br>"
            "Total Fees: %{customdata[1]}<br>"  # This uses fee_str
            "<extra></extra>"
        )
    )

    return fig

def pick_scale_column(max_fee):
    """Return which scale (billions, millions, thousands, or raw) to use 
       based on the maximum fee in the dataset."""
    if max_fee == 0:
        return 'transfer_fee', ''   
    if max_fee >= 1e9:
        return 'transfer_fee_b', '(B)'
    elif max_fee >= 1e6:
        return 'transfer_fee_m', '(M)'
    elif max_fee >= 1e3:
        return 'transfer_fee_t', '(K)'
    else:
        return 'transfer_fee', ''

def format_fee(value):
    """Return a string with the appropriate suffix (B, M, K) for the given fee."""
    try:
        fee = float(value)
    except (ValueError, TypeError):
        return "N/A"
    
    if fee >= 1e9:
        return f"{fee/1e9:.2f}B"
    elif fee >= 1e6:
        return f"{fee/1e6:.2f}M"
    elif fee >= 1e3:
        return f"{fee/1e3:.2f}K"
    else:
        return f"{fee:.2f}"

# Total Transfer Fees by League (All Time)
@app.callback(
    Output('league-total-fees-bar', 'figure'),
    [Input('age-range-slider', 'value'),
     Input('position-checklist', 'value'),
     Input('foot-dropdown', 'value')]
)
def update_league_total_fees_bar(age_range, positions, foot_values):
    min_age, max_age = age_range
    
    # Filter based on age, position, and foot
    filtered = master_df[
        (master_df['player_age'] >= min_age) &
        (master_df['player_age'] <= max_age) &
        (master_df['position'].isin(positions)) &
        (master_df['foot'].isin(foot_values)) &
        (master_df['transfer_fee'] > 0)
    ]
    
    # Group by league (using league_name_to) and sum transfer fees
    league_fees = filtered.groupby('league_name_to')['transfer_fee'].sum().reset_index()
    
    overall_max = league_fees['transfer_fee'].max()
    scale_col, scale_suffix = pick_scale_column(overall_max)
    if scale_col == 'transfer_fee_m':
        league_fees['scaled_fee'] = league_fees['transfer_fee'] / 1e6
    elif scale_col == 'transfer_fee_b':
        league_fees['scaled_fee'] = league_fees['transfer_fee'] / 1e9
    elif scale_col == 'transfer_fee_t':
        league_fees['scaled_fee'] = league_fees['transfer_fee'] / 1e3
    else:
        league_fees['scaled_fee'] = league_fees['transfer_fee']

    # Create a bar chart and sort leagues by descending fee
    fig_bar = px.bar(
        league_fees,
        x='league_name_to',
        y='scaled_fee',
        title=f"Total Transfer Fees by League (All Time) {scale_suffix}",
        labels={'league_name_to': 'League', 'scaled_fee': 'Transfer Fees'},
        custom_data=['transfer_fee']  # if you want to include the raw fee in hover
    )
    
    # Order leagues by total fee in descending order
    fig_bar.update_layout(xaxis={'categoryorder': 'total descending'})
    
    # Optionally, customize the hovertemplate to show the raw fee
    fig_bar.update_traces(
        hovertemplate=(
            "League: %{x}<br>" +
            "Total Fees: %{customdata[0]:,.0f}<br>" +
            "<extra></extra>"
        )
    )
    
    return fig_bar

# Accumulative Total Transfer Fees by League Over Time
@app.callback(
    Output('leagues-race', 'figure'),
    [Input('age-range-slider', 'value'),
     Input('position-checklist', 'value'),
     Input('foot-dropdown', 'value')]
)
def update_leagues_race(age_range, positions, foot_values):
    min_age, max_age = age_range
    # Filter data based on selected filters
    filtered = master_df[
        (master_df['player_age'] >= min_age) &
        (master_df['player_age'] <= max_age) &
        (master_df['position'].isin(positions)) &
        (master_df['foot'].isin(foot_values))
    ]
    
    # Group data by year and league, summing fees
    league_year = filtered.groupby(['transfer_year', 'league_name_to'])['transfer_fee'].sum().reset_index()

    # If you prefer a cumulative sum (accumulative fees up to that year), you can compute it like this:
    league_year = league_year.sort_values(['league_name_to', 'transfer_year'])
    league_year['cumulative_fee'] = league_year.groupby('league_name_to')['transfer_fee'].cumsum()
    # Then use x='cumulative_fee' in the chart.

    league_year = league_year.sort_values(['transfer_year', 'cumulative_fee'], ascending=[True, False])
    league_year = league_year.groupby('transfer_year').head(5)

    def assign_rank(df):
        df['rank'] = range(1, len(df) + 1)
        return df

    league_year = league_year.groupby('transfer_year', group_keys=True).apply(assign_rank).reset_index(drop=True)

    # Create the animated bar chart (horizontal)
    fig_race = px.bar(
        league_year,
        # x='transfer_fee',
        x='cumulative_fee',
        y='rank',
        color='league_name_to',
        orientation='h',
        animation_frame='transfer_year',
        text='league_name_to',  # <-- pass the column name here
        range_x=[0, league_year['cumulative_fee'].max() * 1.1],
        title='Accumulative Transfer Fees Over Time by League',
        labels={'cumulative_fee': 'Fees', 'league_name_to': 'League', 'transfer_year': 'Year', 'rank': 'Rank'}
    )

    fig_race.update_layout(yaxis={'autorange': 'reversed'})

    return fig_race

@app.callback(
    Output('clubs-race', 'figure'),
    [Input('clubs-year-slider', 'value'),
     Input('league-dropdown', 'value')]
)
def update_clubs_race(year_range, selected_leagues):
    min_year, max_year = year_range

    # 1. Filter data based on year range and selected leagues
    filtered = master_df[
        (master_df['transfer_year'] >= min_year) &
        (master_df['transfer_year'] <= max_year) &
        (master_df['league_name_to'].isin(selected_leagues))
    ]

    # 2. Group data by (transfer_year, club_name_to), summing fees
    clubs_year = filtered.groupby(['transfer_year', 'club_name_to'])['transfer_fee'].sum().reset_index()

    # 3. Sort for cumsum if you want accumulative
    clubs_year = clubs_year.sort_values(['club_name_to','transfer_year'])
    clubs_year['cumulative_fee'] = clubs_year.groupby('club_name_to')['transfer_fee'].cumsum()

    # 4. Sort by (year, cumulative_fee) desc, pick top 20 clubs each year
    clubs_year = clubs_year.sort_values(['transfer_year','cumulative_fee'], ascending=[True,False])
    clubs_year = clubs_year.groupby('transfer_year').head(20)

    # 5. Assign rank so we can do a bar chart race
    def assign_rank(df):
        df['rank'] = range(1, len(df)+1)
        return df
    clubs_year['rank'] = clubs_year.groupby('transfer_year')['cumulative_fee']\
                              .rank(ascending=False, method='first').astype(int)


    # 6. Build the race chart
    fig_race = px.bar(
        clubs_year,
        x='cumulative_fee',
        y='rank',
        orientation='h',
        color='club_name_to',
        animation_frame='transfer_year',
        text='club_name_to',
        range_x=[0, clubs_year['cumulative_fee'].max() * 1.1],
        title='Accumulative Transfer Fees Over Time by Club',
        labels={'cumulative_fee': 'Fees', 'club_name_to': 'Club', 'transfer_year': 'Year', 'rank': 'Rank'}
    )

    # Reverse the y-axis so rank=1 is at the top
    fig_race.update_layout(yaxis={'autorange': 'reversed'})

    return fig_race

@app.callback(
    Output('club-dropdown', 'options'),
    [Input('league-dropdown', 'value')]
)
def update_club_options(selected_leagues):
    # Filter the master_df for these leagues
    sub_df = master_df[master_df['league_name_to'].isin(selected_leagues)]
    clubs = sub_df['club_name_to'].unique()
    return [{'label': c, 'value': c} for c in sorted(clubs)]

@app.callback(
    Output('clubs-bar', 'figure'),
    [Input('clubs-year-slider', 'value'),
     Input('league-dropdown', 'value'),
     Input('club-dropdown', 'value')]
)
def update_clubs_bar(year_range, selected_leagues, selected_clubs):
    min_year, max_year = year_range

    # 1. Filter data
    filtered = master_df[
        (master_df['transfer_year'] >= min_year) &
        (master_df['transfer_year'] <= max_year) &
        (master_df['league_name_to'].isin(selected_leagues))
    ]
    if selected_clubs:  # if the user picked some clubs
        filtered = filtered[filtered['club_name_to'].isin(selected_clubs)]

    # 2. Group by year, summing fees
    year_fees = filtered.groupby('transfer_year')['transfer_fee'].sum().reset_index()

    # 3. Create a bar chart of total fees per year
    fig_bar = px.bar(
        year_fees,
        x='transfer_year',
        y='transfer_fee',
        title='Total Transfer Fees per Year',
        labels={'transfer_year': 'Year', 'transfer_fee': 'Fees'}
    )
    return fig_bar

@app.callback(
    Output('players-race', 'figure'),
    Input('players-year-slider', 'value')
)
def update_players_race(year_range):
    min_year, max_year = year_range

    # Filter data for the selected year range
    filtered = master_df[(master_df['transfer_year'] >= min_year) &
                         (master_df['transfer_year'] <= max_year)].copy()

    # Group by (transfer_year, player_name) and sum transfer fees for that year
    players_year = filtered.groupby(['transfer_year', 'player_name'])['transfer_fee'].sum().reset_index(name='year_fee')

    # Sort by player then by year and compute cumulative fees for each player
    players_year = players_year.sort_values(['player_name', 'transfer_year'])
    players_year['cumulative_fee'] = players_year.groupby('player_name')['year_fee'].cumsum()

    # For each year, sort players descending by cumulative_fee and select top 10 players
    players_year = players_year.sort_values(['transfer_year', 'cumulative_fee'], ascending=[True, False])
    players_year = players_year.groupby('transfer_year').head(10)

    # Assign rank within each year (highest cumulative_fee gets rank 1)
    players_year['rank'] = players_year.groupby('transfer_year')['cumulative_fee']\
                                       .rank(ascending=False, method='first').astype(int)

    # Create the animated bar chart
    fig_race = px.bar(
        players_year,
        x='cumulative_fee',
        y='rank',
        color='player_name',
        orientation='h',
        animation_frame='transfer_year',
        text='player_name',
        range_x=[0, players_year['cumulative_fee'].max() * 1.1],
        title='Accumulative Transfer Fees Over Time by Player',
        labels={'cumulative_fee': 'Cumulative Fee', 'player_name': 'Player', 'transfer_year': 'Year', 'rank': 'Rank'}
    )

    # Reverse the y-axis so that rank=1 appears at the top
    fig_race.update_layout(yaxis={'autorange': 'reversed'})

    return fig_race

@app.callback(
    Output('players-foot-bar', 'figure'),
    Input('players-year-slider', 'value')
)
def update_players_foot_bar(year_range):
    min_year, max_year = year_range

    # Filter data for the selected year range (or use full data if you prefer)
    filtered = master_df[(master_df['transfer_year'] >= min_year) &
                         (master_df['transfer_year'] <= max_year)]
    
    filtered = filtered[filtered['transfer_fee'] > 0]
    
    # Group by preferred foot and compute median transfer fee
    foot_median = filtered.groupby('foot')['transfer_fee'].median().reset_index()

    # Determine the appropriate scaling using pick_scale_column based on maximum median fee
    overall_max = foot_median['transfer_fee'].max()
    scale_col, scale_suffix = pick_scale_column(overall_max)

    # Scale the median fee values accordingly
    if scale_col == 'transfer_fee_b':
        foot_median['scaled_median'] = foot_median['transfer_fee'] / 1e9
    elif scale_col == 'transfer_fee_m':
        foot_median['scaled_median'] = foot_median['transfer_fee'] / 1e6
    elif scale_col == 'transfer_fee_t':
        foot_median['scaled_median'] = foot_median['transfer_fee'] / 1e3
    else:
        foot_median['scaled_median'] = foot_median['transfer_fee']

    # Create the bar chart for median fees by preferred foot
    fig = px.bar(
        foot_median,
        x='foot',
        y='scaled_median',
        title=f"Median Transfer Fee by Preferred Foot {scale_suffix}",
        labels={'foot': 'Preferred Foot', 'scaled_median': f"Median Fee {scale_suffix}"}
    )
    return fig

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
