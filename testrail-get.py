import os, json
from pprint import pprint
from testrail import *

client = APIClient('https://testrail.stage.mozaws.net')

try:
    client.user = os.environ['TESTRAIL_USERNAME']
    client.password = os.environ['TESTRAIL_PASSWORD']
except KeyError:
    print("TESTRAIL_USERNAME and TESTRAIL_PASSWORD environment variables must be set.")
    exit()

print("Fetching project data from Testrail..." + "\n")

projects = client.send_get('get_projects')

untriaged, suitable, unsuitable, completed, disabled = range(1, 6)

automation_disabled = []
automation_suitable = []

for project in projects:
    project_id = project['id']
    if project_id == 59: # Fenix
       suites = client.send_get('get_suites/%s' % project_id)
       for suite in suites:
           suite_id = suite['id']
           cases = client.send_get('get_cases/%s&suite_id=%s' % (project_id, suite_id))
           for case in cases:
               if case['custom_automation_status'] == disabled:
                   automation_disabled.append(case['title'])
               elif case['custom_automation_status'] == suitable:
                   automation_suitable.append(case['title'])

print("{} disabled automated tests.".format(str(len(automation_disabled))))