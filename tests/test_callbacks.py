import pandas as pd


# def test_dumbbell():
#     input_data = pd.read_csv("tests/data/dumbbell.csv")
#     graph = cb.plot_dumbbell(mem_data=input_data)


import plotly.graph_objects as go
from plotly import data

import pandas as pd

df = data.gapminder()
df = df.loc[(df.continent == "Europe") & (df.year.isin([1952, 2002]))]

countries = (
    df.loc[(df.continent == "Europe") & (df.year.isin([2002]))]
    .sort_values(by=["lifeExp"], ascending=True)["country"]
    .unique()
)

data = {"line_x": [], "line_y": [], "1952": [], "2002": [], "colors": [], "years": [], "countries": []}

for country in countries:
    data["1952"].extend([df.loc[(df.year == 1952) & (df.country == country)]["lifeExp"].values[0]])
    data["2002"].extend([df.loc[(df.year == 2002) & (df.country == country)]["lifeExp"].values[0]])
    data["line_x"].extend(
        [
            df.loc[(df.year == 1952) & (df.country == country)]["lifeExp"].values[0],
            df.loc[(df.year == 2002) & (df.country == country)]["lifeExp"].values[0],
            None,
        ]
    )
    data["line_y"].extend([country, country, None])
