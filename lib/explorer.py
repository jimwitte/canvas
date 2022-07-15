# get course section info from UIUC course explorer
# course_info = explorer.get_course({'year': '2021', 'term': 'FALL', 'rubric': 'LAS', 'number': '100'})

import requests
from lxml import etree


def get_course(course):
    """ get course sections from UIUC course explorer - return courseInfo """

    course_info_url = ("https://courses.illinois.edu/cisapp/explorer/schedule/" +
                       f"{course['year']}/{course['term']}/{course['rubric']}/{course['number']}.xml")
    r = requests.get(course_info_url, params={'mode': 'cascade'}, timeout=60)

    if r.status_code != requests.codes.ok:
        print(f'http error, status code: {r.status_code}')
        exit(1)

    course_data = etree.fromstring(r.content)

    rubric = course_data.get("id")
    termcode = course_data.find(".//term").get("id")
    calendar_year = course_data.find(".//calendarYear").get("id")
    sections = course_data.find("detailedSections")
    dow = {'M': 'Mon', 'T': 'Tue', 'W': 'Wed', 'R': 'Thu', 'F': 'Fri', 'S': 'Sat', '': ''}

    course_info = []
    
    for section in sections:
        course_num = section.find(".//course").get("id")
        course_subj = section.find(".//subject").get("id")
        section_number = section.find("sectionNumber")
        if section_number is not None:
            section_number = section_number.text.strip()
        else:
            section_number = ''

        section_crn = section.get("id")

        # get meeting times & locations
        s_meetings = []

        meetings = section.find("meetings")
        for meeting in meetings:
            start = end = days_of_the_week = room_number = building_name = location = meeting_time = ''
            if meeting.find("start") is not None:
                start = meeting.find("start").text.strip()
            if meeting.find("end") is not None:
                end = meeting.find("end").text.strip()
            if meeting.find("daysOfTheWeek") is not None:
                days_of_the_week = meeting.find("daysOfTheWeek").text.strip()
            if meeting.find("roomNumber") is not None:
                room_number = meeting.find("roomNumber").text.strip()
            if meeting.find("buildingName") is not None:
                building_name = meeting.find("buildingName").text.strip()
            if not room_number == '' and not building_name == '':
                location = f"{room_number} {building_name}"
            if not start == '' and not end == '':
                meeting_time = f"{start}-{end} {dow.get('daysOfTheWeek', days_of_the_week)}"

            s_meetings.append({
                'buildingName': building_name,
                'roomNumber': room_number,
                'daysOfTheWeek': dow.get('daysOfTheWeek', days_of_the_week),
                'startTime': start,
                'endTime': end,
                'location': location,
                'time': meeting_time
            })

        s_meetings_string = ",".join(f"{m['time']} {m['location']}" for m in s_meetings)
        s_meeting_times = ",".join(f"{m['time']}" for m in s_meetings)
        
        course_info.append({
            'rubric': rubric,
            'subject': course_subj,
            'number': course_num,
            'section': section_number,
            'crn': section_crn,
            'termcode': termcode,
            'term': course['term'].lower().capitalize(),
            'year': calendar_year,
            'meetings': s_meetings,
            'meetingsStr': s_meetings_string,
            'meetingTimes': s_meeting_times
        })
    return course_info


if __name__ == "__main__":
    courses = [
        {'rubric': 'MATH', 'number': '101', 'term': 'FALL', 'year': '2021'},
        {'rubric': 'MATH', 'number': '347', 'term': 'FALL', 'year': '2021'}
    ]

    for c in courses:
        print(get_course(c))
