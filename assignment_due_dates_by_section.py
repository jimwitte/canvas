# create overrides for assignment by section start time

if __name__ == "__main__":

    import datetime as dt
    import time
    import csv
    import os
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

    print("Create due date overrides by section for an assignment based on section start day/time.")
    print(f"Assignments due at the time when the section meets that week.\n")
    print(f"Course: {course}")
    csvFilename = input("Enter csv sections filename [LAS101FALL2022_sections.csv]: ") or "LAS101FALL2022_sections.csv"

    sectionMetadata = {}
    with open(csvFilename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sectionMetadata[row['canvasSectionName']] = row

    def filterSectionsByDOW(sections, dow):
        """ given sections and day of week, return filtered dict """
        filtered = {k:v for (k,v) in sections.items() if v['day'] == dow}
        return filtered

    def isoDOWtoStr(dow):
        """ given isoweekday, return short string equivalent """
        """ example: isoDOWtoStr(7) = Sun """
        dow_map = {1:'M', 2:'T', 3:'W', 4:'R', 5:'F', 6:'S', 7:'Sun'}
        return dow_map[dow]

    def convert_to_24h_time(timeStr):
        dt.datetime.strftime
        convert_dt = dt.datetime.strptime(timeStr, '%I:%M %p')
        return convert_dt.strftime('%H:%M')

    print("** Current Assignments **")
    assignments = course.get_assignments()
    for a in assignments:
      print(a)

    assignmentID = input(f"Create due dates by section for which assignment ID? (ENTER = {assignments[0].id}): ") or assignments[0].id
    assignment = course.get_assignment(int(assignmentID))

    course_sections = {}
    for s in course.get_sections():
      course_sections[s.name] = s.id

    todays_date = dt.datetime.now().strftime("%Y-%m-%d")
    reference_date = input(f'Set due date overrides starting on this date [{todays_date}]): ') or todays_date

    unlock_date = input(f'Unlock date [None]: ') or None
    print("Lock date is normally same as due date to prevent late submissions. You can set a global lock date instead.")
    lock_date = input(f'Global Lock date [None]: ') or None

    # print(f'reference date: {reference_date}')
    # format = "%Y-%m-%d %H:%M:%S"
    format = "%Y-%m-%d"
    start_date = dt.datetime.strptime(reference_date, format)
    dayDelta = dt.timedelta(days=1)
    minDelta = dt.timedelta(minutes=1)

    offsetInput = input("Enter due date/time offset, like 1d or -30m [0m]: ") or '0d'
    offsetUnit = offsetInput[-1]  # d or m
    offsetAmt = int(offsetInput[:-1])  # how many d or m

    if offsetUnit == 'd':
        offset = dayDelta * offsetAmt
    elif offsetUnit == 'm':
        offset = minDelta * offsetAmt
    else:
        offset = 0 * dayDelta

    for d in range(7):
        assignment_date = start_date + (dayDelta * d)
        isoDOW = assignment_date.isoweekday()
        filtered_sections = filterSectionsByDOW(sectionMetadata, isoDOWtoStr(isoDOW))

        for section in filtered_sections.keys():
            sectionTime = convert_to_24h_time(filtered_sections[section]['start'])
            sectionDay = filtered_sections[section]['day']
            assignment_date_time_str = assignment_date.strftime("%Y-%m-%d " + sectionTime)
            assignment_date_time = dt.datetime.strptime(assignment_date_time_str, '%Y-%m-%d %H:%M') + (offset)
            override = {
                'course_section_id': course_sections[section],
                'due_at': assignment_date_time,
            }

            if not unlock_date == None:
                unlock_date_time = dt.datetime.strptime(unlock_date, '%Y-%m-%d')
                override['unlock_at'] = unlock_date_time
            
            if not lock_date == None:
                lock_date_time = dt.datetime.strptime(lock_date, '%Y-%m-%d')
                override['lock_at'] = lock_date_time
            else:
                override['lock_at'] = assignment_date_time
    
            print(f'Create override for "{section} {sectionTime} {sectionDay}" Due: {assignment_date_time}')
            assignment.create_override(assignment_override=override)
            time.sleep(.25)
