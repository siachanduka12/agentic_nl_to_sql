from groq import Groq

client = Groq(
    api_key="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"
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