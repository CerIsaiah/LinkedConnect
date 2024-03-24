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
    jobs_df = pd.read_csv('../../filtered_jobs.csv')


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


jobs_df = pd.read_csv('./LinkedConnect/filtered_jobs.csv')


# Get the list of companies
companies = jobs_df['company'].unique()

# Get the school ID for Colgate University
school = linkedin.get_school("colgateuniversity")
school_id = helpers.get_id_from_urn(school["entityUrn"])

# Perform the LinkedIn search for each company
# Get the company IDs for all companies
results = {}  # Initialize an empty dictionary to store search results for each company

for company_name in companies:
    # Replace spaces with dashes if the company name is two words
    if isinstance(company_name, str):
        formatted_company_name = '-'.join(company_name.split()) if len(company_name.split()) == 2 else company_name
    
        print(f"Searching for company: {formatted_company_name}")
        
        try:
            # Attempt to get the company information from LinkedIn
            company = linkedin.get_company(formatted_company_name)
            
            if company:  # If company data is found'
                
                company_id = helpers.get_id_from_urn(company.get("entityUrn"))
                print("Found company IDDD!!!!!!!!!!!!!!!")
                if company_id:  # If a company ID is successfully extracted
                    # Perform the LinkedIn search with the company ID
                    employees = linkedin.search_people(
                        schools=[school_id],
                        current_company=[company_id],
                        limit=3,
                    )
                    
                    # Store the search results in the results dictionary using the company ID
                    results[company_id] = employees
                    print(f"Found {len(employees)} employees for company ID {company_id}")
                else:
                    print(f"Could not extract ID for company: {formatted_company_name}")
            else:
                print(f"No data found for company: {formatted_company_name}")
                
        except Exception as e:
            print(f"An error occurred while searching for {formatted_company_name}: {e}")
    else:
        print(f"Non-string value encountered in 'company' column: {company_name}")
        continue

    # After all companies have been searched, you may want to save the results
try:
    with open('search_results.json', 'w') as file:
        json.dump(results, file)
    print("Search results saved to search_results.json")
except Exception as e:
    print(f"An error occurred while saving the search results: {e}")


"""
if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""