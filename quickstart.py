import os
from adaption import Adaption
from dotenv import load_dotenv
load_dotenv()

adaption_api_key = os.getenv("ADAPTION_API_KEY")

client = Adaption(api_key=adaption_api_key)
print("Connected to adaption ✨")
response1 = client.responses.create(
    model="qwen3.5-397b",
    input="Write a one-sentence bedtime story about a unicorn.",
        store=True,

)
print(response1.output_text)

response2 = client.responses.create(
    model="qwen3.5-397b",
    previous_response_id = response1.id,
    input="Write a one-sentence bedtime story about a unicorn continuing from the previous one.",
        store=True,

)

print(response2.output_text)
