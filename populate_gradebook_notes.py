# Add gradebook column with metadata from csv section list

if __name__ == "__main__":
    import os
    from canvasapi import Canvas
    from dotenv import load_dotenv
    import time
    import csv

    load_dotenv()
    API_URL = os.environ.get('API_URL', None)
    API_KEY = os.environ.get('API_KEY', None)
    CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)

    if not all([API_URL, API_KEY, CANVAS_COURSE_ID]):
        print("Required environment variable not set.")
        exit(1)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(CANVAS_COURSE_ID)

    print("Populate gradebook \"notes\" column using metadata from csv section list.")
    print(f"Course: {course}")
    csvFilename = input("Enter csv sections filename [LAS101FALL2022_sections.csv]: ") or "LAS101FALL2022_sections.csv"

    sectionMetadata = {}
    with open(csvFilename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sectionMetadata[row['canvasSectionName']] = row
    
    notes_column = None
    custom_columns = course.get_custom_columns()
    for c in custom_columns:
        if c.title == 'Notes':
            notes_column = c

    if not notes_column:
        print('Notes column not found. exiting.')
        exit(1)

    sections = course.get_sections()
    column_data = []
    for section in sections:
        enrollments = section.get_enrollments()
        time.sleep(.25)
        metadata = sectionMetadata.get(section.name, {})
        if metadata == {}:
            print(f"No metadata found in csv file for canvas section \"{section.name}\"")
        else: 
            column_content = f"{metadata.get('399Section', '')} {metadata.get('internEmail', '')} {metadata.get('internName', '')}"
            for enrollment in enrollments:
                if enrollment.enrollment_state == 'active' and enrollment.type == 'StudentEnrollment':
                    print(f"add note \"{column_content}\" student: {enrollment.user['name']} section: {section.name}")
                    column_data.append(
                        {
                            "column_id": notes_column.id,
                            'user_id': enrollment.user['id'],
                            'content': column_content
                        }
                    )
    course.column_data_bulk_update(column_data)
