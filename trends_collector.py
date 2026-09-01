from pytrends.request import TrendReq
import pandas as pd
import time

pytrend = TrendReq()

KEYWORD_GROUPS = [
    ["Python", "Docker", "AWS", "Kubernetes", "SQL"],
    ["DevOps", "Machine Learning", "Cybersecurity", "Cloud", "React"]
]

def fetch_trends(geo):
    frames = []
    for group in KEYWORD_GROUPS:
        pytrend.build_payload(kw_list=group, geo=geo)
        result = pytrend.interest_over_time()
        if "isPartial" in result.columns:
            result = result.drop(columns=["isPartial"])
        frames.append(result)
        time.sleep(10)
    return pd.concat(frames, axis=1)

fetch_trends("MA").to_csv("trends_morocco.csv")
fetch_trends("FR").to_csv("trends_france.csv")
print("Saved trends for 10 keywords")