from google import genai
from google.genai import types
import os

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options=types.HttpOptions(api_version="v1")
)

for model in client.models.list():
    print(model.name)
