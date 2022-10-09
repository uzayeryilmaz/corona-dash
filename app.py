import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'COVID-19 Dashboard'

death_data = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
confirmed_data = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"


def clean_table(data_source):
    a = pd.read_csv(data_source)
    a = a.drop(columns=["Province/State","Lat","Long"])
    df = a.groupby(a["Country/Region"]).aggregate(["sum"])
    return df


def mine_table(df,start_number = 10, drop_some = True):
    final_table = pd.DataFrame()
    for col_num in range(len(df)):
        row_iter = df.iloc[col_num]
        new_series = pd.Series()
        for x in row_iter:
            if x <= start_number:
                next
            else:
                new_series = new_series.append(pd.Series(x), ignore_index=True)
        if len(new_series) == 0:
            continue
        new_series.name = row_iter.name
        if drop_some:
            if new_series.name in ["Diamond Princess","China"]:
                continue
        final_table = final_table.append(new_series)
    return final_table

def mine_table_per_change(df,start_number = 10, drop_some = True):
    final_table = pd.DataFrame()
    for col_num in range(len(df)):
        row_iter = df.iloc[col_num]
        new_series = pd.Series()
        for x in row_iter:
            if x <= start_number:
                next
            else:
                new_series = new_series.append(pd.Series(x), ignore_index=True)
        if len(new_series) == 0:
            continue
        new_series.name = row_iter.name
        if drop_some:
            if new_series.name in ["Diamond Princess","China"]:
                continue
        final_table = final_table.append(new_series)
    a = final_table.pct_change(axis='columns',fill_method='bfill').drop(columns=final_table.columns[0])*100
    return a.rolling(7,axis='columns').mean().drop(columns=final_table.columns[range(1,7)]).round(2)



def fix_confirmed(df):
    target_slice = [52, 53, 54, 55, 56, 57, 58, 59]
    new_values = [6, 18, 47, 98, 192, 359, 670, 947]
    new_data = pd.Series(data = new_values, index=df.loc["Turkey",df.columns[[target_slice]]].index)
    df.loc["Turkey", df.columns[[target_slice]]] = new_data
    return df


def fix_death(df):
    target_slice = [52, 53, 54, 55, 56, 57, 58, 59]
    new_values = [0, 1, 1, 2, 3, 4, 9, 21]
    new_data = pd.Series(data = new_values, index=df.loc["Turkey",df.columns[[target_slice]]].index)
    df.loc["Turkey", df.columns[[target_slice]]] = new_data
    return df


df_death = fix_death(clean_table(death_data))
df_confirmed = fix_confirmed(clean_table(confirmed_data))
df_death_final = mine_table(df_death,10)
df_confirmed_final = mine_table(df_confirmed,100)
df_death_per_change = mine_table_per_change(df_death,10)
df_confirmed_per_change =mine_table_per_change(df_confirmed,100)


