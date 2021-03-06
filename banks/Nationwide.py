from threading import Thread
import requests
import time
from bs4 import BeautifulSoup
from utils import get_num

class Nationwide(Thread):

    accounts = []

    def __init__(self):

        Thread.__init__(self)

    def set_login_params(self, login_dict):

        self.user = login_dict['user']
        self.pswd = login_dict['pswd']
        self.info = login_dict['info']

    def run(self):

        s = requests.Session() # new requests session
        s.headers.update({'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'})

        try:
            r = self.login1(s)
            r = self.login2(s, r)
            r = self.main_page(s, r)
        except:
            import traceback
            traceback.print_exc()

            acc = {'bank': 'Nationwide'}

            acc['name'] = 'error'

            acc['balance'] = 0
            acc['available'] = 0

            self.accounts.append(acc)

    def get_accounts(self):
        return self.accounts

    def login1(self, s):

        ## login 1 - customer number

        # get login page (contains form token)
        r = s.get('https://onlinebanking.nationwide.co.uk/AccessManagement/Login')

        # get all form fields, put in dictionary d - # http://stackoverflow.com/a/32074666# new beautifulsoup parser
        soup = BeautifulSoup(r.text, 'html.parser')
        d = {e['name']: e.get('value', '') for e in soup.find_all('input', {'name': True})}

        # add customer number to form fields
        d['CustomerNumber'] = self.user

        # post to login page with dictionary as header data. response contains cookies
        return s.post("https://onlinebanking.nationwide.co.uk/AccessManagement/Login", data=d)

    def login2(self, s, r):

        ## login 2 - memorable info and passnumber characters

        # get page for non card reader login
        r = s.get('https://onlinebanking.nationwide.co.uk/AccessManagement/Login/NonRCALogin')

        # get all form fields, put in dictionary d - # http://stackoverflow.com/a/32074666
        soup = BeautifulSoup(r.text, 'html.parser')
        d = {e['name']: e.get('value', '') for e in soup.find_all('input', {'name': True})}

        # get the character position of the requested pass number characters. removes all non digits text in the field label

        # field labels in form
        char1label = "firstSelect"
        char2label = "secondSelect"
        char3label = "thirdSelect"

        # find the requested character index from login page (index starts at 1)
        char = [ int(''.join(c for c in soup.find('label',{'for':char1label}).text if c.isdigit())) \
                ,int(''.join(c for c in soup.find('label',{'for':char2label}).text if c.isdigit())) \
                ,int(''.join(c for c in soup.find('label',{'for':char3label}).text if c.isdigit()))]

        # add corresponding memorable info character to post data
        d['SubmittedPassnumber1'] = self.info[char[0] - 1]
        d['SubmittedPassnumber2'] = self.info[char[1] - 1]
        d['SubmittedPassnumber3'] = self.info[char[2] - 1]

        # add memorable info to post data
        d['SubmittedMemorableInformation'] = self.pswd

        # post to 2nd login page with dictionary as header data. r is logged in main page
        return s.post("https://onlinebanking.nationwide.co.uk/AccessManagement/Login/NonRCALogin", data=d)

    def main_page(self, s, r):
        
        soup = BeautifulSoup(r.text, 'html.parser')

        for accountEntry in soup.find_all(class_ = 'account-row'):

            # get account details and add to accounts list

            r = s.get('https://onlinebanking.nationwide.co.uk' + accountEntry.find(class_ = 'acLink')['href'])
            soup = BeautifulSoup(r.text, 'html.parser')

            accInfo = soup.find(class_ = 'stage-head-ac-info')
            accNumbers = accInfo.find('h2').get_text()
            
            acc = {'bank': 'Nationwide'}

            acc['name'] = accNumbers.splitlines()[3].lstrip()
            acc['sort'] = accNumbers.splitlines()[4].lstrip().split()[0]
            acc['number'] = accNumbers.splitlines()[4].lstrip().split()[1]
            
            acc['balance'] = get_num(accInfo.find_all('dd')[0].get_text())
            acc['available'] = get_num(accInfo.find_all('dd')[1].get_text())

            self.accounts.append(acc)

            # download transaction files

            d = {}
            d['__token'] = soup.find(id = 'transactionsfullstatementdownloadfs')['value']
            d['downloadType'] = 'Ofx'

            r = s.post('https://onlinebanking.nationwide.co.uk/Transactions/FullStatement/DownloadFS', data=d)

            filename = time.strftime('%Y%m%d') + '-' + acc['sort'] + '-' + acc['number'] + '.ofx'
            file = open(filename, 'w')
            file.write(r.text)
            file.close()