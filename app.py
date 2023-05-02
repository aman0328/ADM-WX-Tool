import os
import openai
import http.client
from flask import Flask, render_template, request

openai.api_key = os.getenv("OPENAI_API_KEY")

conn = http.client.HTTPSConnection("api.checkwx.com")
payload = ''

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    departure = None
    destination = None
    alternate = None
    time = None
    ceiling = None
    winds = None
    visibility = None
    flightrule = None
    trans1 = None
    trans2 = None
    trans3 = None
    sentiment = None

    if request.method == 'POST':
        departure = request.form['departure']
        destination = request.form['destination']
        alternate = request.form['alternate']
        time = request.form['time']
        ceiling = request.form['ceiling']
        winds = request.form['winds']
        visibility = request.form['visibility']
        flightrule = request.form['flightrule']
        
        url_base = "https://api.checkwx.com/metar/"
        url_departure = url_base + departure
        url_destination = url_base + destination
        url_alternate = url_base + alternate
            
        conn.request("GET", url_departure, payload, {'X-API-Key': '4289ea32e9664cd58e1b191253'})
        res = conn.getresponse()
        input_str = (res.read()).decode('utf-8')
        metar1 = input_str.replace('{"data":["', '').replace('"],"results":1}', '')
            
        conn.request("GET", url_destination, payload, {'X-API-Key': '4289ea32e9664cd58e1b191253'})
        resDest = conn.getresponse()
        destination_str = (resDest.read()).decode('utf-8')
        metar2 = destination_str.replace('{"data":["', '').replace('"],"results":1}', '')
            
        conn.request("GET", url_alternate, payload, {'X-API-Key': '4289ea32e9664cd58e1b191253'})
        resAlt = conn.getresponse()
        alternate_str = (resAlt.read()).decode('utf-8')
        metar3 = alternate_str.replace('{"data":["', '').replace('"],"results":1}', '')

        # Add code to retrieve METARs and perform calculations using the user input data
        if metar1:
            metar_translation1 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(metar1),
                    temperature=0.4,
                    max_tokens=1000 
                    )
            trans1 = metar_translation1.choices[0].text.strip()

            if metar2:
                metar_translation2 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(metar2),
                    temperature=0.4,
                    max_tokens=1000 
                    )
                trans2 = metar_translation2.choices[0].text.strip()
        
            if metar3:
                metar_translation3 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(metar3),
                    temperature=0.4,
                    max_tokens=1000 
                    )
                trans3 = metar_translation3.choices[0].text.strip()    
        
        
        senti = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages= [
                    {"role": "user", "content": generate_sentiment(departure, destination, alternate, metar1, metar2, metar3, time, ceiling, winds, visibility, flightrule)}
                ]
                )
        
        sentiment = senti.choices[0].message
        

    return render_template('index.html', departure=departure, destination=destination, alternate=alternate,
                           time=time, ceiling=ceiling, winds=winds, visibility=visibility, flightrule=flightrule, trans1 = trans1,
                           trans2=trans2, trans3=trans3, sentiment=sentiment)


def generate_prompt(metar):
    return f"""Translate the given METAR into its expanded form: METAR: KBNA 260053Z 07004KT 
10SM BKN250 17/01 A3008 RMK AO2 SLP185 T01670011\n
Translation: KBNA (Nashville International Airport), Date and Time: 260053Z, Wind: 070 degrees 
at 4 knots (07004KT), Visibility: 10 statute miles (10SM), Clouds: Broken at 25,000 feet (BKN250), 
Temperature and Dew Point: 17°C and 1°C, respectively (17/01), Altimeter setting: 30.08 inches of 
mercury (A3008), Remarks: Automated station with a precipitation discriminator (RMK AO2), sea 
level pressure of 1018.5 hPa (SLP185), temperature of 16.7°C and dew point of 11.1°C .\n  
\n METAR:{metar} Translation: """

def generate_sentiment(departure, destination, alternate, metar1, metar2, metar3, time, ceiling, winds, visibility, flightrule):
    return "Decide the sentiment of a pilot flying from" + departure + " with weather " + metar1 + "to" + destination + "with weather" + metar2 + "with an alternate at" + alternate + "with weather " + metar3 + ". The pilot has" + time + " hours and is " + flightrule + " rated.  The pilot has a personal minimum of " + winds + " kias maximum wind, and mimumum " + ceiling + " foot ceilings as well as minimum" + visibility + "miles visibility. It is okay to push some minimums set by the pilot by a small margin, however if there are more than one category of minimums pushed, that should be reconsidered.  Decide on a sentiment whether the pilot should conduct this trip or not and why."


