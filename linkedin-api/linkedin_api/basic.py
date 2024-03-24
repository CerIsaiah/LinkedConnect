import json

from linkedin_api import Linkedin
from linkedin_api.utils import helpers
import openai
from openai import OpenAI
import os
import pandas as pd




linkedin = Linkedin("icisaiahcerven@gmail.com","21IC02463" )

from flask import Flask, jsonify, request


app = Flask(__name__)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    profile_id = data.get('profile_id')
    profile_data = linkedin.get_profile(profile_id)
    profile_data["contact_info"] = linkedin.get_profile_contact_info(profile_id)

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

    template =  """Subject: [Your University] Alumni Seeking Job Search Advice [Your Name]
    Hi [Fellow Alumni's Name], I hope you're doing well. I recently found your profile on our [University Name] alumni network. I noticed that we both [shared connection #1, e.g., graduated with a degree in Business Administration] and [shared connection #2, e.g., volunteered at the campus food bank]. I am currently exploring new opportunities in [your field or industry] and would appreciate any advice or guidance you may have.
    It is inspiring to see a fellow [University Name] graduate succeed in [their position/industry]. If you have any tips or resources that have helped you in your career journey, I would be grateful to learn from your experience.
    Thank you for your time and consideration.
    Best regards,
    [Your Name] """
    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": f"You are creating short connection requests, trying to network with alumni. Your name is Isaiah, here is a short template you can grab ideas from: {template}"},{"role": "user", "content": prompt}]
    )
    message_body = chat_completion.choices[0].message.content
    send_message = linkedin.send_message(message_body=message_body, recipients=[extracted_profile["urn_id"]])
    return jsonify({'message': 'Message sent successfully', 'response': send_message}), 200 

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

    all_employees = []  # List to store all employees

    for company_name in companies:
        if isinstance(company_name, str):
            formatted_company_name = '-'.join(company_name.split()) if len(company_name.split()) == 2 else company_name
            print(f"Searching for company: {formatted_company_name}")

            try:
                company = linkedin.get_company(formatted_company_name)
                if company:
                    company_id = helpers.get_id_from_urn(company.get("entityUrn"))
                    if company_id:
                        employees = linkedin.search_people(
                            schools=[school_id],
                            current_company=[company_id],
                            limit=3,
                        )

                        # Add formatted company name to each employee's data
                        for employee in employees:
                            employee['formatted_company_name'] = formatted_company_name
                            all_employees.append(employee)

                        print(f"Found {len(employees)} employees for company {formatted_company_name}")
                    else:
                        print(f"Could not extract ID for company: {formatted_company_name}")
                else:
                    print(f"No data found for company: {formatted_company_name}")
            except Exception as e:
                print(f"An error occurred while searching for {formatted_company_name}: {e}")
        else:
            print(f"Non-string value encountered in 'company' column: {company_name}")

    return jsonify(all_employees)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
