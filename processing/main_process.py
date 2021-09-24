from process import *
from clean import *
import numpy as np
import pandas as pd
import json
from update_people import *


def get_quotes(df):
    df = clean(df)
    df = process(df)
    return df


if __name__ == "__main__":
    with open("../scraping/scrapped_data.json", "r") as f:
        df = json.load(f)
    df = get_quotes(df)
    jsn = df.to_json(orient="records")  # result is a string
    with open("../data/quotes.json", "w+") as f:
        f.write(jsn)
    with open("../data/universes.json", "r") as f:
        universes = json.load(f)
    quotes = json.loads(jsn)
    new_universes = update_ppl(universes, quotes)
    with open("../data/universes.json", "w") as f:
        json.dump(universes, f, indent=4, sort_keys=True)

