from groq import Groq

client = Groq(
    api_key="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"
)

question = input("Ask a database question: ")

prompt = f"""
You are an SQL expert.

Database Schema:

employees(
    id,
    name,
    department,
    salary,
    joining_year
)

sales(
    id,
    product,
    amount,
    year
)

Convert the user's question into SQL.

Rules:
1. Return ONLY SQL.
2. Do NOT use markdown.
3. Do NOT use ```sql.
4. Do NOT give explanations.

Question:
{question}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\nGenerated SQL:")
print(response.choices[0].message.content)
