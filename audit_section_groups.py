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
    print("Audit section groups for members who have dropped, added, or changed sections")
    print()

    print("*** Current Groupsets ***")
    group_categories = course.get_group_categories()
    for groupset in group_categories:
      print(groupset)
    print()
    groupset_id = int(input("Enter group set id: "))
    groupset = canvas.get_group_category(groupset_id)
    groups = groupset.get_groups()
    for group in groups:
        memberships = group.get_memberships()
        group_members = set([int(member.user_id) for member in memberships])
        sectionid = int(group.description)  #sectionid stored in group description field
        section = course.get_section(sectionid)
        enrollments = section.get_enrollments()
        section_members = set([int(enrollment.user_id) for enrollment in enrollments])
        section_members.discard(125495) # remove the test student if present
        if section_members == group_members:
            print(f"{group.name} -> OK")
        for user_id in (section_members - group_members):
            user = course.get_user(user_id)
            print(f'{group.name} -> add {user}')
        for user_id in (group_members - section_members):
            user = course.get_user(user_id)
            print(f'{group.name} -> remove {user} ')
        time.sleep(1)