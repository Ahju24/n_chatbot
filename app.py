from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(force=True)
    session = req.get("session")
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    if intent == "Welcome_Neutral":
        
        context_name = f"welcome-followup"

        response_text = (
            f"Hello! I’d love to help you choose an outfit. "
            "First, where are you headed today? Options: Job interview, date, lecture"
        )

        return jsonify({
            "fulfillmentText": response_text,
            "outputContexts": [
                {
                    "name": f"{session}/contexts/{context_name}",
                    "lifespanCount": 5
                }
            ]
        })


    elif intent == "SelectEventIntent":
        event_param = parameters.get("Event", "")
        event = event_param[0].lower() if isinstance(event_param, list) else event_param.lower()


        valid_events = ["job interview", "date", "lecture"]
        if event not in valid_events:
            return jsonify({
                "fulfillmentText": (
                    "I'm sorry, I didn't catch that. Please choose one of the following events: "
                    "job interview, date, lecture."
                ),
                "outputContexts": req.get("queryResult", {}).get("outputContexts", [])
            })


        response_text = f"Great choice! We'll get you ready for your {event}. What's the weather like today? Options: Season (summer/winter) and temperature (cold, warm, hot)"

        return jsonify({
            "fulfillmentText": response_text,
            "outputContexts": [
                {
                    "name": f"{session}/contexts/weather-followup",
                    "lifespanCount": 5,
                    "parameters": {
                        "Event": event
                    }
                }
            ]
        })


    elif intent == "WeatherIntent":
        season = parameters.get("Season", "").lower()
        temperature = parameters.get("Temperature", "").lower()

        response_text = f"Got it — a {temperature} {season} day. Thanks for the information! Do you have one favorite color you'd like me to consider?"

        return jsonify({
            "fulfillmentText": response_text
        })


    elif intent == "ColorPreferenceIntent":
        raw_color = parameters.get("Color", "")
        color = raw_color.lower() if raw_color else ""

        # Retrieve from previous context
        event = ""
        temperature = ""
        season = ""
        for context in req.get("queryResult", {}).get("outputContexts", []):
            if "weather-followup" in context["name"]:
                event = context.get("parameters", {}).get("Event", "")
                temperature = context.get("parameters", {}).get("Temperature", "")
                season = context.get("parameters", {}).get("Season", "")
                break

        if not color or color in ["no", "none"]:
            response_text = (
                "Alright, no problem! Do you have any clothing type preferences? "
                "Options: formal or casual"
            )
        else:
            response_text = (
                f"Thanks! I’ll keep {color} in mind when recommending your outfit. "
                "Do you have any clothing type preferences? Options: formal or casual"
            )


        return jsonify({
            "fulfillmentText": response_text,
            "outputContexts": [
                {
                    "name": f"{session}/contexts/color-followup",
                    "lifespanCount": 5,
                    "parameters": {
                        "Color": color,
                        "Event": event,
                        "Temperature": temperature,
                        "Season": season
                    }
                }
            ]
        })


    elif intent == "ClothingTypeIntent":
        clothing_type = parameters.get("ClothingType", "").lower()

        color = ""
        event = ""
        temperature = ""
        season = ""
        outfit = ""

        for context in req.get("queryResult", {}).get("outputContexts", []):
            if "color-followup" in context["name"]:
                color = context.get("parameters", {}).get("Color", "")
                event = context.get("parameters", {}).get("Event", "")
                temperature = context.get("parameters", {}).get("Temperature", "")
                season = context.get("parameters", {}).get("Season", "")
                break

        # Tailored outfit suggestions for formal and casual
        if clothing_type == "formal":
            outfit = f"a {color} shirt with dress trousers and classic shoes"
        elif clothing_type == "casual":
            outfit = f"a comfy {color} t-shirt with denim jeans and sneakers"


        # Compose return link (assuming you store pid in session or from query param)
        pid = request.args.get('pid', 'missingPID')  # or fetch it another way
        survey_link = f"https://www.soscisurvey.de/seminar19/?r=return&pid={pid}"

        # Compose summary + recommendation
        response_text = (
            f"Thanks for sharing all your preferences!\n\n"
            f"Based on what you've told me, I’d recommend {outfit} — perfect for a {temperature} {season} {event}.\n"
            f"I hope it matches your style!\n\n"
            f"To complete your experience, please click the button on the top to return to the survey.\n"
        )

        #Shorter answer
        #f"{title}, I recommend {outfit} for your {temperature} {season} {event}.\n\n"

        # Return both text and payload
        return jsonify({
            "fulfillmentText": response_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [response_text]
                    }
                },
                {
                    "payload": {
                        "type": "return_link"
                    }
                }
            ]
        })

    elif intent == "ClosingIntent":
        # Compose return link (assuming you store pid in session or from query param)
        pid = request.args.get('pid', 'missingPID')  # or fetch it another way
        survey_link = f"https://www.soscisurvey.de/seminar19/?r=return&pid={pid}"

        response_text = (
            "You're very welcome! If you haven't already, please feel free to complete our quick follow-up survey. "
            f"Have a great day!"
        )

        return jsonify({
            "fulfillmentText": response_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [response_text]
                    }
                },
                {
                    "payload": {
                        "type": "return_link"
                    }
                }
            ]
        })

    # Default fallback
    return jsonify({"fulfillmentText": "I'm not sure how to help with that."})


#if __name__ == '__main__':
#   app.run(port=5000)
