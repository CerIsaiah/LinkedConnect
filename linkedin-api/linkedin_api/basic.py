import json

from linkedin_api import Linkedin
from linkedin_api.utils import helpers
import openai
from openai import OpenAI
import os
import pandas as pd



""" with open("credentials.json", "r") as f:
    credentials = json.load(f) """

linkedin = Linkedin("icisaiahcerven@gmail.com","21IC02463" )

profile_data = linkedin.get_profile("ashley-hendrata")
profile_data["contact_info"] = linkedin.get_profile_contact_info(
        "ashley-hendrata"
)

extracted_profile = {
    "displayPictureUrl": profile_data.get("displayPictureUrl"),
    "profile_id": profile_data.get("profile_id"),
    "profile_urn": profile_data.get("profile_urn"),
    "member_urn": profile_data.get("member_urn"),
    "public_id": profile_data.get("public_id"),
    "experience": profile_data.get("experience"),
    "education": profile_data.get("education"),
    "languages": profile_data.get("languages"),
    "publications": profile_data.get("publications"),
    "certifications": profile_data.get("certifications"),
    "volunteer": profile_data.get("volunteer"),
    "honors": profile_data.get("honors"),
    "projects": profile_data.get("projects"),
    "skills": profile_data.get("skills"),
    "urn_id": profile_data.get("urn_id"),
}

# Print the extracted information
#print(json.dumps(extracted_profile, indent=4))

""" print(extracted_profile["profile_id"])
print(extracted_profile["profile_urn"])
print(extracted_profile["urn_id"])
 """
for skill in profile_data.get("skills", []):
    skill_name = skill.get('name', 'Unknown Skill')
    #print(skill_name)

for experience in profile_data.get("experience", []):
    location = experience.get('locationName', 'Unknown Location')
    description = experience.get('description', 'Unknown Description')
    



with open("profile_data.json", "w") as f:
    json.dump(extracted_profile, f)


client = OpenAI(api_key='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')

prompt = f"Write a personalized message to connect with a LinkedIn user based on their profile information:\n\n"
prompt += f"Name: {profile_data.get('public_id', 'Unknown')}\n"
prompt += f"Skills: {', '.join([skill.get('name', 'Unknown Skill') for skill in profile_data.get('skills', [])])}\n"
prompt += f"Experience: {', '.join([experience.get('title', 'Unknown Title') for experience in profile_data.get('experience', [])])}\n"
prompt += f"Education: {', '.join([education.get('schoolName', 'Unknown School') for education in profile_data.get('education', [])])}\n"

""" chat_completion = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "system", "content": "You are creating short connection requests, trying to network with alumni. Your name is Isaiah"},{"role": "user", "content": prompt}]
)
message_body = chat_completion.choices[0].message.content
send_message = linkedin.send_message(message_body=message_body, recipients=[extracted_profile["urn_id"]])
print(send_message) """

colgate_info = linkedin.get_school("colgateuniversity")



params = {
    "keywords": "Google Colgate University",
    "filters": "List(currentCompany->Google, school->Colgate University)"
}

from flask import Flask, jsonify, request


app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

posted_data = {
    'company': 'google',
    'keywords': ''
}

@app.route('/post_data', methods=['POST'])
def post_data():
    global posted_data
    data = request.json
    posted_data['company'] = data.get('company', 'google')
    posted_data['keywords'] = data.get('keywords', '')
    return jsonify({'message': 'Data posted successfully'}), 200

@app.route('/get_employees', methods=['GET'])
def get_employees():
    jobs_df = pd.read_csv('./filtered_jobs.csv')

    # Get the list of companies
    companies = jobs_df['company'].unique()

    # Get the school ID for Colgate University
    school = linkedin.get_school("colgateuniversity")
    school_id = helpers.get_id_from_urn(school["entityUrn"])

    # Perform the LinkedIn search for each company
    # Get the company IDs for all companies
    company_ids = []
    for company_name in companies:
        company = linkedin.get_company(company_name)
        company_id = helpers.get_id_from_urn(company["entityUrn"])
        company_ids.append(company_id)

     # Perform the LinkedIn search with multiple company IDs
    employees = linkedin.search_people(
        keywords='',
        schools=[school_id],
        current_company=company_ids,
        limit=5,
        include_private_profiles=True
    )

    # Return the number of employees as the result
    print(employees)
    return jsonify(employees)

   
jobs_df = pd.read_csv('./filtered_jobs.csv')

# Get the list of companies
companies = jobs_df['company'].unique()

# Get the school ID for Colgate University
school = linkedin.get_school("colgateuniversity")
school_id = helpers.get_id_from_urn(school["entityUrn"])

# Perform the LinkedIn search for each company
# Get the company IDs for all companies
company_ids = []
for company_name in companies:
    print(company_name)
    company = linkedin.get_company(company_name)
    company_id = helpers.get_id_from_urn(company["entityUrn"])
    company_ids.append(company_id)

    # Perform the LinkedIn search with multiple company IDs
employees = linkedin.search_people(
    keywords='',
    schools=[school_id],
    current_company=company_ids,
    limit=5,
    include_private_profiles=True
)

# Return the number of employees as the result
print(employees)

"""
if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""