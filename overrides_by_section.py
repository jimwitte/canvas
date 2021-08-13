if __name__ == "__main__":

    import datetime as dt
    import time
    import yaml
    import os
    from canvasapi import Canvas

    API_URL = os.environ.get('API_URL', None)
    API_KEY = os.environ.get('API_KEY', None)
    MIN_DUE = os.environ.get('MIN_DUE', None)
    CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)
    SECTION_FILE = os.environ.get('SECTIONS_FILE', None)
    
    if not all([API_URL, API_KEY, MIN_DUE, CANVAS_COURSE_ID, SECTION_FILE]):
        print("Missing connection parameter(s). Need to source env file. Exiting.")
        exit(1)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(CANVAS_COURSE_ID)

    with open(SECTION_FILE, 'r') as file:
        sections_list = yaml.load(file, Loader=yaml.FullLoader)

    def filterSectionsByDOW(sections, dow):
        """ given sections and day of week, return filtered dict """
        filtered_sections = {k:v for (k,v) in sections.items() if v['day'] == dow}
        return filtered_sections

    def isoDOWtoStr(dow):
        """ given isoweekday, return short string equivalent """
        """ example: isoDOWtoStr(7) = Sun """
        dow_map = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}
        return dow_map[dow]

    print("Create a week (7 days) of Canvas overrides by section for an assignment based on section meeting day/time.")
    print(f"Assignments due at the time when the section meets that week.\n")

    print(f"Assignments for course: {course}")

    assignments = course.get_assignments()
    for a in assignments:
      print(a)

    assignmentID = input(f"Create overrides for which assignment ID? (ENTER = {assignments[0].id}): ")
    if assignmentID == '':
        assignmentID = assignments[0].id

    assignment = course.get_assignment(int(assignmentID))

    course_sections = {}
    for s in course.get_sections():
      course_sections[s.name] = s.id

    todays_date = dt.datetime.now().strftime("%Y-%m-%d")
    reference_date = input(f'Create overrides starting on this date (ENTER = {todays_date}): ')
    if reference_date == '':
        reference_date = todays_date

    # print(f'reference date: {reference_date}')
    # format = "%Y-%m-%d %H:%M:%S"
    format = "%Y-%m-%d"
    start_date = dt.datetime.strptime(reference_date, format)
    dayDelta = dt.timedelta(days=1)
    minDelta = dt.timedelta(minutes=1)

    for d in range(7):
        assignment_date = start_date + (dayDelta * d)
        isoDOW = assignment_date.isoweekday()
        filtered_sections = filterSectionsByDOW(sections_list, isoDOWtoStr(isoDOW))
        for section in filtered_sections.keys():
            sectionTime = filtered_sections[section]['time']
            sectionDay = filtered_sections[section]['day']
            assignment_date_time_str = assignment_date.strftime("%Y-%m-%d " + sectionTime)
            assignment_date_time = dt.datetime.strptime(assignment_date_time_str, '%Y-%m-%d %H:%M') # - (MIN_DUE * minDelta)
            print(f'Created override for "{section}" {sectionTime} {sectionDay} -> DUE DATE/TIME {assignment_date_time} assignment: {assignmentID} SECTIONID: {course_sections[section]}')
            assignment.create_override(
                assignment_override = {
                    'course_section_id': course_sections[section],
                    'due_at': assignment_date_time,
                }
            )
            time.sleep(1)
