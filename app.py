import os
import re
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig

load_dotenv()

app = Flask(__name__)
CORS(app)

def ensure_list(field):
    if isinstance(field, str):
        return [s.strip() for s in field.split(",") if s.strip()]
    return field

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/recommendation', methods=['POST'])
def get_recommendation():
    print("Received request at /api/recommendation")
    data = request.json
    interests = data.get('interests', '')
    education = data.get('education', '')
    aptitude = data.get('aptitude', '')

    print(f"User input: Interests={interests}, Education={education}, Aptitude={aptitude}")

    try:
        # RENDER ALREADY SETS THE GOOGLE_APPLICATION_CREDENTIALS ENVIRONMENT VARIABLE.
        # THIS LINE WAS CONFLICTING WITH IT AND CAUSING THE ERROR.
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        #     os.getcwd(), 'gcloud-credentials.json'
        # )

        vertexai.init(project='career-472010', location='us-central1')
        model = GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are a comprehensive career and skills advisor for Indian college students. Your task is to generate a detailed, actionable career guide based on a user's profile.

        User Profile:
        - Interests: {interests}
        - Education: {education}
        - Aptitude: {aptitude}

        Generate a complete career roadmap including these sections as bullet points (lists), not paragraphs:
        1. Personal Profile
        2. Academic Background
        3. Aptitude & Skills
        4. Projects/Achievements (if available)
        5. Recommendations for improvement

        Also, include these fields as bullet point lists only, without quotes or star symbols:
        - packages (named in multiple languages as bullet points)
        - market_value (bullet points)
        - roadmap (bullet points)
        Generate a detailed step-by-step career roadmap with estimated timelines for each step.
        Example format for each step: "Within 3 months: Learn SQL and Python fundamentals.

        For important company names or any key entity, wrap the names with <span class='important'>...</span> tags to indicate they need special styling in the frontend.
         You are a career advisor. Provide a detailed step-by-step roadmap with explicit timelines.

        Example format for each step:
        - "Month 1-3: Learn Python and SQL basics."
        - "Months 4-6: Build projects and gain internship experience."

        Output the roadmap as a list of strings with timelines included clearly.
        Output must be a single JSON object with the following schema:

        {{
            "profile_bullets": [ "string", "string", ... ],
            "recommended_career": "string",
            "roadmap": [ "string", "string", ... ],
            "required_skills": [ "string", "string", ... ],
            "companies": [ {{ "name": "string", "type": "string" }} ],
            "course_guidance": [ {{ "title": "string", "platform": "string", "link": "string", "paid_or_free": "string" }} ],
            "market_value": [ "string", "string", ... ],
            "packages": [ "string", "string", ... ]
        }}

        Ensure no quotes, stars, or additional symbols decorate the list items.
        """

        print("Sending request to Vertex AI with gemini-2.5-flash...")
        response = model.generate_content(prompt, generation_config=GenerationConfig(response_mime_type="application/json"))
        print("Response received from Vertex AI.")

        try:
            recommendation_data = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return jsonify({'error': 'Failed to parse AI model response.'}), 500

        recommendation_data['market_value'] = ensure_list(recommendation_data.get('market_value', []))
        recommendation_data['packages'] = ensure_list(recommendation_data.get('packages', []))
        recommendation_data['roadmap'] = ensure_list(recommendation_data.get('roadmap', []))

        return jsonify(recommendation_data)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f"An unexpected server error occurred: {str(e)}"}), 500


# ----------- Updated Chatbot API Endpoint -------------

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    try:
        # RENDER ALREADY SETS THE GOOGLE_APPLICATION_CREDENTIALS ENVIRONMENT VARIABLE.
        # THE PREVIOUS CODE WAS CONFLICTING WITH IT AND CAUSING THE ERROR.

        vertexai.init(project='career-472010', location='us-central1')
        model = GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are a helpful career assistant chatbot. Answer the user's question clearly and simply, without any special characters like asterisks (*), bullet points, or quotes.

        User: {user_message}
        AI:
        """

        response = model.generate_content(prompt, generation_config=GenerationConfig(response_mime_type="text/plain"))
        ai_reply = response.text.strip()

        ai_reply = re.sub(r'\*', '', ai_reply).strip()

        return jsonify({'reply': ai_reply})
    except Exception as e:
        return jsonify({'reply': f"Sorry, an error occurred: {str(e)}"})
