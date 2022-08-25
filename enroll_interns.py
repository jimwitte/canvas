import time
import os
import csv
from canvasapi import Canvas
from dotenv import load_dotenv

load_dotenv()
API_URL = os.environ.get('API_URL', None)
API_KEY = os.environ.get('API_KEY', None)
CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)

if not all([API_URL, API_KEY, CANVAS_COURSE_ID]):
    print("Required environment variable not set.")
    exit(1)

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(CANVAS_COURSE_ID)

print("Enroll interns into course from csv file")
print(f"Course: {course}")
csvFilename = input("Enter csv sections filename [LAS101FALL2022_sections.csv]: ") or "LAS101FALL2022_sections.csv"

sectionMetadata = {}
with open(csvFilename, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sectionMetadata[row['canvasSectionName']] = row

sections = course.get_sections()
for section in sections:
    md = sectionMetadata.get(section.name, None)
    if md is not None:
        internEmail = md.get('internEmail', None)
        internName = md.get('internName', None)
        if internEmail is not None:
            netid = internEmail.split('@')[0]
            if netid != '':
                netid_user = canvas.get_user(netid, id_type='sis_login_id')
                new_enrollment = section.enroll_user(
                    user=netid_user, 
                    enrollment={
                        'type': 'TeacherEnrollment', 
                        'limit_privileges_to_course_section': True
                    }
                )
                print(f"Name: {internName} NetID:{netid} -> {section.name}   Enrollment: {new_enrollment}")

# note: figure out how to use role: and/or role_id: to set role to undergraduate intern