''''

@app.route('/secondform', methods=['POST'])
def secondform():
    departure = request.form['departure']
    destination = request.form['destination']
    alternate = request.form['alternate']
    time = request.form['time']
    ceiling = request.form['ceiling']
    winds = request.form['winds']
    visibility = request.form['visibility']
    flightrule = request.form['flightrule']

    # Add code to perform calculations using the user input data and generate the AI sentiment

    return render_template('secondform.html', )


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'departure' in request.form and 'destination' in request.form and 'alternate' in request.form:
            departure = request.form['departure']
            destination = request.form['destination']
            alternate = request.form['alternate']
            
            url_base = "https://api.checkwx.com/metar/"
            headers = {'X-API-Key': '4289ea32e9664cd58e1b191253'}

            metartrans1, metartrans2, metartrans3 = "", "", ""

            responseDep = request.get(url_base + departure, headers=headers).json()
            responseDest = request.get(url_base + destination, headers=headers).json()
            responseAlt = request.get(url_base + alternate, headers=headers).json()

            if responseDep['data']:
                print("working")
            metar_translation1 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(responseDep['data'][0]),
                    temperature=0.4,
                    max_tokens=1000
                )
                metartrans1 = metar_translation1.choices[0].text.strip()
                

            if responseDest['data']:
                metar_translation2 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(responseDest['data'][0]),
                    temperature=0.4,
                    max_tokens=1000
                )
                metartrans2 = metar_translation2.choices[0].text.strip()

            if responseAlt['data']:
                metar_translation3 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(responseAlt['data'][0]),
                    temperature=0.4,
                    max_tokens=1000
                )
                metartrans3 = metar_translation3.choices[0].text.strip()
                
                
            return jsonify({'result': 'success', 'departure': departure, 'destination': destination, 'alternate': alternate, 'metartrans1': metartrans1, 'metartrans2': metartrans2, 'metartrans3': metartrans3})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/", methods=("GET", "POST"))
def index():

    
    if request.method == "POST":
        departure = request.form["departure"]
        destination = request.form["destination"]
        alternate = request.form["alternate"]
        time = request.form.get["time"]
        ceiling = request.form.get["ceiling"]
        winds = request.form.get["winds"]
        visibility = request.form.get["visibility"]
        flightrule = request.form.get["flightrule"]
        
        if departure and destination and alternate and not time:
            url_base = "https://api.checkwx.com/metar/"
            url_departure = url_base + departure
            url_destination = url_base + destination
            url_alternate = url_base + alternate
            
            conn.request("GET", url_departure, payload, {'X-API-Key': '4289ea32e9664cd58e1b191253'})
            res = conn.getresponse()
            input_str = (res.read()).decode('utf-8')
            responseDep = input_str.replace('{"data":["', '').replace('"],"results":1}', '')
            
            conn.request("GET", url_destination, payload, {'X-API-Key': '4289ea32e9664cd58e1b191253'})
            resDest = conn.getresponse()
            destination_str = (resDest.read()).decode('utf-8')
            responseDest = destination_str.replace('{"data":["', '').replace('"],"results":1}', '')
            
            conn.request("GET", url_alternate, payload, {'X-API-Key': '4289ea32e9664cd58e1b191253'})
            resAlt = conn.getresponse()
            alternate_str = (resAlt.read()).decode('utf-8')
            responseAlt = alternate_str.replace('{"data":["', '').replace('"],"results":1}', '')
            
            if responseDep:
                metar_translation1 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(responseDep),
                    temperature=0.4,
                    max_tokens=1000 
                    )
                metartrans1 = metar_translation1.choices[0].text.strip()

            if responseDest:
                metar_translation2 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(responseDest),
                    emperature=0.4,
                    max_tokens=1000 
                    )
                metartrans2 = metar_translation2.choices[0].text.strip()
        
            if responseAlt:
                metar_translation3 = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=generate_prompt(responseAlt),
                    temperature=0.4,
                    max_tokens=1000 
                    )
                metartrans3 = metar_translation3.choices[0].text.strip()
                
                return render_template("second_form.html", departure=departure, destination=destination, alternate=alternate)
            
        if departure and destination and alternate and time and ceiling and winds and visibility and flightrule:
            
            decision_sentiment = openai.Completion.create(
                model="text-davinci-003",
                prompt=generate_prompt(responseDep),
                temperature=0.4,
                max_tokens=1000
                )
            
            decision = decision_sentiment.choices[0].text.strip()
            
            return redirect(url_for("index", departure=responseDep, destination=responseDest, 
                                alternate=responseAlt, trans1=metartrans1, trans2=metartrans2, 
                                trans3=metartrans3, time=time, ceiling=ceiling, winds=winds, 
                                visibility=visibility, flightrule=flightrule))
    
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    alternate = request.args.get("alternate")
    trans1 = request.args.get("trans1")
    trans2 = request.args.get("trans2")
    trans3 = request.args.get("trans3")
    time = request.args.get("time")
    ceiling = request.args.get("ceiling")
    winds = request.args.get("winds")
    visibility = request.args.get("visibility")
    flightrule = request.args.get("flightrule")
    
    
    return render_template("index.html", departure=departure, destination=destination, 
                           alternate=alternate, trans1=trans1, trans2=trans2, 
                           trans3=trans3, time=time, ceiling=ceiling, winds=winds, 
                                visibility=visibility, flightrule=flightrule)

def generate_prompt(metar):
    return f"""Translate the given METAR into its expanded form: METAR: KBNA 260053Z 07004KT 
10SM BKN250 17/01 A3008 RMK AO2 SLP185 T01670011\n
Translation: KBNA (Nashville International Airport), Date and Time: 260053Z, Wind: 070 degrees 
at 4 knots (07004KT), Visibility: 10 statute miles (10SM), Clouds: Broken at 25,000 feet (BKN250), 
Temperature and Dew Point: 17°C and 1°C, respectively (17/01), Altimeter setting: 30.08 inches of 
mercury (A3008), Remarks: Automated station with a precipitation discriminator (RMK AO2), sea 
level pressure of 1018.5 hPa (SLP185), temperature of 16.7°C and dew point of 11.1°C .\n  
\n METAR:{metar} Translation: """

def generate_sentiment(metar1, metar2, metar3, time, ceiling, winds, visibility, flightrule):
    return f
'''