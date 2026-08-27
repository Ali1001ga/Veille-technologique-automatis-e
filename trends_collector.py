from pytrends.request import TrendReq
pytrend = TrendReq()
keywords = ["Python", "Docker", "AWS"]
pytrend.build_payload(kw_list=keywords, geo='MA')
data = pytrend.interest_over_time()
print(data)
data.to_csv("trends_morocco.csv")

pytrend.build_payload(kw_list=keywords, geo='FR')
data_fr = pytrend.interest_over_time()
data_fr.to_csv("trends_france.csv")