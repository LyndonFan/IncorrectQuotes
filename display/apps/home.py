import streamlit as st
import pandas as pd
import numpy as np
import json, re, time
import os

from apps.commonFunctions import show_quote, load_data


@st.cache(suppress_st_warning=True)
def select_quote(quotes, index):
    curr_quote = quotes[index]
    return curr_quote


def customize_quote(curr_quote):
    num_ppl = curr_quote["num_ppl"]
    new_ppl = [st.text_input(f"Person {i+1}: ") for i in range(num_ppl)]
    temp_quote = curr_quote["quote"]
    for i in range(num_ppl):
        if new_ppl[i] == "":
            new_ppl[i] = "Person " + str(i + 1)
        temp_quote = temp_quote.replace("{" + str(i) + "}", new_ppl[i])
    show_quote(temp_quote)
    st.write("Source: " + curr_quote["url"])
    show_original = st.checkbox("Show me the original!")
    if show_original:
        show_quote(curr_quote["raw"], True)
    st.write("Full info (can expand / collapse)")
    st.write(curr_quote)


def app():
    st.title("Tumblr Incorrect Quotes")
    quotes = load_data()[0]
    index = st.slider("Index bar", 0, len(quotes) - 1)
    quote = select_quote(quotes, index)
    customize_quote(quote)
