# create overrides for assignment by section start time

if __name__ == "__main__":

    import datetime as dt
    import time
    import csv
    import os
    from canvasapi import Canvas
    from dotenv import load_dotenv

    DAYDELTA = dt.timedelta(days=1)
    MINDELTA = dt.timedelta(minutes=1)

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

    def getOffset(contextPrompt):
        offsetInput = input(f"Enter relative date/time offset for {contextPrompt}, like 1d or -30m [0d]: ") or '0d'
        offsetUnit = offsetInput[-1]  # d or m
        offsetAmt = int(offsetInput[:-1])  # how many d or m
        if offsetUnit == 'd':
            relativeOffset = DAYDELTA * offsetAmt
        elif offsetUnit == 'm':
            relativeOffset = MINDELTA * offsetAmt
        else:
            relativeOffset = 0 * DAYDELTA
        return relativeOffset

    load_dotenv()
    API_URL = os.environ.get('API_URL', None)
    API_KEY = os.environ.get('API_KEY', None)
    CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)

    if not all([API_URL, API_KEY, CANVAS_COURSE_ID]):
        print("Required environment variable not set.")
        exit(1)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(CANVAS_COURSE_ID)

    print("Create due date overrides by section for an assignment relative to section start day & time.")
    print(f"Course: {course}")
    csvFilename = input("Enter csv sections filename [LAS101FALL2022_sections.csv]: ") or "LAS101FALL2022_sections.csv"

    sectionMetadata = {}
    with open(csvFilename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sectionMetadata[row['canvasSectionName']] = row

    print("** Current Assignments **")
    assignments = course.get_assignments()
    for a in assignments:
      print(a)
    assignmentID = input(f"Create due dates by section for which assignment ID? (ENTER = {assignments[0].id}): ") or assignments[0].id
    assignment = course.get_assignment(int(assignmentID))

    # create section name/id dictionary
    course_sections = {}
    for s in course.get_sections():
      course_sections[s.name] = s.id

    duedate_reference_date_input = input(f'Set due date overrides starting on this Sunday (YYYY-MM-DD)): ') or '2022-07-17'
    duedate_reference_date = dt.datetime.strptime(duedate_reference_date_input, "%Y-%m-%d")
    if not duedate_reference_date.isoweekday() == 7:
        print(f"{duedate_reference_date_input} is not a Sunday. Exiting.")
        exit(1)
    duedate_offset = getOffset("due dates")

    unlock_offset = 0 * DAYDELTA
    unlock_date_pref = input("Unlock date preference (global,relative,none) [none]: ") or None
    if unlock_date_pref == "global":
        unlock_reference_date_input = input('Global unlock date (YYYY-MM-DD): ')
        unlock_reference_date = dt.datetime.strptime(unlock_reference_date_input, "%Y-%m-%d")
    elif unlock_date_pref == "relative":
        unlock_reference_date_input = input('Relative unlock starting on this Sunday: (YYYY-MM-DD): ') or '2022-07-10'
        unlock_reference_date = dt.datetime.strptime(unlock_reference_date_input, "%Y-%m-%d")
        if not unlock_reference_date.isoweekday() == 7:
            print(f"{unlock_reference_date_input} is not a Sunday. Exiting.")
            exit(1)
        unlock_offset = getOffset("unlock dates")
    else:
        unlock_reference_date = dt.datetime.strptime('2022-01-01', "%Y-%m-%d")  # valid date, but not used
    
    lock_offset = 0 * DAYDELTA
    lock_date_pref = input("Lock date preference (duedate,relative,global,none): ") or None
    if lock_date_pref == 'global':
        lock_reference_date_input = input('Global Lock date (YYYY-MM-DD): ')
        lock_reference_date = dt.datetime.strptime(lock_reference_date_input, "%Y-%m-%d")
    elif lock_date_pref == 'relative':
        lock_reference_date_input = input('Relative lock starting on this date: (YYYY-MM-DD): ') or '2022-07-24'
        lock_reference_date = dt.datetime.strptime(lock_reference_date_input, "%Y-%m-%d")
        if not lock_reference_date.isoweekday() == 7:
            print(f"{lock_reference_date_input} is not a Sunday. Exiting.")
            exit(1)
        lock_offset = getOffset("lock dates")
    else:
        lock_reference_date = dt.datetime.strptime('2022-01-01', "%Y-%m-%d")  # valid date, but not used

    for d in range(7):
        assignment_duedate = duedate_reference_date + (DAYDELTA * d)
        assignment_unlock_date = unlock_reference_date + (DAYDELTA * d)
        assignment_lock_date = lock_reference_date + (DAYDELTA * d)
        isoDOW = assignment_duedate.isoweekday()
        filtered_sections = filterSectionsByDOW(sectionMetadata, isoDOWtoStr(isoDOW))

        for section in filtered_sections.keys():
            sectionTime = convert_to_24h_time(filtered_sections[section]['start'])
            sectionDay = filtered_sections[section]['day']
            assignment_duedate_time_str = assignment_duedate.strftime("%Y-%m-%d " + sectionTime)
            assignment_duedate_time = dt.datetime.strptime(assignment_duedate_time_str, '%Y-%m-%d %H:%M') + (duedate_offset)
            override = {
                'course_section_id': course_sections[section],
                'due_at': assignment_duedate_time,
            }

            if unlock_date_pref == 'global':
                override['unlock_at'] = dt.datetime.strptime(unlock_reference_date_input, '%Y-%m-%d')
            elif unlock_date_pref == 'relative':
                assignment_unlock_time_str = assignment_unlock_date.strftime("%Y-%m-%d " + sectionTime)
                override['unlock_at'] = dt.datetime.strptime(assignment_unlock_time_str, '%Y-%m-%d %H:%M') + (unlock_offset)

            if lock_date_pref == 'global':
                override['lock_at'] = dt.datetime.strptime(lock_reference_date_input, '%Y-%m-%d')
            elif lock_date_pref == 'duedate':
                override['lock_at'] = assignment_duedate_time
            elif lock_date_pref == 'relative':
                assignment_lock_time_str = assignment_lock_date.strftime("%Y-%m-%d " + sectionTime)
                override['lock_at'] = dt.datetime.strptime(assignment_lock_time_str, '%Y-%m-%d %H:%M') + (lock_offset)
    
            print(f"{section[:30] : <30} {sectionTime : <6} {sectionDay : <2} Due: {assignment_duedate_time}     Unlock: {override.get('unlock_at','')}     Lock: {override.get('lock_at','')}")
            assignment.create_override(assignment_override=override)
            time.sleep(.25)
