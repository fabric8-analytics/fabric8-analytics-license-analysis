#!/usr/bin/env groovy
@Library('github.com/msrb/cicd-pipeline-helpers')

def commitId
node('docker') {

    def image = docker.image('license-analysis-image')

    stage('Checkout') {
        checkout scm
        commitId = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()

        dir('openshift') {
            stash name: 'template', includes: 'template.yaml'
        }
    }

    stage('Build') {
        dockerCleanup()
        docker.build(image.id, '--pull --no-cache .')
    }

    if (env.BRANCH_NAME == 'master') {
        stage('Push Images') {
            docker.withRegistry('https://registry.devshift.net/') {
                image.push('latest')
                image.push(commitId)
            }
        }
    }
}

if (env.BRANCH_NAME == 'master') {
    node('oc') {

        def dcs = ['license-analysis' ]
        lock('f8a_staging') {

            stage('Deploy - stage') {
                unstash 'template'
                sh "oc --context=rh-idev process -v IMAGE_TAG=${commitId} -v CPU_REQUEST=2 -f template.yaml | oc --context=rh-idev apply -f -"
            }

            stage('End-to-End Tests') {
                def result
                try {
                    timeout(10) {
                        sleep 5
                        sh "oc logs -f dc/${dcs[0]}"
                        def e2e = build job: 'fabric8-analytics-common-master', wait: true, propagate: false, parameters: [booleanParam(name: 'runOnOpenShift', value: true)]
                        result = e2e.result
                    }
                } catch (err) {
                    error "Error: ${err}"
                } finally {
                    if (!result?.equals('SUCCESS')) {
                        dcs.each {
                            sh "oc rollback ${it}"
                        }
                        error 'End-to-End tests failed.'
                    } else {
                        echo 'End-to-End tests passed.'
                    }
                }
            }
        }
    }
}

