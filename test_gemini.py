import google.generativeai as genai

API_KEY = "api"

genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Hello")
    print(response.text)

except Exception as e:
    print("ERROR:")
    print(e)
