import os, json
from pprint import pprint
from enum import Enum
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

class Status(Enum):
    UNTRIAGED = 1
    SUITABLE = 2
    UNSUITABLE = 3
    COMPLETED = 4
    DISABLED = 5

automation_untriaged, automation_suitable, automation_unsuitable, automation_completed, automation_disabled = ([] for i in range(5))

for project in projects:
    project_id = project['id']
    if project_id == 14: # Firefox-iOS
        cases = client.send_get('get_cases/%s&suite_id=%s' % (project_id, 19))
        for case in cases:
            if case['custom_automation_status'] == Status.DISABLED.value:
                automation_disabled.append(case)
            elif case['custom_automation_status'] == Status.SUITABLE.value:
                automation_suitable.append(case)
            elif case['custom_automation_status'] == Status.UNSUITABLE.value:
                automation_unsuitable.append(case)
            elif case['custom_automation_status'] == Status.UNTRIAGED.value:
                automation_untriaged.append(case)
            elif case['custom_automation_status'] == Status.COMPLETED.value:
                automation_completed.append(case)
            else:
                pass

print("{} disabled automated tests.".format(str(len(automation_disabled))))
print("{} unsuitable automated tests.".format(str(len(automation_unsuitable))))
print("{} untriaged automated tests.".format(str(len(automation_untriaged))))
print("{} suitable automated tests.".format(str(len(automation_suitable))))
print("{} completed automated tests.".format(str(len(automation_completed))))
