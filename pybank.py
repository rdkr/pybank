#pip install pyyaml appdirs requests beautifulsoup4 tabulate

import threading

# config file imports
import yaml
from appdirs import AppDirs

from tabulate import tabulate

from account import account

# get config from user config file 

dirs = AppDirs("pybank", "rdkr.uk")
config = yaml.safe_load( \
    open(dirs.user_config_dir + '/config.yml'))

# set up lists for accounts and account providers

accounts = []

accProviderThreads = []

for accProvider, accProviderDetails in config.items():

    exec( 'from banks.' + accProvider + ' import ' + accProvider )
    
    accProviderThread = eval( accProvider + '()')
    accProviderThread.set_login_params(accProviderDetails)

    accProviderThreads.append(accProviderThread)
    accProviderThread.start()

for accProviderThread in accProviderThreads:
    print(accProviderThread)    
    accProviderThread.join()
    accounts.extend(accProviderThread.get_accounts())

print(tabulate(accounts, headers="keys"))