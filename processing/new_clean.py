from typing import Any, List, Optional, Dict
import pandas as pd
import re, json


def correct_spellings(txt: str) -> str:
    for cor in REPLACEMENTS:
        for mis in REPLACEMENTS[cor]:
            txt = txt.replace(mis, cor)
    return txt


# drops formatting
def npf_to_quote(npf: List[Dict[str, Any]]) -> str:
    return "\n".join(r["text"] for r in npf)


def is_quote(q: str) -> bool:
    return (len(q) - q.count("\n")) / (q.count("\n") + 1) < 500 and (bool)(
        re.search("^((\*[^\n]+\*|\[[^\n]+\]|[A-Za-z0-9][^\n:]*:[^\n]*)(\n|))+$", q)
    )
    # check for each line, the only colon should NOT be inside parenthesis


def clean(df: Any) -> pd.DataFrame:
    if type(df) is not pd.DataFrame:
        df = pd.DataFrame(df)
    df = df[
        [(not any((bool)(re.search("^not.*quote$", t)) for t in ts)) for ts in df.tags]
    ]
    df["quote"] = df["content"].apply(npf_to_quote)
    df = df[df["quote"].apply(is_quote)]
    return df
