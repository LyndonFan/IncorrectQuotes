import streamlit as st
import pandas as pd
import numpy as np
import json, re, time
import os
from apps import home, credits
from multiapp import MultiApp

BASE_PATH = "/Users/lyndonf/Desktop/IncorrectQuotesGenerator"

app = MultiApp()
app.add_app("Home", home.app)
app.add_app("Credits", credits.app)


app.run()
