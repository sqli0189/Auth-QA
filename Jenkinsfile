pipeline{
    agent { label 'bj-dashboard-qa' }
    environment {
        ALLURE_RESULT_PATH = './target/allure-result'
    }
    stages{
        stage('Prepare test environment') {
            steps{
                sh '''
                    echo 'Update config.json'
                    python3 update_config.py --db_host=${DB_HOST} --db_port=${DB_PORT} --db_name=${DB_NAME} --env_type=${ENV_TYPE} --db_username=${DB_USERNAME} --db_password=${DB_PASSWORD} --admin_service_host=${ADMIN_SERVICE_HOST} --manage_service_host=${MANAGE_SERVICE_HOST} --auth_service_host=${AUTH_SERVICE_HOST}
                    echo 'Remove test-results folder generated last run'
                    rm -rf ${ALLURE_RESULT_PATH}
                '''
            }
        }
        stage('Execute Automation Test') {
            steps{
                echo 'Execute full automation test...'
                sh '''
                    py.test --alluredir=${ALLURE_RESULT_PATH} || true
                '''
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
            slackSend (color: '#00FF00', message: "*Test Job:* ${env.JOB_NAME}\n*Build Num:* ${env.BUILD_NUMBER}\n*Admin Service Host:* ${ADMIN_SERVICE_HOST}\n*Manage Service Host:* ${MANAGE_SERVICE_HOST}\n*Test Result:* :green_light:Passed\n*Test Duration:* ${currentBuild.durationString}\n*Test Report:* ${env.BUILD_URL}")
        }
        unstable {
            slackSend (color: '#F8DE00', message: "*Test Job:* ${env.JOB_NAME}\n*Build Num:* ${env.BUILD_NUMBER}\n*Admin Service Host:* ${ADMIN_SERVICE_HOST}\n*Manage Service Host:* ${MANAGE_SERVICE_HOST}\n*Test Result:* :red_light:Failed\n*Test Duration:* ${currentBuild.durationString}\n*Test Report:* ${env.BUILD_URL}")
        }
        failure {
            slackSend (color: '#FF0000', message: "The job ${env.JOB_NAME} is borken, Please check the reason. (${env.BUILD_URL})")
        }
    }
}