app.layout = html.Div([dcc.Tabs([
    dcc.Tab(label='Deaths', children=[
        dcc.Graph(
            figure={
                'data': [
                    dict(
                        x = df_death_final.columns,
                        y = df_death_final.iloc[i],
                        mode = 'lines',
                        name = df_death_final.iloc[i].name
                        ) for i in range(len(df_death_final))
                        ],
                'layout': dict(
                    yaxis={'type': 'log', 'title': 'Death Count'},
                    xaxis={'title': 'Days after 10th death'},
                    margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                    #legend={'x': 0, 'y': 1},
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            ),
    dcc.Tab(label='Confirmed Cases', children=[
        dcc.Graph(
            figure={
                'data': [
                    dict(
                        x = df_confirmed_final.columns,
                        y = df_confirmed_final.iloc[i],
                        mode = 'lines',
                        name = df_confirmed_final.iloc[i].name
                        ) for i in range(len(df_confirmed_final))
                        ],
                'layout': dict(
                    yaxis={'type': 'log', 'title': 'Case Count'},
                    xaxis={'title': 'Days after 100th case'},
                    margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                    #legend={'x': 0, 'y': 1},
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            ),
    dcc.Tab(label='Death % Change', children=[
        dcc.Graph(
            figure={
                'data': [
                    dict(
                        x = df_death_per_change.columns,
                        y = df_death_per_change.iloc[i],
                        mode = 'lines',
                        name = df_death_per_change.iloc[i].name
                        ) for i in range(len(df_death_per_change))
                        ],
                'layout': dict(
                    yaxis={'title': 'Death Percentage Change (Week Avg)'},
                    xaxis={'title': 'Days after 10th death'},
                    margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                    #legend={'x': 0, 'y': 1},
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            ),
    dcc.Tab(label='Confirmed Cases % Change', children=[
        dcc.Graph(
            figure={
                'data': [
                    dict(
                        x = df_confirmed_per_change.columns,
                        y = df_confirmed_per_change.iloc[i],
                        mode = 'lines',
                        name = df_confirmed_per_change.iloc[i].name
                        ) for i in range(len(df_confirmed_per_change))
                        ],
                'layout': dict(
                    yaxis={'title': 'Confirmed Cases Percentage Change (Week Avg)'},
                    xaxis={'title': 'Days after 100th case'},
                    margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                    #legend={'x': 0, 'y': 1},
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            ),
    dcc.Tab(label='New Confirmed Cases & Deaths', children=[
        dcc.Graph(
            figure={
                'data': [
                    {'x': df_confirmed.diff(axis=1).loc[df_confirmed.sort_values(by= df_confirmed.columns[-1], ascending=False).index[:50],:].index[:50],
                     'y': df_confirmed.diff(axis=1).loc[df_confirmed.sort_values(by= df_confirmed.columns[-1], ascending=False).index[:50],:].iloc[:50,-1],
                     'type': 'bar', 
                     'name': 'New Cases'},
                    {'x': df_confirmed.diff(axis=1).loc[df_confirmed.sort_values(by= df_confirmed.columns[-1], ascending=False).index[:50],:].index[:50],
                     'y': df_death.diff(axis=1).loc[df_confirmed.sort_values(by= df_confirmed.columns[-1], ascending=False).index[:50],:].iloc[:,-1],
                     'type': 'bar', 
                     'name': 'New Deaths'},
                ],
                'layout': dict(
                    yaxis={'type': 'log', 'title': 'Case Count'},
                    xaxis={'title': 'Countries (Sorted by Total Cases)'},
                    margin={'l': 60, 'b': 80, 't': 10, 'r': 10},
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            ),
    dcc.Tab(label='Confirmed Case Progress', children=[
        dcc.Graph(
            figure={
                'data': [
                    dict(
                        x = df_confirmed.iloc[:,-1],
                        y = df_confirmed.diff(axis=1).iloc[:,-7:].mean(1),
                        hovertext  = df_confirmed.index,
                        mode = 'markers',
                        marker={'size': 10},
                        )
                        ],
                'layout': dict(
                    yaxis={'type': 'log','title': 'New Confirmed Cases (In the Past Week)'},
                    xaxis={'type': 'log','title': 'Total Cases'},
                    margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                    hovermode='closest',
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            ),
    dcc.Tab(label='Death Progress', children=[
        dcc.Graph(
            figure={
                'data': [
                    dict(
                        x = df_death.iloc[:,-1],
                        y = df_death.diff(axis=1).iloc[:,-7:].mean(1),
                        hovertext  = df_death.index,
                        mode = 'markers',
                        marker={'size': 10, 'color': '#ff7f0e'},
                        )
                        ],
                'layout': dict(
                    yaxis={'type': 'log','title': 'New Deaths (In the Past Week)'},
                    xaxis={'type': 'log','title': 'Total Deaths'},
                    margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                    hovermode='closest',
                    height= 860
                    )
                    },
            config={'displayModeBar': False}
                )]
            )
            ])
        ])


if __name__ == '__main__':
    app.run_server(
        #host='0.0.0.0'
        debug=True
        )