from groq import Groq

client = Groq(
    api_key="api"
)

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "Say hello"
            }
        ]
    )

    print(response.choices[0].message.content)

except Exception as e:
    print("ERROR:")
    print(e)
