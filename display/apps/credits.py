import streamlit as st
import pandas as pd
import numpy as np
import json, re, time
import os

from apps.commonFunctions import show_quote, load_data


def show_sources(sources):
    st.title("Tumblr Incorrect Quotes")
    st.write(
        "I own NONE of the quotes shown. I have scrapped them from various tumblr pages."
    )
    st.markdown("Please contact me if you want to remove your page's quotes.")
    st.write("Here are the pages in no particular order:")
    df = pd.DataFrame(sources)
    titles = df.universe.unique()
    st.title("Generic / Templates")
    st.markdown("\n".join(f"- {u}" for u in df[df.universe == "Generic"].url))
    for t in titles:
        if t == "Generic":
            continue
        st.title(t)
        st.markdown("\n".join(f"- {u}" for u in df[df.universe == t].url))


def app():
    show_sources(load_data()[1])
