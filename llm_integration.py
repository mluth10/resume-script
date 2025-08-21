from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


# Load your resume and job description
with open('resume.json') as f:
    resume = json.load(f)
with open('job_description.txt') as f:
    job_desc = f.read()

# Build prompt
prompt = f"""
Given the following resume (in JSON format) and the following job description, rewrite the resume JSON to better match the keywords, skills, and requirements in the job description.
Only output optimized JSON — do not add explanations. Do not add any other text or comments. Keep the original formatting and structure of the resume. The output should be a similar length to the original resume.
Do not format the json, return the json as a raw string so that json.loads() can be used to parse it.
Make sure not to make up any information, only modify the resume to match the job description. You can change the ordering and add more detail, but do not claim I did anything I didn't do or have skills I don't have.

RESUME JSON:
{json.dumps(resume)}

JOB DESCRIPTION:
{job_desc}

OPTIMIZED RESUME JSON:
"""

# Call OpenAI API
response = client.chat.completions.create(
    model="gpt-4o",  # Or another suitable model
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000  # Adjust as needed
)

# Parse and save new resume
optimized_json = response.choices[0].message.content
optimized_resume = json.loads(optimized_json)
with open('optimized_resume.json', 'w') as f:
    json.dump(optimized_resume, f, indent=2)
