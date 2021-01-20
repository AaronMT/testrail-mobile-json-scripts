import os, sys
import json
import argparse
import logging
from testrail import *

client = APIClient('https://testrail.stage.mozaws.net')

try:
    client.user = os.environ['TESTRAIL_USERNAME']
    client.password = os.environ['TESTRAIL_PASSWORD']
except KeyError:
    print("TESTRAIL_USERNAME and TESTRAIL_PASSWORD environment variables must be set.")
    exit()

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

def get_project(project):
    print("Fetching project data from Testrail...", end="\n")
    project = client.send_get('get_project/{0}'.format(project))
    return project

def get_cases(project, suite):
    print("Fetching cases data from Testrail...", end="\n")
    cases = client.send_get('get_cases/{0}&suite_id={1}'.format(project, suite))
    return cases

def get_suites(project):
    print("Fetching suite data from Testrail...", end="\n")
    suites = client.send_get('get_suites/{0}'.format(project))
    return suites

def write_json(blob, file):
    with open(file, "w") as f:
        json.dump(blob, f)

def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    
    cases = get_cases(args.project, args.suite)
    write_json(cases, 'cases.json')

if __name__ == '__main__':
    main()
