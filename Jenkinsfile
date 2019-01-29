pipeline {
    agent any

    environment {
        FULL_DOCKER_IMAGE_NAME = 'docker-repository.codemart.ro/tvb-build'
        LATEST_TAG = 'latest'
    }

    stages {
        stage ('Build docker image') {
            steps {
                script {
                    def dockerImage = docker.build("${FULL_DOCKER_IMAGE_NAME}:${env.BUILD_ID}", 'docker')
                    dockerImage.push()
                    dockerImage.push('${LATEST_TAG}')
                }
            }
        }
        stage ('Build TVB documentation') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${LATEST_TAG}'
                }
            }
            steps {
                sh '''#!/bin/bash
                    source activate tvb-docs
                    sh install_from_svn.sh
                    cd tvb_build
                    python build_step1.py
                '''
                archiveArtifacts artifacts: 'tvb_build/build/*.zip'
                stash includes: 'tvb_build/build/*.zip', name: 'docs-website'
            }
        }
        stage ('Run tests') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${LATEST_TAG}'
                }
            }
            steps {
                sh '''#!/bin/bash
                    source activate tvb-run
                    sh install_from_svn.sh
                    service postgresql start
                    cd tvb_bin
                    bash run_tests.sh postgres
                '''
            }
        }
        stage ('Build TVB') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${LATEST_TAG}'
                }
            }
            steps {
                unstash 'docs-website'
                sh 'rm -R -f tvb_build/build/TVB_Distribution'
                sh '''#!/bin/bash
                    source activate tvb-run
                    sh install_from_svn.sh
                    cd tvb_build
                    rm -R -f build/TVB_Distribution
                    python build_from_conda.py
                '''
                archiveArtifacts artifacts: 'tvb_build/build/TVB_Linux*.zip'
                junit 'tvb_bin/TEST_OUTPUT/TEST-*RESULTS.xml'
            }
        }
        stage ('Generate coverage') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${LATEST_TAG}'
                }
            }
            steps {
                sh '''#!/bin/bash
                    source activate tvb-run
                    sh install_from_svn.sh
                    cd scientific_library
                    py.test --cov-config .coveragerc --cov=tvb tvb/tests --cov-branch --cov-report xml:TEST_OUTPUT/coverage_library.xml --junitxml=TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml
                '''
                junit 'scientific_library/TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml'
                step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'scientific_library/TEST_OUTPUT/coverage_library.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
            }
        }
    }
    post {
        changed {
            mail to: 'lia.domide@codemart.ro, paula.popa@codemart.ro',
            subject: "Jenkins Pipeline ${currentBuild.fullDisplayName} changed status",
            body: """
                Result: ${currentBuild.result}
                Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'
                Check console output at ${env.BUILD_URL}"""
        }

        success {
            echo 'Build finished successfully'
        }
    }
}