#!/usr/bin/python
from selenium import webdriver
from selenium.common import exceptions
import os
import getpass
import time

def WaitForXPathUI(Browser, xpath):
    while True:
        time.sleep(1)
        try:
            ui = Browser.find_element_by_xpath(xpath)
            if ui and ui.is_displayed():
                return ui
        except exceptions.NoSuchElementException:
            pass

def PrepareFirefox():
    p = webdriver.FirefoxProfile()
    p.set_preference('browser.download.folderList', 2) # custom location
    p.set_preference('browser.download.manager.showWhenStarting', False)
    p.set_preference('browser.download.dir', '/root/Desktop')
    p.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')
    return webdriver.Firefox(p)

print 'Activate google developer account'
username = raw_input('Gmail: ').strip()
password = getpass.getpass('Password: ').strip()

Browser = PrepareFirefox()
Browser.get('https://console.developers.google.com/start/api?id=drive')

print "Waiting for username page"
Browser.find_element_by_xpath('//*[@id="identifierId"]').send_keys(username)
Browser.find_element_by_xpath('//*[@id="identifierNext"]').click()

print "Waiting for password page"
WaitForXPathUI(Browser, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(password)
Browser.find_element_by_xpath('//*[@id="passwordNext"]').click()

print "Waiting for build project"
WaitForXPathUI(Browser, '//*[@id="p6n-api-flow-continue"]').click()

print "Waiting for go to credentials"
WaitForXPathUI(Browser, '//*[@id="p6n-api-flow-to-credentials"]').click()

print "Waiting for cancel button"
WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/div/form/div[2]/div/jfk-button').click()

print "Waiting for OAuth consent screen"
WaitForXPathUI(Browser, '//*[@id=":6"]').click()

print "Waiting for product name input"
WaitForXPathUI(Browser, '//*[@id="p6n-consent-product-name"]').send_keys('Backup Service')

print "Waiting for save button"
time.sleep(1)
WaitForXPathUI(Browser, '//*[@id="api-consent-save"]').click()

print "Waiting for create credentials button"
WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/div[3]/div[2]/div/div').click()

print "Waiting for OAuth client ID"
WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/div[3]/div[2]/div/div/div/section[1]/div/div/div[1]/div[2]').click()

print "Waiting for Others"
WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/form/fieldset/div/div/label[6]/span').click()

print "Waiting for name input"
othername = WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/form/oauth-client-editor/ng-form/div/label/div[1]/input')
othername.clear()
othername.send_keys('Drive API Quickstart')
WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/form/div/div/button').click()

print "Waiting for OK button"
WaitForXPathUI(Browser, '/html/body/div[6]/md-dialog/md-dialog/md-dialog-actions/pan-modal-actions/pan-modal-action/a/span').click()

print "Waiting for download button"
WaitForXPathUI(Browser, '/html/body/div[2]/div[2]/div[3]/div[1]/div/md-content/div/div[2]/div/section/table/tbody/tr/td[6]/a').click()

print "Waiting for client_secret.json"
while True:
    time.sleep(1)
    fs = filter(lambda s: s.startswith("client_secret"), next(os.walk("/root/Desktop"))[2])
    if fs:
        fs = fs[0]
        break

os.rename(fs, 'client_secret.json')    

Browser.close()

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'

def get_credentials(CLIENT_SECRET_FILE="", APPLICATION_NAME='Drive API Python Quickstart'):
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~/Desktop')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
	assert CLIENT_SECRET_FILE
	flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
	flow.user_agent = APPLICATION_NAME
	if flags:
	    credentials = tools.run_flow(flow, store, flags)
	else: # Needed only for compatibility with Python 2.6
	    credentials = tools.run(flow, store)
	print 'Storing credentials to ' + credential_path
    return credentials

def AcquireDriveService(
    CLIENT_SECRET_FILE = "",
    APPLICATION_NAME = 'Drive API Python Quickstart'
):
    credentials = get_credentials(
        CLIENT_SECRET_FILE=CLIENT_SECRET_FILE,
        APPLICATION_NAME=APPLICATION_NAME
    )
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service

AcquireDriveService("client_secret.json")
os.system("tar zcvf credentials.tar.gz .credentials")
