import sys
import os

# Add 'src' to the Python search path
sys.path.append(os.path.abspath('src'))
print("appending")

from flask import Flask, jsonify, request
from classes.constrain.program import Program
from classes.constrain.profile import Profile
from classes.solver_config import SolverConfig
from pymongo import MongoClient
from classes.components.course import Course
from classes.components.enums import Quarter
import json

# certifi included to explicitly point the backend to a trusted CA certificate
import certifi
from flask_cors import CORS


def load_app_settings(file_path='appsettings.json'):
    with open(file_path, 'r') as file:
        app_settings = json.load(file)
        return app_settings
    
# Database testing
app_settings = load_app_settings()
connection_string = app_settings["DatabaseConnection"]["ConnectionString"]

# certifi included to explicitly point the backend to a trusted CA certificate
client = MongoClient(connection_string, tls=True, tlsCAFile=certifi.where())


app = Flask(__name__)
CORS(app)

@app.get('/solve-user-schedule')
def solve_user_schedule():
    
    # Extracting URL parameters
    program_id = request.args.get("program")
    profile_id = request.args.get("profile")
    
    # Accessing collections
    db = client["SchedulerDB"]
    program_collection = db["Programs"]
    profile_collection = db["Profiles"]
    
    # TODO: Add null checking
    # Pulling documents
    program_dict = program_collection.find_one({"id": program_id})
    profile_dict = profile_collection.find_one({"id": profile_id})
    
    # Converting to objects
    program_obj = Program.from_dict(program_dict)
    profile_obj = Profile.from_dict(profile_dict)
    
    # TODO: Add validation to objects (most immediately course) to make sure they have necessary fields
    # Configuring solver
    scheduleSolver = SolverConfig(program=program_obj, profile=profile_obj)
    
    # Solving
    schedule = scheduleSolver.solve()
    
    # Master schedule dictionary
    schedule_dict = {"FRESH": {Quarter.FRESH_FALL: [], Quarter.FRESH_WINTER: [], Quarter.FRESH_SPRING: []}, 
                     "SOPH": {Quarter.SOPH_FALL: [], Quarter.SOPH_WINTER: [], Quarter.SOPH_SPRING: []}, 
                     "JUNIOR": {Quarter.JUNIOR_FALL: [], Quarter.JUNIOR_WINTER: [], Quarter.JUNIOR_SPRING: []}, 
                     "SENIOR": {Quarter.SENIOR_FALL: [], Quarter.SENIOR_WINTER: [], Quarter.SENIOR_SPRING: []}}
    
    if schedule:
        for course_code, quarter in schedule.items():
            if quarter.value <= 3:
                schedule_dict["FRESH"][quarter].append(course_code)
            elif quarter.value <= 7: 
                schedule_dict["SOPH"][quarter].append(course_code)
            elif quarter.value <= 11:
                schedule_dict["JUNIOR"][quarter].append(course_code)
            else:
                schedule_dict["SENIOR"][quarter].append(course_code)
    else:
        return jsonify({"schedule": "No schedule found"}), 200
    
    # Converting schedule to JSON serializable format
    for year in schedule_dict:
        schedule_dict[year] = {quarter.name: courses for quarter, courses in schedule_dict[year].items()}
    
    return jsonify({"schedule": schedule_dict}), 200


# Insert a program document into DB
@app.post('/post-program')
def post_program():
    
    # Accessing DB and collection
    db = client["SchedulerDB"]
    collection = db["Programs"]
    
    # Pseudo validation (Add real validation)
    request_json = request.json
    program = Program.from_dict(request_json)
    program_insert = program.to_dict()
    
    inserted_id = collection.insert_one(program_insert).inserted_id
    inserted_string = f"Inserted ID: {inserted_id}"
    
    return jsonify({"result": inserted_string}), 200


@app.post('/post-program-course')
def post_program_course():
    
    # Accessing DB and collection
    db = client["SchedulerDB"]
    collection = db["Programs"]
    
    # Accessing request information
    request_json = request.json
    course = request_json['course']
    program_id = request_json['id']
    
    # Validating for valid (offered quarters) string
    for quarter_string in course['offered_quarters']:
        if quarter_string not in Quarter.__members__:
            return jsonify({"error": f"Invalid quarter offered string: {quarter_string}"}), 400
    
    # Updating program sheet
    result = collection.update_one(
        {"id": program_id},
        {"$push": {"required_courses": course}}
    )
    
    # Check if the update was successful
    if result.matched_count == 0:
        return jsonify({"error": f"No program found with ID {program_id}"}), 404
    
    return jsonify({"result": f"Course {course['code']}: {course['title']} added to program {program_id}"}), 200

@app.post('/post-prereq-course')
def post_prereq_course():
    # Accessing DB and collection
    db = client["SchedulerDB"]
    collection = db["Programs"]
    
    # Accessing request information
    request_json = request.json
    program_id = request_json['id']
    course_code = request_json['course']
    
    # Getting prereq course
    prereq_course = request_json['prereq_course']
    
    result = collection.update_one(
        {
            "id": program_id, 
            "required_courses.code": course_code
        },
        {
            "$push": {
                    "required_courses.$.prereqs": prereq_course
            }
        }
    )
    
    if result.matched_count == 0:
        return jsonify({"error": f"No program found with ID {program_id} or course with code {course_code}"}), 404
    if result.modified_count == 0:
        return jsonify({"error": f"Course {course_code} not found in program {program_id}"}), 404
    
    return jsonify({"result": f"Prereq course {prereq_course} added to course {course_code} in program {program_id}"}), 200
    


@app.post('/post-profile')
def post_profile():
    
    # Accessing DB and collection
    db = client["SchedulerDB"]
    collection = db["Profiles"]
    
    # Pseudo validatin (Add real validation)
    request_json = request.json
    profile = Profile.from_dict(request_json)
    profile_insert = profile.to_dict()
    
    inserted_id = collection.insert_one(profile_insert).inserted_id
    inserted_string = f"Inserted ID: {inserted_id}"
    
    return jsonify({"result": inserted_string}), 200

# REMOVE THIS FOR PRODUCTION
# app.run(debug=True)
    