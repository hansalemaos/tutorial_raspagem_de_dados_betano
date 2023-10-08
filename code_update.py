# pip install selenium seleniumbase PrettyColorPrinter a-selenium2df
import re
from collections import defaultdict
from seleniumbase import Driver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
import numpy as np

add_printer(1)


def obter_dataframe(query="*"):
    df = pd.DataFrame()
    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector=query,
            with_methods=True,
        )
    return df


driver = Driver(uc=True)
driver.get("https://br.betano.com/sport/futebol/brasil/brasileirao-serie-a/10016/")
df = obter_dataframe(query="section")
texto = df.loc[
    df.aa_className.str.contains("grid__column", regex=False, na=False)
].aa_innerText.iloc[0]
df = pd.DataFrame(texto.splitlines())
df = df.loc[
    df.loc[
        df[0].str.contains(r"Brasileirão\s+-\s+Série\s+A", regex=True, na=False)
    ].index[-1]
    + 1 :
].reset_index(drop=True)
df[0] = df[0].str.strip()
allbets = np.array_split(df, df.loc[df[0].str.contains(r"^\d\d/\d\d$")].index)
d = defaultdict(list)
for bet in allbets:
    d[len(bet)].append(bet)
df = pd.concat(
    [q.reset_index(drop=True) for q in d[sorted(d)[-1]]], axis=1, ignore_index=True
)
# para tirar o SO de jogos ao vivo 
try:
    df=df.loc[np.setdiff1d(df.index,df[df=='SO'].dropna().index)].reset_index(drop=True)
except Exception:
    pass 
df = df.loc[
    np.setdiff1d(
        df.index,
        df.applymap(lambda x: re.match("resultado|total|ambas", x, flags=re.I))
        .dropna(how="all")
        .index,
    )
].reset_index(drop=True)[:7]
df = df.T
df.columns = ["data", "hora", "team1_nome", "team2_nome", "team1", "empate", "team2"]
df = df.astype({"team1": "Float64", "empate": "Float64", "team2": "Float64"})
