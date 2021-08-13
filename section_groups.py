if __name__ == "__main__":

    import time
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
    
    print(course)
    print("Create a new groupset and create groups populated by section.")
    print("Students in multiple sections are added to only one group.")
    print()
    
    print("*** current groupsets ***")
    group_categories = course.get_group_categories()
    for groupset in group_categories:
      print(groupset)
    print()
    
    groupset_name = input('Enter new groupset name (like "section groups"): ')
    groupset = course.create_group_category(groupset_name)
    print(f'created groupset: "{groupset}"')
    print()

    print("Group name prefix + section name = group name")
    group_name_prefix = input('Enter group name prefix (like "LAS100 Sec"): ')
    print()
    
    sections = course.get_sections()
    for section in sections:
      sectionid = section.id
      group_name = group_name_prefix + " " + section.name
      group = groupset.create_group(
        name=group_name,
        description=section.id
      )
      print()
      print(f"created group: {group}")

      enrollments = section.get_enrollments()
      for enrollment in enrollments:
          if enrollment.user_id != 125495: # do not add test student id 125495
            group.create_membership(enrollment.user_id)
            print(f"create group membership for: {enrollment.user['name']} {enrollment.user_id} {enrollment.role}")
            time.sleep(.5)
