node() {
    def os = System.properties['os.name'].toLowerCase()
    try {
        // notifyBuild('STARTED')
        def HUDSON_URL = "${env.HUDSON_URL}"
        def SERVER_JENKINS = ""
        if (HUDSON_URL.contains("10.88.48.21")) {
            SERVER_JENKINS = "WOPR-SB 10.88.48.21"
        } else {
            SERVER_JENKINS = "WOPR-PROD-JENKINS"
        }
        stage("VALIDATE") {
          if (env.branch == "") {} else if (env.branch == "main") {} else if (env.branch == "master") {} else {

// env.EMAIL = sh(returnStdout: true, script: "python3 -c \"import wcommon as wc; wc.sendmail('${env.mailRecipients}', 'try', 'data'); exit()\"").trim() 
            env.BUILD_TIME = "${BUILD_TIMESTAMP}"



            env.validated = sh(returnStdout: true, script: "python3 -c \"import json,requests,yaml; print(yaml.dump(requests.get('http://10.88.48.21:5000/validated?branch=${env.branch}',verify=False).json()));\"").replaceAll("  ","&emsp;").replaceAll("\n","<BR>").trim()
            env.mailBody = "${env.mailBody} <BR>${env.validated}"
          }
        }
        stage("EMAIL") {
            echo "*** Prepare Workspace ***"
            env.WORKSPACE_LOCAL = sh(returnStdout: true, script: 'pwd').trim()
            env.BUILD_TIME = "${BUILD_TIMESTAMP}"
            echo "Workspace set to:" + env.WORKSPACE_LOCAL
            echo "Build time:" + env.BUILD_TIME
            env.mailBody1 = "${env.mailBody} <BR><BR>SERVER_JENKINS = ${SERVER_JENKINS} <BR>BUILD_TIMESTMAP = ${env.BUILD_TIMESTAMP} <BR>JOB = ${env.JOB_NAME} ${env.BUILD_NUMBER} <BR>"
            echo env.mailBody1
            emailext body: "${env.mailBody1}", mimeType: "text/html", subject: "${env.mailSubject}", to: "${env.mailRecipients}", replyTo: "${env.mailRecipients}"
        }
    }
    catch(e) {
        // If there was an exception thrown, the build failed
        currentBuild.result = "FAILED"
        throw e
    } finally {
        // Success or failure, always send notifications
        echo "I AM HERE"
        notifyBuild(currentBuild.result)
        echo currentBuild.result
    }
}
def formatXray(input_string, String delimiter = "\n") {
    result = ""
    for(line in input_string.split(delimiter)) {
        result = result.replaceAll("\t","    ") + "\\n" + line
        // single to double / for all
    }
    return result
}
def notifyBuild(String buildStatus = 'STARTED') {
    // build status of null means successful
    buildStatus =  buildStatus ?: 'SUCCESSFUL'
    // Default values
    def colorName = 'RED'
    def colorCode = '#FF0000'
    def summary = "${env.mailSubject}"
    def details = "https://pl-acegit01.as12083.net/arc-lab/asset-data/merge_requests/new?merge_request%5Bsource_branch%5D=${env.branch}"
    def subject = "CHECKIN TO BRANCH=${env.branch} ran validation       ${summary}        ${details}"
    def msg = "${subject}"
      // Override default values based on build status
      if (buildStatus == 'STARTED') {
        color = 'BLUE'
        colorCode = '#0000FF'
        msg = "Build: ${env.JOB_NAME} has started: ${BUILD_TIMESTAMP}"
      } else if (buildStatus == 'UNSTABLE') {
        color = 'YELLOW'
        colorCode = '#FFFF00'
        msg = "Build: ${env.JOB_NAME} was listed as unstable. Look at ${env.BUILD_URL} and Report: ${env.BUILD_URL}/cucumber-html-reports/overview-features.html"
      } else if (buildStatus == 'SUCCESSFUL') {
        color = 'GREEN'
        colorCode = '#00FF00'
      } else {
        color = 'RED'
        colorCode = '#FF0000'
      }
    // Send notifications
    slackSend baseUrl: 'https://hooks.slack.com/services/', 
    channel: 'arc-wopr', 
    color: colorCode, 
    message: msg,
    teamDomain: 'https://wow-technology.slack.com', 
    tokenCredentialId: 'Slack-Token', 
    username: 'JenkinsAutomation'
}
def sendEmail(String buildStatus = 'STARTED') {
    // build status of null means successful
    // if buildStatus is not STARTED and mailRecipients is a parameter
    buildStatus =  buildStatus ?: 'SUCCESSFUL'
    if (buildStatus != 'STARTED') {
        if (params.toString().contains("mailRecipients")) {
            def jobName = currentBuild.fullDisplayName
            emailext body: '''${SCRIPT, template="groovy-html.template"}''',
                mimeType: 'text/html',
                subject: "[Jenkins] ${jobName}",
                to: "${params.mailRecipients}",
                replyTo: "${params.mailRecipients}",
                recipientProviders: [[$class: 'CulpritsRecipientProvider']]
        }
    }
}
def scm_checkin() {
    def branch = scm.branches[0].name
    def scm_user = "${scm.userRemoteConfigs}"
    def scm_branch = scm_user.split(" ")[2] + '  HEAD:' + branch.split("/")[1]
    def inv_sync_output = sh(script: "git config credential.helper store; git add .; git commit -m ${env.BUILD_TAG}; git push ${scm_branch}", returnStdout: true)
    echo "${inv_sync_output}"
}// 
