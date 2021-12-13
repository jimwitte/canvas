if __name__ == "__main__":

    import os
    from canvasapi import Canvas

    API_URL = os.environ.get('API_URL', None)
    API_KEY = os.environ.get('API_KEY', None)
    CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)

    if not all([API_URL, API_KEY, CANVAS_COURSE_ID]):
        print("Missing connection parameter(s). Need to source env file. Exiting.")
        exit(1)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(CANVAS_COURSE_ID)

    ### Get User from Canvas by netid ###
    netid = input('Enter netid: ')
    netid_user = canvas.get_user(netid, id_type='sis_login_id')
    print(netid_user)
    input('press enter to continue...')
    print()

    ### Get groupsets ###
    print("*** current groupsets ***")
    group_categories = course.get_group_categories()
    for groupset in group_categories:
        print(groupset)
    input('press enter to continue...')
    print()

    ### Create groupset ###
    groupset_name = input('Enter new groupset name: ')
    groupset = course.create_group_category(groupset_name)
    print(f'created groupset: "{groupset}"')
    input('press enter to continue...')
    print()

    ### Create Group ###
    group_name = input('Enter new group name: ')
    group = groupset.create_group(name=group_name)
    print(f"created group {group} in groupset {groupset}")
    input('press enter to continue...')
    print()

    ### Assign user to group ###
    ### user must be enrolled in course already
    group.create_membership(netid_user.id)
    print(f"added {netid_user.name} to group {group.name}")
    input('press enter to continue...')
    print()

    ### Get sections from course
    print('list of all sections in course:')
    sections = course.get_sections()
    for section in sections:
        print(section)
    input('press enter to continue...')
    print()

    ### Show section attributes
    first_section = sections[0]
    print(f"first section: {first_section}")
    print('Attributes of first section:')
    print(dir(first_section))
    input('press enter to continue...')
    print()

    ### find specific section by name
    ### section names do not have to be unique
    print("find/show section mu...")
    for section in sections:
        if section.name == 'mu':
            mu_section = section
            print(mu_section.name)
    input('press enter to continue...')
    print()

    ### enroll user in section
    ### note that users (including teachers) cannot unenroll themselves from any section

    print(f"Enrolled {netid_user.name} in section {first_section.name} as student")
    # StudentEnrollment, TeacherEnrollment, TaEnrollment, ObserverEnrollment, DesignerEnrollment
    first_section.enroll_user(netid_user, type='StudentEnrollment')
    input('press enter to continue...')
    print()

    ### create new section
    ## not currently authorized to delete sections, even sections we create here
    new_section_name = input('Enter new section name (you will not be able to delete this section!): ')
    if new_section_name != '':
        new_section = course.create_course_section(
            course_section={'name': new_section_name},
        )
        print(new_section)
    input('press enter to continue...')

    ### Enrollments ###
    enrollments = first_section.get_enrollments()
    print(f"enrollments for section {first_section}:")
    for enrollment in enrollments:
        print(enrollment.user['name'])
