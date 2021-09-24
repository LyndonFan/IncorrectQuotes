import streamlit as st
import json, re, time, os
import numpy as np
import pandas as pd

BASE_PATH = "/Users/lyndonf/Desktop/IncorrectQuotesGenerator"


def show_quote(q, is_html=False):
    if is_html:
        st.write(q, unsafe_allow_html=True)
    else:
        for line in q.split("\n"):
            st.text(line)


@st.cache
def load_data():
    with open(os.path.join(BASE_PATH, "data/quotes.json"), "r") as f:
        quotes = json.load(f)
    with open(os.path.join(BASE_PATH, "data/sources.json"), "r") as f:
        sources = json.load(f)
    with open(os.path.join(BASE_PATH, "data/universes.json"), "r") as f:
        universes = json.load(f)
    return quotes, sources, universes
