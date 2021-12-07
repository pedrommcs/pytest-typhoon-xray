# -*- coding: utf-8 -*-

from datetime import datetime
import requests
from tzlocal import get_localzone
from .runtime_settings import Settings
from .exceptions import XrayAuthError, XraySubmissionError, JiraError


def to_xray_timestamp(ts):
    local_tz = get_localzone()
    aware_ts = ts.replace(tzinfo=local_tz)
    text = aware_ts.strftime('%Y-%m-%dT%H:%M:%S%z')
    return text[:-2] + ':' + text[-2:]


def authenticate_xray():
    if not Settings.XRAY_TOKEN:
        credentials = {'client_id': Settings.XRAY_CLIENT_ID,
                       'client_secret': Settings.XRAY_CLIENT_SECRET}
        r = requests.post(
            f'{Settings.XRAY_HOST}/api/v1/authenticate',
            json=credentials)
        if r.status_code != 200 and not Settings.XRAY_FAIL_SILENTLY:
            raise XrayAuthError
        Settings.XRAY_TOKEN = r.json()
    return {'Authorization': f'Bearer {Settings.XRAY_TOKEN}'}


def send_test_results(test_results):
    headers = authenticate_xray()
    r = requests.post(f'{Settings.XRAY_HOST}/api/v1/import/execution',
                      headers=headers, json=test_results)
    if r.status_code != 200 and not Settings.XRAY_FAIL_SILENTLY:
        raise XraySubmissionError
    output = r.json()
    return output


def make_initial_test_result(start_time=datetime.now(), end_time=datetime.now()):
    return {
        'testExecutionKey': Settings.XRAY_EXEC_KEY,
        'info': {
            'description': 'This execution is automatically filled when running pytest.',
            'startDate': to_xray_timestamp(start_time),
            'finishDate': to_xray_timestamp(end_time),
            'testPlanKey': Settings.XRAY_PLAN_KEY,
            'testEnvironments': []
        },
        'tests': []
    }
