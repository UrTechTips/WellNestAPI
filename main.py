from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api_key = os.environ.get("GEN_AI_KEY")
genai.configure(api_key=api_key)  
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type=content.Type.OBJECT,
    required=["summary", "properties"],
    properties={
      "summary": content.Schema(
        type=content.Type.STRING,
      ),
      "properties": content.Schema(
        type=content.Type.OBJECT,
        required=["hydration", "clothing", "food", "others"],
        properties={
          "hydration": content.Schema(
            type=content.Type.STRING,
          ),
          "clothing": content.Schema(
            type=content.Type.STRING,
          ),
          "food": content.Schema(
            type=content.Type.STRING,
          ),
          "others": content.Schema(
            type=content.Type.STRING,
          ),
        },
      ),
    },
  ),
  "response_mime_type": "application/json",
}
model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)


@app.route("/getTip", methods=['POST'])
@cross_origin()
def index():
        data = request.json  
        cityName = data.get('cityName')
        temp = data.get('temp')
        humidity = data.get('humidity')
        weatherDescription = data.get('weatherDescription')
        prompt = f'Given the weather in {cityName} where the temperature is {round(temp - 273.15)}°C and humidity is {humidity}%, and the condition is "{weatherDescription}", generate a wellness tip for staying healthy today. The tip should focus on hydration, clothing recommendations, or any other factors related to well-being in this kind of weather.'
        
        response = model.generate_content(prompt)
        # temp = '{"properties": {"clothing": "Opt for light-colored and loose-fitting clothes to stay cool and comfortable in the haze.", "food": "Keep yourself hydrated with plenty of water, coconut water, and fresh fruits.", "hydration": "Drink plenty of fluids throughout the day to stay hydrated, especially with the humidity.", "others": "Avoid strenuous activities during the hottest parts of the day and take breaks in shaded areas."}, "summary": "With the haze and humidity, focus on staying hydrated by drinking plenty of fluids. Light and loose clothing will keep you comfortable, and its best to avoid strenuous activity during the hottest parts of the day."}'
        response_dict = json.loads(response.text)
        return jsonify({"status": 200, "message": response_dict})  

if __name__ == "__main__":
    app.run(port=8080, debug=True)