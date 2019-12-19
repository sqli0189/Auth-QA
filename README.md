# Auth QA

This repo hosts the test framework and QA code for Auth project. Auth provides authorization services to Dashboard Apps include Demmand-side dashboard and Supply-side dashboard 

The test framework we've implemented is mainly built on Pytest and Requests library, it tests Auth backend services by sending HTTP requests to the backend endpoints and validates the JSON schema and field values. The framework inregrates Allure reporting framework to generate descritpive test execution reports that are clear to everyone in the team.

## Set up test environment

### Installation

The test framework is running against Python 3, please make sure you have Python 3.7(or above) and Pip3 installed on your computer. Once you create a local copy from this repo, you can go into it and install dependent python libraries by shooting below command:

> pip3 install -r packages.txt

The command will install all required libraries like Pytest, PyHamcrest and Allure etc. to your computer. 

You need to use allure command-line to resolve allure results and present test report in browsers, you can install it with Homebrew

> brew install allure

To develope your test cases, you may choose Visual Studio Code(Recommended!) or PyCharm as your IDE

### MongoDB Connection Settings

In the test framework, most of test cases need to access MongoDB in QA environment to prepare and clean up test data, so you need to config the MongoDB connection with your credentials before you run your first test case, in your local repom, you can execute below script to set up the MongoDB connection. (please make sure your crendentials have write permission to MongoDB)

> python3 update_config.py --db_host=#DB_HOST# --db_username=#DB_USERNAME# --db_password=#DB_PASSWORD#

You can also open the file named **config.json** on your local repo, and set your crendentials manually for below fields:

```
"mongo": {
    "host": "#DB_HOST#",
    "port": "15841",
    "username": "#DB_USERNAME#",
    "password": "#DB_PASSWORD#",
    "db_name": "vvv-repl"
    }
```

If you do not have credentials to access MongoDB in QA environment, please contracts Ops team to help you create the account.

## Run test cases

Our test framework is built on Pytest which supports several ways to run and select tests from the command-line. (We put all our test code in the **tests** foler)

### Run tests in a module

Run all test classes and test methods in the module **test_login.py**

>py.test tests/auth/login/test_login.py

### Run tests in a directory

>py.test tests/auth/login

### Run a specific test within a module and a class

>py.test tests/auth/login/test_login.py::TestLogin::test_login_with_valid_user

### Run tests by keyword expression

This will run tests which contain names that match the given string expression, which can include Python operators that use filenames, class names and function names as variables

>py.test -k "test_login_with_valid_user"

## Generate allure report

By default, Pytest will ouput test results to the terminal console directly, to generate descriptive allure report, firstly, you need to set Pytest to generate allure results while executing the tests

> py.test --alluredir=%allure_result_folder%

Then you can run allure command-line to review the test results in your local browser:

> allure serve %allure_result_folder%

On the opened browser, you will see the test report like below screenshot:

![image](https://user-images.githubusercontent.com/42924996/61687387-e4438880-ad54-11e9-8975-6301314cf3a7.png)