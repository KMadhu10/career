
# Career Goals Web App

A student career guidance platform that provides personalized career plans and recommendations using Google Cloud Vertex AI (Gemini), Flask API backend, and a modern, responsive web frontend.

## Features

- Student profile input and chat-based guidance
- Personalized career recommendations powered by Generative AI (Gemini 2.5 Flash)
- REST API backend using Flask for recommendations and chat endpoints
- Modern web frontend built with HTML, Tailwind CSS, and JavaScript
- Containerized and serverless deployment on Google Cloud Run / App Engine

 ## Architecture


Student (User)
      |
Frontend (HTML/Tailwind/JS)
      |
Backend (Flask API)
      |
Vertex AI (Gemini)
      |
Deployment (Cloud Run/App Engine)


## Setup Instructions

1. Arranging the all necessary files with the proper structure and api initiations with the required imports

2. Install dependencies
   
   pip install -r requirements.txt
   npm install        # If using frontend build tools
   

3. Set up Google Cloud credentials
   - Create a project and service account in Google Cloud Console
   - Enable Vertex AI API
   - Download service account JSON and set environment variable:
     
     export GOOGLE_APPLICATION_CREDENTIALS="your-service-account.json"
     

4. Run Flask backend
   
   python main.py
   

   Deploy to Google Cloud SDK
   - Use Dockerfile for containerization
   - Follow Google Cloud deployment guides

## Folder Structure



├── backend/

│   ├── app.py

│   ├── requirements.txt

├── frontend/

│   ├── index.html(Tailwind,js)

├── deploy/

│   ├── Dockerfile

│   ├── cloud_run.yaml

├── README.md


## Technologies Used

- Flask (Python)
- HTML, Tailwind CSS, JavaScript
- Google Cloud Vertex AI (Gemini)
- Google Cloud Run / App Engine



## License

MIT


Live Server Link:https://careergoals-1074185916996.asia-south1.run.app/
