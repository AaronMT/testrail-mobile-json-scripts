import os, sys
import json
import argparse
import logging
from testrail import APIClient
from enum import Enum

_logger = logging.getLogger('testrail')

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

    parser.add_argument(
        "--status",
        help="Custom automation status",
        required=True,
        type=int,
        nargs='+',
        choices=range(1,6)
    )

    parser.add_argument(
        "--stripped",
        help="Stripped output (default: %(default)",
        nargs='?',
        const='no',
        default='no',
        required=True,
        choices=['yes', 'no']
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

    def get_sections(self, project_id, suite_id):
        return self.client.send_get('get_sections/{0}&suite_id={1}'.format(project_id, suite_id))
    
    def write_json(self, blob, file):
        with open(file, "w") as f:
            json.dump(blob, f, sort_keys=True, indent=4)

class Cases:

    def __init__(self):
        pass
    
    def write_custom_automation_status(self, cases, status, suite, stripped):
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
        
        output = []
        statusFilename = ""

        for data in Status:
            for i in status:
                if i == data.value:
                    statusFilename += "-" + data.name
                    if i == Status.UNTRIAGED.value:
                        output.append(automation_untriaged)  
                    elif i == Status.SUITABLE.value:
                        output.append(automation_suitable)
                    elif i == Status.UNSUITABLE.value:
                        output.append(automation_unsuitable)
                    elif i == Status.COMPLETED.value:
                        output.append(automation_completed)
                    elif i == Status.DISABLED.value:
                        output.append(automation_disabled)
                    else:
                        pass

        with open("custom-automation-status-{0}{1}.json".format(str(suite), statusFilename), "w") as f:
            json.dump(output, f, sort_keys=True, indent=4)
            
        if(stripped == "yes"):
            with open("custom-automation-status-{0}{1}.json".format(str(suite), statusFilename)) as input:
                s = json.load(input)
                for x in s:
                    for case in x:
                        delete = [key for key in case if key != 'title' and key != 'custom_automation_status']
                        for key in delete: del case[key]
            with open("custom-automation-status-{0}{1}.json".format(str(suite), statusFilename), "w") as f:
                json.dump(s, f, sort_keys=True, indent=4)
        else:
            pass
                            
class Sections:

    def __init__(self):
        pass

    def write_section_name(self, sections, suite, stripped):
        data = []

        for s in sections:
            delete = [key for key in s if key != 'suite_id' and key != 'name']
            for key in delete: del s[key]
            data.append(s)

        with open('sections-from-suite-{}.json'.format(str(suite)), "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)

def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    _logger.debug("Fetching project data from Testrail...")
    t = TestRail()


    _logger.debug("Writing case automation status to JSON dump...")
    c = Cases()
    
    cases = t.get_cases(args.project, args.suite)  
    c.write_custom_automation_status(cases, args.status, args.suite, args.stripped)

    _logger.debug("Writing section data to JSON dump...")
    s = Sections()
    
    sections = t.get_sections(args.project, args.suite)
    s.write_section_name(sections, args.suite, args.stripped)

    _logger.debug("Stripping JSON dump...")

if __name__ == '__main__':
    main()
