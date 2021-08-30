if __name__ == "__main__":
    import os
    from canvasapi import Canvas
    import time
    import yaml

    API_URL = os.environ.get('API_URL', None)
    API_KEY = os.environ.get('API_KEY', None)
    MIN_DUE = os.environ.get('MIN_DUE', None)
    CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)
    SECTION_FILE = os.environ.get('SECTIONS_FILE', None)

    if not all([API_URL, API_KEY, MIN_DUE, CANVAS_COURSE_ID, SECTION_FILE]):
        print("Missing connection parameter(s). Need to source env file. Exiting.")
        exit(1)

    with open(SECTION_FILE, 'r') as file:
        section_metadata = yaml.load(file, Loader=yaml.FullLoader)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(CANVAS_COURSE_ID)

    print(course)
    print("Add non-editable gradebook column to list intern.")
    print()
    intern_column = None
    custom_columns = course.get_custom_columns()
    for custom_column in custom_columns:
        print(custom_column)
        if custom_column.title == 'Notes':
            intern_column = custom_column

    if not intern_column:
        print('Notes column not found. exiting.')
        exit(0)

    sections = course.get_sections()
    column_data = []
    for section in sections:
        enrollments = section.get_enrollments()
        time.sleep(.25)
        metadata = section_metadata.get(section.name, None)
        if metadata:
            for enrollment in enrollments:
                if enrollment.user['name'] != 'Test Student' and enrollment.type == 'StudentEnrollment':
                    print(f"add intern {metadata['intern']} for user {enrollment.user['name']} - {enrollment.user['id']}")
                    column_data.append(
                        {
                            "column_id": intern_column.id,
                            'user_id': enrollment.user['id'],
                            'content': metadata['intern']
                        }
                    )
        course.column_data_bulk_update(column_data)

