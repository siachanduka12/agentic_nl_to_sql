import google.generativeai as genai

API_KEY = "AQ.Ab8RN6LLkEY_MMpZCDbhR_xqi7b1Z4edy3nOAakuqdxyRigFXg"

genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Hello")
    print(response.text)

except Exception as e:
    print("ERROR:")
    print(e)
