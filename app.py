import os
import re
import json
from flask import Flask, request, jsonify, render_template  # Added render_template
from flask_cors import CORS
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig





app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def ensure_list(field):
    """
    Helper function to ensure a field is a list,
    splitting a comma-separated string if necessary.
    """
    if isinstance(field, str):
        return [s.strip() for s in field.split(",") if s.strip()]
    return field


@app.route('/')
def home():
    """
    Serves the main frontend page (index.html).
    """
    return render_template('index.html')


@app.route('/api/recommendation', methods=['POST'])
def get_recommendation():
    """
    Handles career recommendation requests by calling the Vertex AI Gemini model.
    """
    print("Received request at /api/recommendation")
    data = request.json
    interests = data.get('interests', '')
    education = data.get('education', '')
    aptitude = data.get('aptitude', '')

    print(f"User input: Interests={interests}, Education={education}, Aptitude={aptitude}")

    try:
        # On Cloud Run, Vertex AI automatically authenticates using
        # the service account assigned to the service, so no local credentials are needed.
        vertexai.init(project='career-472010', location='us-central1')
        model = GenerativeModel("gemini-2.5-flash")

        # The prompt remains the same as it's designed to guide the model's output.
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
        
        response = model.generate_content(prompt, generation_config=GenerationConfig(response_mime_type="application/json"))
        
        print("Response received from Vertex AI.")

        try:
            recommendation_data = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return jsonify({'error': 'Failed to parse AI model response.'}), 500

        # Ensure bullet point fields are lists for frontend rendering
        recommendation_data['market_value'] = ensure_list(recommendation_data.get('market_value', []))
        recommendation_data['packages'] = ensure_list(recommendation_data.get('packages', []))
        recommendation_data['roadmap'] = ensure_list(recommendation_data.get('roadmap', []))

        return jsonify(recommendation_data)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f"An unexpected server error occurred: {str(e)}"}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles chatbot conversations using the Vertex AI Gemini model.
    """
    data = request.json
    user_message = data.get('message', '')

    try:
        # On Cloud Run, Vertex AI automatically authenticates using
        # the service account assigned to the service.
        vertexai.init(project='career-472010', location='us-central1')
        model = GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        You are a helpful career assistant chatbot. Answer the user's question clearly and simply, without any special characters like asterisks (*), bullet points, or quotes.

        User: {user_message}
        AI:
        """

        response = model.generate_content(prompt, generation_config=GenerationConfig(response_mime_type="text/plain"))
        ai_reply = response.text.strip()

        # Optional cleanup: remove any asterisks if still present
        ai_reply = re.sub(r'\*', '', ai_reply).strip()

        return jsonify({'reply': ai_reply})
    except Exception as e:
        return jsonify({'reply': f"Sorry, an error occurred: {str(e)}"})


if __name__ == '__main__':
    # This block is for local development only and will be ignored by Gunicorn on Cloud Run.
    app.run(debug=True)
