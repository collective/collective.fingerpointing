*** Settings ***
Documentation  Audit log view (@@fingerpointing-audit-log) and its user menu link.
Resource  fingerpointing.robot
Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***
The manager reads the audit log from the user menu
    Log in as manager
    The personal action links to  audit-log  ${AUDIT_LOG_URL}
    Open the audit log
    The audit log contains  user=manager
    The audit log contains  action=login

Content creations are in the audit log
    A folder is created  robot-created-folder
    Log in as manager
    Open the audit log
    The audit log contains  action=create object=
    The audit log contains  /plone/robot-created-folder>

The manager filters the audit log
    A folder is created  robot-filtered-folder
    Log in as manager
    Open the audit log
    Filter the audit log  robot-filtered-folder
    The audit log contains  /plone/robot-filtered-folder>
    The audit log does not contain  action=login
    Click link  clear
    The audit log contains  action=login

A member has no audit log
    Log in as member
    The personal action is not available  audit-log
