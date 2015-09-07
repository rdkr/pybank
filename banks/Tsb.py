from threading import Thread
import requests
import time
from bs4 import BeautifulSoup

from account import account

class Tsb(Thread):

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
            print('EXCEPT IN TSB')
            import traceback
            traceback.print_exc()
            self.accounts.append(account('tsb', 'error', 'error', 'error', 'error', 'error'))

    def get_accounts(self):
        return self.accounts

    def login1(self, s):
        
        ## login 1 - id and password

        # get login page (contains form token)
        r = s.get('https://online.tsb.co.uk/personal/logon/login.jsp')

        # get all form fields, put in dictionary d - # http://stackoverflow.com/a/32074666
        soup = BeautifulSoup(r.text, 'html.parser')
        d = {e['name']: e.get('value', '') for e in soup.find_all('input', {'name': True})}

        # add login and password to dictionary
        d['frmLogin:strCustomerLogin_userID'] = self.user
        d['frmLogin:strCustomerLogin_pwd'] = self.pswd

        # post to login page with dictionary as header data. response contains cookies
        return s.post("https://online.tsb.co.uk/personal/primarylogin", data=d)

    def login2(self, s, r):

        ## login 2 - memorable info and passnumber characters

        # get all form fields, put in dictionary d - # http://stackoverflow.com/a/32074666
        soup = BeautifulSoup(r.text, 'html.parser')
        d = {e['name']: e.get('value', '') for e in soup.find_all('input', {'name': True})}

        # get the character position of the requested pass number characters. removes all non digits text in the field label

        # field label in form and field name in post is the same (but post data contains &nbsp;
        char1label = "frmentermemorableinformation1:strEnterMemorableInformation_memInfo1"
        char2label = "frmentermemorableinformation1:strEnterMemorableInformation_memInfo2"
        char3label = "frmentermemorableinformation1:strEnterMemorableInformation_memInfo3"

        # find the requested character index from login page (index starts at 1)
        char = [ int(''.join(c for c in soup.find('label',{'for':char1label}).text if c.isdigit())) \
                ,int(''.join(c for c in soup.find('label',{'for':char2label}).text if c.isdigit())) \
                ,int(''.join(c for c in soup.find('label',{'for':char3label}).text if c.isdigit()))]

        # add corresponding memorable info character to post data (prepend &nbsp; in login form options)
        d[char1label] = '&nbsp;' + self.info[char[0] - 1]
        d[char2label] = '&nbsp;' + self.info[char[1] - 1]
        d[char3label] = '&nbsp;' + self.info[char[2] - 1]

        # post to 2nd login page with dictionary as header data. r is logged in main page
        return s.post("https://secure.tsb.co.uk/personal/a/logon/entermemorableinformation.jsp", data=d)

    def main_page(self, s, r):
        
        soup = BeautifulSoup(r.text, 'html.parser')
      
        for accountEntry in soup.find(id = 'lstAccLst').findAll('li', recursive=False):

            # get account details and add to accounts list

            r = s.get('https://secure.tsb.co.uk' + accountEntry.find('h2').a['href'])
            soup = BeautifulSoup(r.text, 'html.parser')

            accountNumbers = soup.find(class_ = 'numbers').get_text().split(', ')
            
            acc = {}

            acc['name'] = soup.find('h1').get_text()
            acc['sort'] = accountNumbers[0].replace('-', '')
            acc['number'] = accountNumbers[1]

            acc['balance'] = self.get_num(soup.find(class_ = 'balance').get_text())
            acc['available'] = self.get_num(soup.find(class_ = 'manageMyAccountsFaShowMeAnchor {bubble : \'fundsAvailable\', pointer : \'top\'}').parent.get_text())
            
            self.accounts.append(acc)

            # download transaction files

            r = s.get('https://secure.tsb.co.uk' + soup.find(id = 'pnlgrpStatement:conS1:lkoverlay')['href'])
            soup = BeautifulSoup(r.text, 'html.parser')

            # get all form fields, put in dictionary d - # http://stackoverflow.com/a/32074666
            soup = BeautifulSoup(r.text, 'html.parser')
            d = {e['name']: e.get('value', '') for e in soup.find_all('input', {'name': True})}

            now = time.localtime(time.time())
            yearAgo = time.localtime(time.time() - 6570000) # ~ 2.5 months year ago

            d['frmTest:rdoDateRange'] = '1'
            
            d['frmTest:dtSearchFromDate'] = time.strftime('%d', yearAgo) 
            d['frmTest:dtSearchFromDate.month'] = time.strftime('%m', yearAgo) 
            d['frmTest:dtSearchFromDate.year'] = str(time.strftime('%Y', yearAgo)) 

            d['frmTest:dtSearchToDate'] = time.strftime('%d', now) 
            d['frmTest:dtSearchToDate.month'] = time.strftime('%m', now)
            d['frmTest:dtSearchToDate.year'] = str(time.strftime('%Y', now))

            d['frmTest:strExportFormatSelected'] =  'Quicken 98 and 2000 and Money (.QIF)' 
            
            r = s.post('https://secure.tsb.co.uk/personal/a/viewproductdetails/m44_exportstatement_fallback.jsp', data=d)

            filename = time.strftime('%Y%m%d') + '-' + acc['sort'] + '-' + acc['number'] + '.qif'
            file = open(filename, 'w')
            file.write(r.text)
            file.close()

    def get_num(self, x): # http://stackoverflow.com/a/10365472
        return float(''.join(ele for ele in x if ele.isdigit() or ele == '.'))