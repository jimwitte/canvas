# Create a groupset, and create a group for each section
# Note that only students can be added to a group, not Teachers or TAs.

if __name__ == "__main__":

  import time
  import os
  import csv
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

  def make_url_table(urllist):
    table = "<table>"
    for u in urllist:
      table += f"""
      <tr>
        <td>{u['name']} &nbsp;</td>
        <td><a href=\"{u['url']}\">{u['url']}</a></td>
      </tr>
      """
    table += "</table>"
    return table

  def make_section_page(sectionData,canvasGroup):
    section_page_content = f"""
      <strong>Meeting time:</strong> {sectionData['prettyDay']} {sectionData['start']}<br />
      <strong>Location:</strong> {sectionData['bldg']} {sectionData['room']}<br />
      <strong>Intern:</strong> {sectionData['internName']} {sectionData['internEmail']}<br />
    """
    canvasGroup.create_page(
      wiki_page={
        'title': f"{sectionData['rubric']} Section {sectionData['sectionName']} Information",
        'editing_roles': 'teachers',
        'published': True,
        'body': section_page_content
      },
      url='info'
    )

  print("Create a new groupset and create groups populated by section.")
  print("Students in multiple sections are added to only one group.")
  print("Only students may be added to groups. Not Teachers or TAs.")
  print("CSV file is optional to create section group pages.")
  print(f"Course: {course}")

  csvFilename = input("Enter csv sections filename [none]: ") or None

  if not csvFilename == None:
    sectionMetadata = {}
    with open(csvFilename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sectionMetadata[row['canvasSectionName']] = row
  
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
  urls = []

  for section in sections:
    sectionid = section.id
    group_name = f"{section.name}"
    group = groupset.create_group(
      name=group_name,
      description=section.id
    )
    groupTabs = group.get_tabs()
    groupHome = [t for t in groupTabs if t.id == 'home'][0]
    print(f"{group.name},{groupHome.full_url}")
    urls.append({
      'name': group_name,
      'url': groupHome.full_url
    })

    if not csvFilename == None:
      md = sectionMetadata.get(group_name, None)
      if md is not None:
        make_section_page(sectionMetadata[group_name],group)
        print(f"Created page for section: {group_name}")
        time.sleep(.25)

    enrollments = section.get_enrollments()
    for enrollment in enrollments:
        if enrollment.enrollment_state == 'active' and enrollment.type == 'StudentEnrollment':
          group.create_membership(enrollment.user_id)
          print(f"   {enrollment.user['name']} added to {group}")
          time.sleep(.25)
  pageContent = make_url_table(urls)

  pageContent = make_url_table(urls)
  course.create_page(
    wiki_page={
      'title': groupset_name,
      'editing_roles': 'teachers',
      'published': False,
      'body': pageContent
    },
    url=groupset_name
  )