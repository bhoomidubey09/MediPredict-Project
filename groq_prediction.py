import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Check your .env file or deployment environment variables.")



system_message = None

def initialize_groq_system():
    global system_message
    print("📚 Loading datasets...")
    # Load symptom-disease dataset
    # with open("models/disease_data.txt",'r') as file:
    #     symptoms_data = file.read()
    # with open("models/severity_data.txt",'r') as file:
    #     severity_data = file.read()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    disease_file = os.path.join(BASE_DIR, "models", "disease_data.txt")
    severity_file = os.path.join(BASE_DIR, "models", "severity_data.txt")

    with open(disease_file, "r", encoding="utf-8") as file:
        symptoms_data = file.read()

    with open(severity_file, "r", encoding="utf-8") as file:
        severity_data = file.read()
    system_message = f"""You are an expert medical AI assistant specialized in disease prediction.

**DISEASE-SYMPTOM DATABASE:**
{symptoms_data}

**SYMPTOM SEVERITY WEIGHTS:**
{severity_data}

**YOUR ROLE:**
1. Analyze user's symptoms
2. Match with diseases from database
3. Calculate confidence scores (0-100) for top 5 diseases
4. Calculate severity score using symptom weights
5. Generate medical recommendations

**IMPORTANT RULES:**
- Base predictions ONLY on provided database
- Be realistic with confidence scores
- Severity = (sum of symptom weights / max possible weight) × 100
- according to Severity give Urgency level like Normal, Moderate or high and Risk Level and Action like consult doctor
- Provide practical, helpful recommendations in short 2 lines.

**RESPONSE FORMAT (MUST BE VALID JSON):**
{{
    "predictions": [
        {{"Disease": "Disease Name", "Confidence": 85.5}},
        {{"Disease": "Disease Name", "Confidence": 72.3}},
        {{"Disease": "Disease Name", "Confidence": 68.1}},
        {{"Disease": "Disease Name", "Confidence": 45.2}},
        {{"Disease": "Disease Name", "Confidence": 38.7}}
    ],
    "severity": {{
        "score": 65,
        "urgency": "Moderate",
        "risk_level": "Medium",
        "action": "Consult Doctor"
    }},
    "recommendations": {{
        "description": "Brief description in 1 line of the top predicted disease",
        "precautions": ["precaution 1", "precaution 2", "precaution 3", "precaution 4"],
        "medications": ["medication 1", "medication 2"],
        "diet": ["diet suggestion 1", "diet suggestion 2"],
        "workout": "recommended physical activity"
    }}
}}

Respond ONLY with valid JSON, no additional text."""
    print("✅ Groq system initialized with medical data!")


# Main Prediction Function
def predict_with_groq(user_symptoms):
    
    if system_message is None:
        raise Exception("System not initialized! Call initialize_groq_system() first.")
    
    # Create messages (only 2: system + user)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"User symptoms: {user_symptoms}"}
    ]

    
    try:
        # Call Groq API
        client = Groq(api_key=GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b",
        )
        
        # Get response
        response_text = chat_completion.choices[0].message.content
        # Parse JSON safely
        # result = json.loads(response_text)
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            print("Invalid JSON returned by Groq")
            print(response_text)
            return False, {}
        
        # Convert predictions to DataFrame for consistency with UI
        predictions_df = pd.DataFrame(result['predictions'])
        
        return True, {
            'predictions': predictions_df,
            'severity': result['severity'],
            'recommendations': result['recommendations']
        }
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return False, {}

initialize_groq_system()


