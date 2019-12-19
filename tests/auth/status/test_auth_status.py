import pytest
import allure

from hamcrest import *
from http import HTTPStatus

from qa.utils.common import *

import qa.utils.db_access as db
import qa.utils.payload as payload
from qa.utils.assertions import *

import qa.data.response_schema as response_schema

from qa.settings import *

@allure.epic('Mission Ctrl: Authentication')
@allure.feature('Get Auth Status')
@allure.story('Check status of the auth services')
@allure.severity('blocker')
def test_auth_status():
    '''
    The status endpoint should return HTTP 200 OK
    '''
    r = get(auth_status_endpoint)
    assert_response_status_code(r.status_code, HTTPStatus.OK)