import os, sys
import json
import argparse
import logging
from testrail import *
from enum import Enum

_logger = logging.getLogger('xcresult')

def parse_args(cmdln_args):
    parser = argparse.ArgumentParser(
        description="Script that fetches case data for mobile projects on Testrail"
    )

    parser.add_argument(
        "--project",
        help="Use selected project",
        required=True,
        type=int
    )

    parser.add_argument(
        "--suite",
        help="Use selected suite",
        required=True,
        type=int
    )

    return parser.parse_args(args=cmdln_args)

class Status(Enum):
    UNTRIAGED = 1
    SUITABLE = 2
    UNSUITABLE = 3
    COMPLETED = 4
    DISABLED = 5

class TestRail:
    
    def __init__(self):
        self.set_config()

    def set_config(self):
        self.client = APIClient('https://testrail.stage.mozaws.net')
        try:
            self.client.user = os.environ['TESTRAIL_USERNAME']
            self.client.password = os.environ['TESTRAIL_PASSWORD']
        except KeyError:
            _logger.debug("TESTRAIL_USERNAME and TESTRAIL_PASSWORD environment variables must be set.")
            exit()

    def get_project(self, project_id):
        return self.client.send_get('get_project/{0}'.format(project_id))

    def get_cases(self, project_id, suite_id):
        return self.client.send_get('get_cases/{0}&suite_id={1}'.format(project_id, suite_id))

    def get_suites(self, project_id):
        return self.client.send_get('get_suites/{0}'.format(project_id))

    def get_runs(self, project_id):
        return self.client.send_get('get_runs/{0}'.format(project_id))

    def get_priorities(self):
        return self.client.send_get('get_priorities')

    def write_json(self, blob, file):
        with open(file, "w") as f:
            json.dump(blob, f)

class Cases:

    def __init__(self):
        pass
    
    def get_custom_automation_statuses(self, cases):
        automation_untriaged, automation_suitable, automation_unsuitable, automation_completed, automation_disabled = ([] for i in range(5))
    
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
        
        # Take arrays and write out to json?
        # json.dumps(array)
  
        
def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    _logger.debug("Fetching project data from Testrail...")
    t = TestRail()

    cases = t.get_cases(args.project, args.suite)
    t.write_json(cases, 'cases.json')

    c = Cases()
    c.get_custom_automation_statuses(cases)


if __name__ == '__main__':
    main()
