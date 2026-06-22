from groq import Groq
from dotenv import load_dotenv
import json


load_dotenv()
system_message = ""

def groq_initialize():
    with open("models/disease_text.txt", "r") as file:
        symptoms_data = file.read()
    with open("models/severity_data.txt", "r") as file:
        severity_data = file.read()
    global system_message
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



def predict_disease(user_symptoms):
    chatbot = Groq()
    res = None   # ✅ define here

    try:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_symptoms}
        ]

        res = chatbot.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )

        response_text = res.choices[0].message.content
        response = json.loads(response_text)
        return response

    except Exception as e:
        try:
            if res:  # ✅ only if response exists
                import re
                response_text = res.choices[0].message.content

                match = re.search(r'"Disease"\s*:\s*"([^"]+)"', response_text)
                if match:
                    return {"fallback_disease": match.group(1)}

        except:
            pass

        return None


groq_initialize()


