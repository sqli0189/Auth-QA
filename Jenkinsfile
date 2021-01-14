pipeline{
    agent { 
        kubernetes {
            yamlFile 'KubernetesPod.yaml'
            defaultContainer 'pytest'            
        }
    }
    //triggers{
    //    cron('H 17 * * *')
    //}
    environment {
        ALLURE_RESULT_PATH = './target/allure-result'
    }
    parameters {
        choice(name: 'ENV_TYPE', choices: ['STAGE', 'QA', 'E2E', 'CI'], description: 'Test environment')
        string(name: 'ADMIN_SERVICE_HOST', defaultValue: 'pub-ctrl-stage-api.vungle.io', description: 'Admin service host')
        string(name: 'AUTH_SERVICE_HOST', defaultValue: 'auth-qa-api.vungle.io', description: 'Auth service host')
        string(name: 'MANAGE_SERVICE_HOST', defaultValue: 'publisher-stage-api.vungle.io', description: 'Manage service host')
        string(name: 'TEST_SUITE', defaultValue: 'tests/mission_ctrl/admin/', description: 'Test suite')
        choice(name: 'EXECUTION_TYPE', choices: ['Full Regression', 'Smoke Test'], description: 'Execution type')
    }
    stages{
        stage('Prepare test env') {
            steps
            {
                echo 'Update config.json'
                withCredentials([usernamePassword(credentialsId: 'ATLAS_QA_DB', usernameVariable: 'DB_USERNAME', passwordVariable: 'DB_PASSWORD')]) 
                {
                    sh 'python3 update_config.py --env_type=${ENV_TYPE} --db_username=${DB_USERNAME} --db_password=${DB_PASSWORD} --admin_service_host=${ADMIN_SERVICE_HOST} --manage_service_host=${MANAGE_SERVICE_HOST} --auth_service_host=${AUTH_SERVICE_HOST}'
                }
            }
        }
        stage('Execute test automation') {
            parallel {
                stage('Smoke Test') {
                    when {expression {params.EXECUTION_TYPE == 'Smoke Test'}}
                    steps {
                        echo 'Execute smoke test...'
                        sh 'py.test ${TEST_SUITE} --allure-severities blocker --alluredir=${ALLURE_RESULT_PATH} || true'
                        sh 'chmod -R o+xw ${ALLURE_RESULT_PATH}'
                    }
                }
                stage('Full Regression') {
                    when {expression {params.EXECUTION_TYPE == 'Full Regression'}}
                    steps {
                        echo 'Execute full regression test...'
                        sh 'py.test ${TEST_SUITE} --alluredir=${ALLURE_RESULT_PATH} || true'
                        sh 'chmod -R o+xw ${ALLURE_RESULT_PATH}'
                    }
                }
            }
        }
        stage('Generate allure report') {
            steps{
                script {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'target/allure-result']]])
                }
            }
        }
    }
    post {
        success {
            slackSend (channel: '#publisher-application-beijing',
                       teamDomain: 'vungle', 
                       tokenCredentialId: 'jenkins_QA_slack_token', 
                       color: '#00FF00', 
                       message: "*Test Job:* ${env.JOB_NAME}\n*Build Num:* ${env.BUILD_NUMBER}\n*Execution Type:* ${env.EXECUTION_TYPE}\n*Admin Service Host:* ${ADMIN_SERVICE_HOST}\n*Manage Service Host:* ${MANAGE_SERVICE_HOST}\n*Test Result:* :green_light:Passed\n*Test Duration:* ${currentBuild.durationString}\n*Test Report:* ${env.BUILD_URL}"
                    )
        }
        unstable {
            slackSend (channel: "#publisher-application-beijing",
                       teamDomain: 'vungle',
                       tokenCredentialId: 'jenkins_QA_slack_token',
                       color: '#F8DE00',
                       message: "*Test Job:* ${env.JOB_NAME}\n*Build Num:* ${env.BUILD_NUMBER}\n*Execution Type:* ${env.EXECUTION_TYPE}\n*Admin Service Host:* ${ADMIN_SERVICE_HOST}\n*Manage Service Host:* ${MANAGE_SERVICE_HOST}\n*Test Result:* :red_light:Failed\n*Test Duration:* ${currentBuild.durationString}\n*Test Report:* ${env.BUILD_URL}"
            )
        }
        failure {
            slackSend (channel: "#publisher-application-beijing",
                       teamDomain: 'vungle',
                       tokenCredentialId: 'jenkins_QA_slack_token',
                       color: '#FF0000',
                       message: "The job ${env.JOB_NAME} is borken, Please check the reason. (${env.BUILD_URL})"
            )
        }
    }
}