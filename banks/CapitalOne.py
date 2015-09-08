from threading import Thread
import requests
import time
from bs4 import BeautifulSoup
from utils import get_num

class CapitalOne(Thread):

    accounts = []

    def __init__(self):

        Thread.__init__(self)

    def set_login_params(self, login_dict):

        self.user = login_dict['user']
        self.info = login_dict['info']

    def run(self):

        s = requests.Session() # new requests session
        s.headers.update({'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'})

        try:
            r = self.login(s)
            r = self.main_page(s, r)
        except:
            import traceback
            traceback.print_exc()
            self.accounts.append({'name': 'error'})

    def get_accounts(self):
        return self.accounts

    def login(self, s):
        
        ## login - id and info

        # get login page (contains form token)
        r = s.get('https://www.capitaloneonline.co.uk/CapitalOne_Consumer/Login.do')

        # get all form fields, put in dictionary d - # http://stackoverflow.com/a/32074666
        soup = BeautifulSoup(r.text, 'html.parser')
        d = {e['name']: e.get('value', '') for e in soup.find_all('input', {'name': True})}

        d['username'] = self.user

        # get the character position of the requested pass number characters. removes all non digits text in the field label

        # field label in form and field name in post is the same (but post data contains &nbsp;
        char1label = "password.randomCharacter0"
        char2label = "password.randomCharacter1"
        char3label = "password.randomCharacter2"

        # find the requested character index from login page (index starts at 1)
        char = [ int(''.join(c for c in soup.find('input',{'name':char1label}).parent.text if c.isdigit())) \
                ,int(''.join(c for c in soup.find('input',{'name':char2label}).parent.text if c.isdigit())) \
                ,int(''.join(c for c in soup.find('input',{'name':char3label}).parent.text if c.isdigit())) ]

        # add corresponding memorable info character to post data (prepend &nbsp; in login form options)
        d[char1label] = self.info[char[0] - 1]
        d[char2label] = self.info[char[1] - 1]
        d[char3label] = self.info[char[2] - 1]

        # post to login page with dictionary as header data. r is logged in main page
        return s.post("https://www.capitaloneonline.co.uk/CapitalOne_Consumer/ProcessLogin.do", data=d)

    def main_page(self, s, r):
        
        soup = BeautifulSoup(r.text, 'html.parser')
     
        acc = {'bank': 'Capital One'}

        acc['original_available'] = get_num(soup.find(text = 'Available to spend').parent.parent.find('div').text)
        acc['limit'] = get_num(soup.find(text = 'Credit limit').parent.parent.text)
        acc['balance'] = get_num(soup.find(text = 'Current balance').parent.parent.text)

        acc['available'] = None

        # get available in terms of debit
        # float precision safe comparison
        if abs(acc['original_available'] == acc['balance']) <= 0.01:
            acc['available'] = -acc['balance']
        else:
            acc['available'] =  acc['original_available'] - acc['limit']

        acc['name'] = 'Capital One'

        self.accounts.append(acc)

        # download transaction files

        r = s.get('https://www.capitaloneonline.co.uk/CapitalOne_Consumer/Transactions.do')
        soup = BeautifulSoup(r.text, 'html.parser')

        d = {}
        d['org.apache.struts.taglib.html.TOKEN'] = \
            soup.find('input',{'name': 'org.apache.struts.taglib.html.TOKEN'})['value']
        d['downloadType'] = 'qif'

        r = s.post('https://www.capitaloneonline.co.uk/CapitalOne_Consumer/DownLoadTransaction.do', data=d)

        #filename = time.strftime('%Y%m%d') + '-' + acc['sort'] + '-' + acc['number'] + '.ofx'
        #file = open(filename, 'w')
        file = open('cap1.qif', 'w')
        file.write(r.text)
        file.close()