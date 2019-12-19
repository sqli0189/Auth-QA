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
@allure.feature('New user confirm to login')
class TestConfirm(object):


    @allure.story('Confirm to sign in with correct token')
    @allure.severity('critical')
    def test_confirm_with_correct_token(self, new_registered_user):
        '''
        A HTTP 200 OK is expected to be returned.
        '''

        # Get the token of new user
        user_name = new_registered_user[0]
        user_token = new_registered_user[2]

        confirm_payload = payload.confirm(token = user_token)

        r = post(auth_confirm_endpoint, json=confirm_payload, headers=headers(vungle_version='1'))

        # Build expected response
        expected_response_payload = {'username': user_name}

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)
        # Verify the resposne content
        assert_that(r.json(), has_entries(expected_response_payload))


    @allure.story('Call confirm endpoint with an inexistent token')
    @allure.severity('normal')
    def testN_confirm_with_inexistent_token(self):
        '''
        A HTTP 404 error is expected to be returned
        '''

        confirm_payload = payload.confirm(token='zzzzzzzzz')

        r = post(auth_confirm_endpoint, json=confirm_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.NOT_FOUND)
        # Verify content
        assert_that(r.text, equal_to(''))


    @allure.story('Call confirm endpoint without payload information')
    @allure.severity('normal')
    def testN_confirm_without_payload(self):
        '''
        An error message is expected to be returned
        '''
        r = post(auth_confirm_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        #Verify response content
        assert_valid_schema(r.json(), response_schema.error_message)
        assert_that(r.json(), equal_to({"code": 602, "message": "body in body is required"}))


    @allure.story('Call confirm endpoint without vungle-version in request headers')
    @allure.severity('minor')
    def testN_confirm_without_vungle_version_in_headers(self):
        '''
        An error message is expected to be returned.
        '''
        confirm_payload = payload.confirm(token='zzzzzzzzz')

        r = post(auth_confirm_endpoint, json=confirm_payload, headers=headers())

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)
        # Verify content
        assert_that(r.json(), equal_to({"code": 602, "message": "vungle-version in header is required"}))