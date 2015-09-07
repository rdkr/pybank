#pip install pyyaml appdirs requests beautifulsoup4

import threading

# config file imports
import yaml
from appdirs import AppDirs

import account

# get config from user config file 

dirs = AppDirs("pybank", "rdkr.uk")
config = yaml.safe_load( \
    open(dirs.user_config_dir + '/config.yml'))

# set up lists for accounts and account providers

accounts = []

accProviderThreads = []


for accProvider, accProviderDetails in config.items():

    print('1')
    exec( 'from banks.' + accProvider + ' import ' + accProvider )
    values = []
    
    for key, value in accProviderDetails.items():
        values.append('\'' + value + '\'')

    accProviderThread = eval( accProvider + '(' + ','.join(values) + ')')
    accProviderThreads.append(accProviderThread)
    accProviderThread.start()


for accProviderThread in accProviderThreads:
    print(accProviderThread)    
    accProviderThread.join()
    accounts.extend(accProviderThread.get_accounts())


print(accounts)
    
    #print(acc)

        #acc = print    ( accProvider + '.' + accProvider + '(' + accDetails + ')')
# tsb:


#threading.Thread(target = tsb.do).start()
#threading.Thread(target = nationwide.do).start()accProvider + '.' + 
