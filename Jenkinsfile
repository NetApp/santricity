//@Library('hub') _
@Library("hub")_
setupBlackduckBuildParameters()

//def hubProjectName = "esg" // "esg"
//def hubProjectVersion = "ansible-santricity-collection-1.1" // "smmonitor-${env.BRANCH_NAME}"
def hubProjectName = "ansible-santricity-collection"
def hubProjectVersion = "1.1"


pipeline {
    agent {
        label "linux-docker"
    }

    options {
        timestamps()
        timeout(time: 60, unit: "MINUTES")
    }

    stages {
        stage("Hub scan") {
            // NOTE: Using the declarative 'agent { docker image ...}' tends to run on a different node. So don't use it here.
            steps {
                script {
                    docker.image("docker.netapp.com/mswbuild/openjdk8:8u181-8").inside {
                        hubScanProject(
                            "${hubProjectName}",
                            "${hubProjectVersion}",
                            productionScan: false,
                        )
                    }
                }
            }
        }
    }

    post {
        always {
            deleteDir()
        }
    }
}
