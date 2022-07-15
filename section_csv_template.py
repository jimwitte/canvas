import csv
import lib.explorer as explorer
from faker import Faker
import random

fake = Faker()
addFakeData = False

def getFakeData(dataType):
    if not addFakeData:
        return ''
    elif dataType == 'name':
        return fake.name()
    elif dataType == 'email':
        return fake.ascii_safe_email()
    elif dataType == 'las399':
        return random.choice(['399A','399B','399C','399D','399E'])

course = {}
course['year'] = input("Year [2022]: ") or "2022"
course['term'] = input("Term [FALL]: ") or "FALL"
course['rubric'] = input("Rubric [LAS]: ") or "LAS"
course['number'] = input("Number [101]: ") or "101"
fakeDataChoice = input("Add fake data? [Yes]: ") or "Yes"
if fakeDataChoice in ['y','yes','Yes']:
    addFakeData = True

# course = {'year': '2022', 'term': 'FALL', 'rubric': 'LAS', 'number': '101'}

sections = explorer.get_course(course)

csv_output_filename = f"{course['rubric']}{course['number']}{course['term']}{course['year']}_sections.csv"

with open(csv_output_filename, 'w', newline='') as csvfile:
    fieldnames = ['rubric','sectionName','crn','canvasSectionName','location','day','start','internName','internEmail','399Section']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for section in sections:
        writer.writerow(
            {
                'rubric': section['rubric'], 
                'sectionName': section['section'],
                'crn': section['crn'],
                'canvasSectionName': f"{section['rubric']} {section['section']} {section['term']} {section['year']} CRN{section['crn']}",
                'location': f"{section['meetings'][0]['buildingName']} {section['meetings'][0]['roomNumber']}",
                'day': section['meetings'][0]['daysOfTheWeek'],
                'start': section['meetings'][0]['startTime'],
                'internName': getFakeData('name'),
                'internEmail': getFakeData('email'),
                '399Section': getFakeData('las399')
            }
        )
