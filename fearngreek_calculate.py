import requests
import json

url = "https://api.alternative.me/fng/?limit="

def fear_day():
    _url = url+"1"
    res = requests.request("GET", _url);
    
    parsed = json.loads(res.text)
    data = parsed["data"]
    
    return data[0]["value"]
                
def fear_yester():
    _url = url+"2"
    res = requests.request("GET", _url);
    
    parsed = json.loads(res.text)
    data = parsed["data"]

    return data[1]["value"]
    
def fear_twodaysago():
    _url = url+"3"
    res = requests.request("GET", _url);
    
    parsed = json.loads(res.text)
    data = parsed["data"]

    return data[2]["value"]

def fear_week():
    _url = url+"7"
    res = requests.request("GET", _url);
    
    parsed = json.loads(res.text)
    data = parsed["data"]
    
    sum = 0
    for index, value in enumerate(data):
        sum += int(value["value"])
        
    return sum/7
    
def fear_month():
    _url = url+"30"
    res = requests.request("GET", _url);
    
    parsed = json.loads(res.text)
    data = parsed["data"]

    sum = 0
    for index, value in enumerate(data):
        sum += int(value["value"])
    
    return sum/30
