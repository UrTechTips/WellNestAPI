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
port = os.environ.get("PORT")
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
def dailyTip():
    data = request.json  
    cityName = data.get('cityName')
    temp = round(data.get('temp') - 273.15)  # Converted to Celsius
    humidity = data.get('humidity')
    mood = data.get('mood')
    activities = ' '.join(data.get('activities', []))
    weatherDescription = data.get('weatherDescription')
    
    # Optimized Prompt
    prompt = (
        f"In {cityName}, it's currently {temp}°C with {humidity}% humidity and '{weatherDescription}' conditions. "
        f"The user's mood today is {mood} after activities like {activities}. "
        f"Provide a wellness tip on hydration, suitable clothing, or any well-being advice for these conditions."
    )
    
    response = model.generate_content(prompt)
    response_dict = json.loads(response.text)
    return jsonify({"status": 200, "message": response_dict})  

@app.route("/getWeeklyTip", methods=['POST'])
@cross_origin()
def weeklyTip():
    data = request.json  
    moods = data.get('moods', {})
    activities = data.get('activities', {})
    
    mood_summary = ' '.join([f"Mood on {day}: {mood}" for day, mood in moods.items()])
    activity_summary = ' '.join([f"Activities on {day}: {' '.join(day_activities)}" for day, day_activities in activities.items()])
    
    prompt = (
        f"Based on the user's weekly report, summarize wellness advice. "
        f"Mood summary: {mood_summary}. Activity summary: {activity_summary}. "
        f"Provide a wellness tip to support mental well-being, suggest physical activities, and offer guidance on lifestyle habits."
    )
    
    response = model.generate_content(prompt)
    response_dict = json.loads(response.text)
    return jsonify({"status": 200, "message": response_dict})  

if __name__ == "__main__":
    app.run(port=port)