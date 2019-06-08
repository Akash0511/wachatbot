import os
import requests
import pyowm
import json
import datetime
import wikipedia
import urllib.request
from db import insertdata,get_time
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "chatbot.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "chatbot-xwsujg"

from gnewsclient import gnewsclient

client = gnewsclient.NewsClient(max_results=3)

def get_news(parameters):
    print(parameters)
    client.topic = parameters.get('news_type')
    client.language = parameters.get('language')
    client.location = parameters.get('geo-country','')
    return client.get_news()

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg, session_id):
    response = detect_intent_from_text(msg, session_id)
    if response.intent.display_name == 'get_news':
        news = get_news(dict(response.parameters))
        news_str = 'Here is your news:'
        for row in news:
            news_str += "\n\n{}\n\n{}\n\n".format(row['title'],
            row['link'])
        return news_str,'',''
    elif response.intent.display_name=='get_weather':
        owm = pyowm.OWM("2242ac01869a406a63e2cf1f430724ef")
        weather=dict(response.parameters)
        city=weather.get("geo-city")
        country=weather.get("geo-country")
        if country!='':
            observation = owm.weather_at_place(city+','+country)
        else:
            observation = owm.weather_at_place(city+',india')
        w = observation.get_weather()
        wind = w.get_wind()['speed']
        humidity=w.get_humidity()
        temprature=w.get_temperature('celsius')['temp']
        status=w.get_detailed_status()
        userdata={'geo-city':city,'geo-country':country,'time':get_time()}
        insertdata(userdata)
        weather="\nstatus: {}\n".format(status)
        weather+="\ntemprature: {} °c\n".format(temprature)
        weather+="\nhumidity : {}\n".format(humidity)
        weather+="\nwind speed: {}\n".format(wind)
        return weather,'',''

    elif response.intent.display_name=='get_lyrics':
        info=dict(response.parameters)
        artist=info.get('music-artist')
        title=info.get('song_name')
        URL="https://api.lyrics.ovh/v1/"+artist+"/"+title
        request=requests.get(URL)
        content_data=request.json()
        if 'error' in content_data.keys():
            return "No Lyrics Available"
        else:
            userdata={'artist':artist,'title':title,'time':get_time()}
            insertdata(userdata)
            #print(content_data)
            return content_data['lyrics'][:1500],'',''

    elif response.intent.display_name=="get_meaning":
        dictionary=dict(response.parameters)
        app_id="230078d5"
        app_key="52e933da09c08cfc07c21ad20a32b412"
        endpoint = "entries"
        language_code = "en-us"
        word_id =dictionary.get('word')
        url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()
        r = requests.get(url, headers = {"app_id": app_id, "app_key": app_key})
        content_data=r.json()
        if len(content_data)!=0:
            data="Meaning of {} is {}\n".format(word_id,content_data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0])
            userdata = {'word_id':word_id, 'time':get_time()}
            insertdata(userdata)
            return data,'',''
        else:
            return "No meaning found for this word"

    elif response.intent.display_name=="get_image":
        image_data=dict(response.parameters)
        image=image_data.get('image_type')
        data=wikipedia.summary(image, sentences=2)
        page_image = wikipedia.page(image).images[0]
        return data,page_image,"image"
    else:
        return response.fulfillment_text,'',''
