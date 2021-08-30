Canvas API Utils
================

overrides_by_section.py
-----------------------
create due dates by individual sections, requires section metadata yaml file that lists section meeting times

custom_gradebook_column.py
--------------------------
add intern info to gradebook "notes" column. Also uses section meta data file.

mult-section-report.py
----------------------
find students with active enrollments in multiple sections

section_groups.py
-----------------
create a canvas group set, and a canvas group for each canvas course section. Used to facilitate group graded discussions.

audit_section_groups.py
-----------------------
for an existing group set, sync active section enrollments to section groups. Note that it's possible to enroll in multiple sections, but membership in a group set is limited to one group. Students enrolled in multiple sections will end up in the last section group processed for which they are a member.

section_only.py
---------------
change active enrollments to "this user can only view students in their assigned course section(s)". Currently students are enrolled with this setting set to false.

sample_envfile.txt
------------------
create a .env file with your canvas API key and the course ID for your course. This file should not be added to git.

sample_sections_file.yml
------------------------
file contains meta data about sections (meeting day/time, intern info). Used for overrides_by_section and custom_gradebook_column scripts.