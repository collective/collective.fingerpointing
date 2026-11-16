*** Settings ***
Documentation  Control panel (@@fingerpointing-settings) of the Site Setup.
Resource  fingerpointing.robot
Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***
The manager turns off the content life cycle audit
    A folder is created  robot-before-folder
    Log in as manager
    Open the settings from the site setup
    Turn off the setting  audit_lifecycle
    A folder is created  robot-after-folder
    Log in as manager
    Open the audit log
    The audit log contains  /plone/robot-before-folder>
    The audit log does not contain  /plone/robot-after-folder>
    The audit log contains  IFingerPointingSettings.audit_lifecycle> value=False
