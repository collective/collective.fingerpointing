*** Settings ***
Documentation  collective.fingerpointing keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Fixture (testing.py): users manager (Manager) and member, an audit log in a temporary directory
...            shared by every test (not rolled back: check entries with unique content ids).
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${MANAGER}  manager
${MANAGER_PASSWORD}  manager123
${MEMBER}  member
${MEMBER_PASSWORD}  member123
${AUDIT_LOG_URL}  ${PLONE_URL}/@@fingerpointing-audit-log
${SETTINGS_URL}  ${PLONE_URL}/@@fingerpointing-settings


*** Keywords ***
Log in as manager
    Log in with the login form  ${MANAGER}  ${MANAGER_PASSWORD}

Log in as member
    Log in with the login form  ${MEMBER}  ${MEMBER_PASSWORD}

A folder is created
    [Documentation]  Created through the remote library (autologin), logged by the life cycle subscriber
    [Arguments]  ${id}
    Enable autologin as  Manager
    Create content  type=Folder  id=${id}  title=${id}
    Disable autologin

Open the audit log
    Go to  ${AUDIT_LOG_URL}
    Wait until element is visible  ${PAGE_TITLE}
    Element should contain  ${PAGE_TITLE}  Audit Log

Filter the audit log
    [Arguments]  ${query}
    Input text  css=input[name="query"]  ${query}
    Click button  css=input[type="submit"][value="filter"]
    Wait until element is visible  css=pre

The audit log contains
    [Arguments]  ${text}
    Element should contain  css=pre  ${text}

The audit log does not contain
    [Arguments]  ${text}
    Element should not contain  css=pre  ${text}

Open the settings from the site setup
    Go to  ${PLONE_URL}/@@overview-controlpanel
    Click link  css=a[href$="/@@fingerpointing-settings"]
    Wait until page contains element  css=#form-widgets-audit_lifecycle-0

Turn off the setting
    [Arguments]  ${name}
    Unselect checkbox  css=#form-widgets-${name}-0
    Save the form
    The status message contains  Changes saved
