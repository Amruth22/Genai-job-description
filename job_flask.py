from quart import Quart, request, jsonify
from quart_cors import cors
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables from a .env file if available
load_dotenv()

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin="*")

# Configure OpenAI API key
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Prompt template
job_description_template = """
You are an expert HR professional tasked with creating key components of job descriptions. When given a job title, generate the following five sections in a specific JSON format:
1. Job Description:
A concise paragraph (2-4 sentences) that summarizes the role, its importance to the organization, and the primary objective of the position.
2. Qualifications:
List 4-6 key qualifications for the role, including:
- Required education or experience
- Personal attributes or soft skills
- Any necessary certifications or licenses
3. Required Skills:
List 5-7 essential skills that are mandatory for the role, such as:
- Technical proficiencies
- Specific software or tool expertise
- Critical competencies for job performance
4. Preferred Skills:
List 3-5 additional skills that are desirable but not mandatory, which could give candidates an edge, such as:
- Advanced certifications
- Specialized knowledge areas
- Additional language proficiencies
- Relevant industry experience
5. Key Responsibilities:
Detail 6-8 primary duties and responsibilities of the role, such as:
- Day-to-day tasks
- Strategic contributions
- Team or leadership responsibilities
- Client or stakeholder interactions
- Any specialized functions specific to the role or industry
Use clear, professional language tailored to the specific industry and level of the position. Use action verbs to begin each responsibility. Maintain a consistent tone that reflects a professional company culture and attracts suitable candidates.
Respond with a JSON object in the following format:
{{
  "Job Description": "string",
  "Qualifications": [
    "string",
    "string",
    ...
  ],
  "Required Skills": [
    "string",
    "string",
    ...
  ],
  "Preferred Skills": [
    "string",
    "string",
    ...
  ],
  "Key Responsibilities": [
    "string",
    "string",
    ...
  ]
}}
Create a job description for the position of {input}.
"""

@app.route('/generate-job-description', methods=['GET'])
async def generate_job_description():
    try:
        # Get the job title from query parameters
        job_title = request.args.get('job_title')

        if not job_title:
            return jsonify({"error": "Job title is required"}), 400

        # Construct the prompt
        prompt = job_description_template.format(input=job_title)

        # Call OpenAI API for completion
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert HR professional. Respond with a JSON object in the specified format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.0
        )

        # Extract the generated JSON from the response
        job_description = json.loads(response.choices[0].message.content)

        # Return the JSON directly
        return jsonify(job_description), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
