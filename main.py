from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
import requests
import json
# 1. إعداد مفتاح الذكاء الاصطناعي (API Key)
# 🚨 ضع مفتاحك الحقيقي هنا بين علامتي التنصيص
GEMINI_API_KEY = "AIzaSyDVghw3JZsDr-9dsKcukUROtWHJIseHbK4"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def evaluate_with_llm(text):
    # المسار الصحيح والمدعوم لنموذج Gemini 2.5 Flash الجديد
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = """
    You are an expert academic evaluator. Analyze the following academic text and extract structural and methodological facts ONLY.
    Strict Instructions: Do not add what is appropriate or subjective commentary. Stick strictly to factual results.
    
    Return ONLY a raw JSON object with this exact structure (no markdown formatting, just the JSON):
    {
      "formal": ["List strings with [✓] or [X] checking if Abstract, Introduction, Literature Review, Methodology, and Conclusion exist in context, regardless of layout"],
      "methodological": ["List strings with [✓] or [-] checking statistical tests used. Pedagogical rule: If Trace Test and Max-Eigenvalue exist, Trace Test MUST precede Max-Eigenvalue"],
      "applied": ["List strings with [✓] or [X] checking for logical contradictions in data/results (e.g., claiming financial recovery while indicating negative capacity)"]
    }
    
    Text to analyze:
    """ + text[:30000]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        
        if response.status_code != 200:
            return {
                "formal": ["[X] API Connection Error"],
                "methodological": [f"[-] Status Code: {response.status_code}"],
                "applied": [f"[-] Error Details: {response.text[:200]}"]
            }
            
        data = response.json()
        result_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
            
        return json.loads(result_text)
        
    except Exception as e:
        return {
            "formal": ["[X] System Parsing Error"],
            "methodological": [f"[-] Details: {str(e)}"],
            "applied": []
        }

@app.post("/evaluate/")
async def evaluate_pdf(file: UploadFile = File(...)):
    content = await file.read()
    extracted_text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text: extracted_text += text + "\n"
    
    evaluation_results = evaluate_with_llm(extracted_text)
    return {"results": evaluation_results}