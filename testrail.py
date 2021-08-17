#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import logging
import os
import sys
from enum import Enum

from testrail_api import APIClient

_logger = logging.getLogger('testrail')


def parse_args(cmdln_args):
    parser = argparse.ArgumentParser(
        description="Gets case data for mobile projects on TestRail"
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
        choices=range(1, 6)
    )

    parser.add_argument(
        "--type",
        help="Case types to filter on",
        required=False,
        type=int,
        nargs='+',
        choices=range(1, 15),
        default=range(1, 15)
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

    parser.add_argument(
        "--output",
        help="Output file for SQL consumption",
        required=False,
        default='output.json'
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
        except KeyError as err:
            _logger.debug("set TESTRAIL_USERNAME and TESTRAIL_PASSWORD")
            SystemExit(err)

    def get_project(self, project_id):
        return self.client.send_get('get_project/{0}'.format(project_id))

    def get_cases(self, project_id, suite_id, type_id):
        return self.client.send_get(
            'get_cases/{0}&suite_id={1}&type_id={2}'.format(
                project_id, suite_id, ','.join(
                        [str(element) for element in type_id]
                )))

    def get_suites(self, project_id):
        return self.client.send_get('get_suites/{0}'.format(project_id))

    def get_suite(self, suite_id):
        return self.client.send_get('get_suite/{0}'.format(suite_id))

    def get_runs(self, project_id):
        return self.client.send_get('get_runs/{0}'.format(project_id))

    def get_priorities(self):
        return self.client.send_get('get_priorities')

    def get_sections(self, project_id, suite_id):
        return self.client.send_get(
            'get_sections/{0}&suite_id={1}'.format(project_id, suite_id))

    def write_json(self, blob, file):
        with open(file, "w") as f:
            json.dump(blob, f, sort_keys=True, indent=4)


class Cases:
    json_data, output = ([] for i in range(2))
    statusFilename = str()

    def __init__(self):
        self.json_data = []
        self.output = []
        self.statusFilename = str()

    def write_custom_automation_status(
        self,
        cases,
        status,
        suite,
        stripped,
        p,
        s,
        outfile
    ):

        (automation_untriaged, automation_suitable, automation_unsuitable,
            automation_completed, automation_disabled) = ([] for i in range(5))

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

        for data in Status:
            for i in status:
                if i == data.value:
                    self.statusFilename += "-" + data.name
                    if i == Status.UNTRIAGED.value:
                        self.output.append(automation_untriaged)
                    elif i == Status.SUITABLE.value:
                        self.output.append(automation_suitable)
                    elif i == Status.UNSUITABLE.value:
                        self.output.append(automation_unsuitable)
                    elif i == Status.COMPLETED.value:
                        self.output.append(automation_completed)
                    elif i == Status.DISABLED.value:
                        self.output.append(automation_disabled)
                    else:
                        pass

        '''with open("custom-automation-status-{0}{1}.json".format(
                  str(suite), statusFilename), "w") as f:
            json.dump(output, f, sort_keys=True, indent=4)

        if stripped == "yes":
            with open("custom-automation-status-{0}{1}.json".format(
                      str(suite), statusFilename)) as input:
                o = json.load(input)
                for x in o:
                    for case in x:
                        delete = [key for key in case if key != 'title' and
                                  key != 'custom_automation_status']
                        for key in delete:
                            del case[key]
            with open('custom-automation-status-{0}{1}.json'.format(str(suite),
                      statusFilename), 'w') as f:
                json.dump(o, f, sort_keys=True, indent=4)
        else:
            pass'''

        self.json_data = {"project_name": p['name'],
                          "suite": s['name'],
                          "untriaged": len(automation_untriaged),
                          "suitable": len(automation_suitable),
                          "unsuitable": len(automation_unsuitable),
                          "completed": len(automation_completed),
                          "disabled": len(automation_disabled)}

        with open(os.path.abspath(outfile), "w") as f:
            json.dump(self.json_data, f, sort_keys=False, indent=4)


class Sections:
    def __init__(self):
        pass

    def write_section_name(self, sections, suite, stripped):
        data = []

        for s in sections:
            delete = [key for key in s if key != 'suite_id' and key != 'name']
            for key in delete:
                del s[key]
            data.append(s)

        with open('sections-from-suite-{}.json'.format(str(suite)), "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)


class SQL:
    def __init__(self):
        pass

    def json_to_sql(self, data):
        return "INSERT INTO testrail_test_coverage (project_name, suite, " \
            "automation_state, case_count) VALUES " \
            "('{}', '{}', '{}', '{}')".format(
                data['project_name'],
                data['suite'],
                data['automation_state'],
                data['case_count']
            )


def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    _logger.debug("Fetching project data from TestRail...")
    t = TestRail()
    p = t.get_project(args.project)

    _logger.debug("Fetching suite data from TestRail...")
    s = t.get_suite(args.suite)

    _logger.debug("Writing case automation status to JSON dump...")
    c = Cases()
    cases = t.get_cases(args.project, args.suite, args.type)
    c.write_custom_automation_status(
        cases, args.status, args.suite, args.stripped, p, s, args.output)

    _logger.debug("Writing SQL inserts for each state...")
    d = SQL()

    for s in Status:
        for i in args.status:
            if i == s.value:
                print(d.json_to_sql({
                    "project_name": c.json_data['project_name'],
                    "suite": c.json_data['suite'],
                    "automation_state": s.name.lower(),
                    "case_count": c.json_data[s.name.lower()]
                }))


if __name__ == '__main__':
    main()
