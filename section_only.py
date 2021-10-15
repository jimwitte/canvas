if __name__ == "__main__":
    import os
    from canvasapi import Canvas
    import time

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
    print("change enrollments to section-only")
    sections = course.get_sections()
    section_limited = True
    for section in sections:
        print(section)
        enrollments = section.get_enrollments()
        for enrollment in enrollments:
            if not enrollment.limit_privileges_to_course_section == section_limited and enrollment.type == 'StudentEnrollment' and enrollment.enrollment_state == 'active':  # do not change test student or students who are already limited
                print(f"    changing {enrollment.user['name']} {enrollment.user['id']} limited:{enrollment.limit_privileges_to_course_section}->{section_limited}")
                time.sleep(.25)
                section.enroll_user(
                    user=enrollment.user['id'],
                    enrollment={
                        'limit_privileges_to_course_section': section_limited
                    }
                )
    print()
    print()
