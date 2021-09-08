#! /usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import logging
import os
import sys
from enum import Enum, auto

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
        "--automation-status",
        help="Custom automation status",
        required=False,
        type=str,
        nargs='+',
        choices=[
            Status.UNTRIAGED.name,
            Status.SUITABLE.name,
            Status.UNSUITABLE.name,
            Status.COMPLETED.name,
            Status.DISABLED.name
        ]
    )

    parser.add_argument(
        "--sub-test-suite",
        help="Sub test suite",
        required=False,
        type=str,
        nargs='+',
        choices=[
            SubTestSuite.FUNCTIONAL.name,
            SubTestSuite.SMOKE.name,
            SubTestSuite.A11Y.name,
            SubTestSuite.L10N.name,
            SubTestSuite.SECURITY.name
        ]
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
        "--output",
        help="Output file for SQL consumption",
        required=False,
        default='output.json'
    )

    return parser.parse_args(args=cmdln_args)


class Status(Enum):
    UNTRIAGED = auto()
    SUITABLE = auto()
    UNSUITABLE = auto()
    COMPLETED = auto()
    DISABLED = auto()


class Coverage(Enum):
    NONE = auto()
    PARTIAL = auto()
    FULL = auto()


class SubTestSuite(Enum):
    FUNCTIONAL = auto()
    SMOKE = auto()
    A11Y = auto()
    L10N = auto()
    SECURITY = auto()


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


class Cases:
    JSON_dataset = []

    def __init__(self):
        pass

    def create_automation_status_count_dataset(
        self,
        cases,
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

        self.JSON_dataset = {
            "project_name": p['name'],
            "suite": s['name'],
            "untriaged": len(automation_untriaged),
            "suitable": len(automation_suitable),
            "unsuitable": len(automation_unsuitable),
            "completed": len(automation_completed),
            "disabled": len(automation_disabled)
        }

        with open(os.path.abspath(outfile), "w") as f:
            json.dump(self.JSON_dataset, f, sort_keys=False, indent=4)

    def get_all_full_automated(self, cases):
        return [case for case in cases if case['custom_automation_coverage'] ==
                Coverage.FULL.value and case['custom_automation_status'] ==
                Status.COMPLETED.value]

    def get_all_partial_automated(self, cases):
        return [case for case in cases if case['custom_automation_coverage'] ==
                Coverage.PARTIAL.value and case['custom_automation_status'] ==
                Status.COMPLETED.value]


class Sections:
    def __init__(self):
        pass

    def write_section_name(self, sections, suite):
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

    _logger.debug("Fetching suite and case data from TestRail...")
    s = t.get_suite(args.suite)

    c = Cases()
    cases = t.get_cases(args.project, args.suite, args.type)
    c.create_automation_status_count_dataset(
        cases, p, s, args.output)

    # for s in Status:
    #     for i in args.status:
    #         if i == s.value:
    #             print(d.json_to_sql({
    #                 "project_name": c.JSON_dataset['project_name'],
    #                 "suite": c.JSON_dataset['suite'],
    #                 "automation_state": s.name.lower(),
    #                 "case_count": c.JSON_dataset[s.name.lower()]
    #             }))

    # Example print all fully automated smoke & sanity
    # $ python testrail.py --project=59 --suite=3192 --sub-test-suite SMOKE
    if args.sub_test_suite:
        for sub_suite in args.sub_test_suite:
            if sub_suite == SubTestSuite.SMOKE.name:
                [print(case['title']) for case in cases if SubTestSuite.SMOKE.value in case['custom_sub_test_suites']
                 and case['custom_automation_status'] == Status.COMPLETED.value and case['custom_automation_coverage'] == Coverage.FULL.value]
            else:
                print(sub_suite)

    

    # E.g, print all full automated test cases in Smoke Tests with provided project/suite
    #print(args.sub_test_suite)
    #[print(case['title']) for case in cases if case['custom_automation_coverage'] ==
    #            Coverage.FULL.value and case['custom_automation_status'] ==
    #            Status.COMPLETED.value and SubTestSuite.SMOKE.value in case['custom_sub_test_suites']]


    # Example print a list of all disabled test cases
    if args.automation_status:
        for i in args.automation_status:
            if i == Status.DISABLED.name:
                [print(case['title']) for case in cases if
                 case['custom_automation_status'] is Status.DISABLED.value]

    # Example get a list of all fully automated test cases
    x = c.get_all_full_automated(cases)
    _logger.debug("{} cases are fully automated [{}][{}] from query".
                  format(len(x), Status.COMPLETED, Coverage.FULL))

    # Example get a list of all partially automated test cases
    f = c.get_all_partial_automated(cases)
    _logger.debug("{} cases are partially automated [{}][{}] from query".
                  format(len(f), Status.COMPLETED, Coverage.PARTIAL))


if __name__ == '__main__':
    main()
