from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import pickle
from flask_cors import CORS
from sparql import *
from job_rec import *
from rdflib import Graph
import os

#App Config
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
app = Flask(__name__, template_folder=FRONTEND_FOLDER, static_folder=FRONTEND_FOLDER+"/src/asssets")
app.config.from_object(__name__)
app.secret_key = b'558'
CORS(app, resources={r'/*': {'origins': '*'}})

# Data Import
DATA_DIR = "app/backend/data/"

with open(DATA_DIR+"all_titles_preview.json") as file:
    all_titles_preview = json.load(file)
with open(DATA_DIR+"all_skills_preview.json") as file:
    all_skills_preview = json.load(file)
with open(DATA_DIR+"knn.pkl",'rb') as file:
    model = pickle.load(file)
with open(DATA_DIR+"mapping.pkl",'rb') as file:
    mapping = pickle.load(file)
graph = Graph()
graph.parse(DATA_DIR+'Career_KG.ttl', format='ttl')
all_skill_preprocessed_df = pd.read_csv(DATA_DIR+"all_titles_jobRec.csv", usecols=["name", "description", "responsibility", "salaryYearly", "salaryHourly", "relatedTitles", "skills"])


@app.route('/', methods = ['GET'])
def index():
    return render_template("index.html")

@app.route('/Search_Title', methods = ['GET','POST'])
def get_titles():
    response_payload = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        response_payload['data'] = all_titles_preview
    else:
        response_payload['data'] = all_titles_preview
    return jsonify(response_payload)

@app.route('/Title_Details/<title_name>', methods = ['GET'])
def get_title_details(title_name):
    title_name = title_name.replace("%or%","/")
    response_payload = {'status': 'success'}
    response_payload["data"] = get_job_info(title_name, graph)
    return jsonify(response_payload)

@app.route('/Search_Skill', methods = ['GET','POST'])
def get_skills():
    response_payload = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        category = post_data.get("category")
        if not category:
            category = None
        else:
            category = category[1]#.replace(" ","_")
        type = post_data.get("type")
        if 'Software' in type: isSoft = True
        else: isSoft = None
        if 'Language' in type: isLang = True
        else: isLang = None
        response_payload['data'] = filter_skills(category, isLang, isSoft, graph)
    else:
        response_payload['data'] = all_skills_preview
    return jsonify(response_payload)

@app.route('/Skill_Details/<skill_name>', methods = ['GET'])
def get_skill_details(skill_name):
    response_payload = {'status': 'success'}
    response_payload["data"] = get_skill_info(skill_name, graph)
    return jsonify(response_payload)

@app.route('/Job_Recommendation', methods = ['POST'])
def get_job_recommendation():
    skillset = set(request.get_json().get('query'))
    response_payload = {'status': 'success'}
    response_payload["data"] = predict(skillset, mapping, model, all_skill_preprocessed_df)
    return jsonify(response_payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5050",debug=True)