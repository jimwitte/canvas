# Create a groupset, and create a group for each section
# Note that only students can be added to a group, not Teachers or TAs.

if __name__ == "__main__":

    import time
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
    
    print("Create a new groupset and create groups populated by section.")
    print("Students in multiple sections are added to only one group.")
    print("Only students may be added to groups. Not Teachers or TAs.")
    print(f"Course: {course}")
    
    print("*** current groupsets ***")
    group_categories = course.get_group_categories()
    for groupset in group_categories:
      print(groupset)
    print()
    
    groupset_name = input('Enter new groupset name [Section Groups]: ') or "Section Groups" 

    for groupset in group_categories:
      if groupset.name == groupset_name:
        print("groupset already exists.")
        exit(1)
    
    groupset = course.create_group_category(groupset_name)
    print()
    print(f'Created groupset: "{groupset}"')
    print()
    
    sections = course.get_sections()
    for section in sections:
      sectionid = section.id
      group_name = f"{section.name} Group"
      group = groupset.create_group(
        name=group_name,
        description=section.id
      )
      print(f"Created group: {group}")

      enrollments = section.get_enrollments()
      for enrollment in enrollments:
          if enrollment.enrollment_state == 'active' and enrollment.type == 'StudentEnrollment':
            group.create_membership(enrollment.user_id)
            print(f"   {enrollment.user['name']} added to {group}")
            time.sleep(.25)
