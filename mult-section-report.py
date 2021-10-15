if __name__ == "__main__":
    import os
    from canvasapi import Canvas
    import time
    from collections import Counter
    import datetime

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

    print(course)
    print("Find users with multiple section enrollments.")
    print()
    sections = course.get_sections()
    enrollment_check_list = []
    for section in sections:
        print(section)
        enrollments = section.get_enrollments()
        time.sleep(.125)
        for enrollment in enrollments:
            if enrollment.enrollment_state == 'active' and enrollment.type == 'StudentEnrollment':
               enrollment_dict = {
                    enrollment.user['id']: {
                        'user_name': enrollment.user['name'],
                        'section_id': section.id,
                        'section_name': section.name,
                        'enrollment_state': enrollment.enrollment_state,
                        'updated_at': enrollment.updated_at
                    }
                }
               enrollment_check_list.append(enrollment_dict)

    users = Counter([list(i.keys())[0] for i in enrollment_check_list])
    multi_section_users = [u for u in users if users[u] > 1]

    print("Name,Section,Enrollment_state,Updated_at")
    for multi_section_user in multi_section_users:
        for user in enrollment_check_list:
            if list(user.keys())[0] == multi_section_user:
                update_datetime = datetime.datetime.strptime(user[multi_section_user]['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                print(f"{user[multi_section_user]['user_name']},{user[multi_section_user]['section_name']},{user[multi_section_user]['enrollment_state']},{update_datetime}")