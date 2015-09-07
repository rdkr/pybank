#pip install pyyaml appdirs requests beautifulsoup4 tabulate

import threading

# config file imports
import yaml
from appdirs import AppDirs

from tabulate import tabulate

def print_table():

    table = [['bank', 'name', 'available']] # 'sort', 'number',

    totalAvailable = 0.0

    for acc in accounts:

        row = []

        # for each table header item, insert entry from each account dictionary to row
        for entry in table[0]:
            if entry in acc:
                row.append(acc[entry])
            else:
                row.append('')       
            

        table.append(row)

        totalAvailable += acc['available']

    table.append(['TOTAL', '', totalAvailable])

    print()
    print(tabulate(table, headers="firstrow"))
    print()



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
    accProviderThread.join()
    accounts.extend(accProviderThread.get_accounts())

print_table()