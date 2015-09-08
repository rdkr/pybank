import threading

import yaml # config file
import click # cli

from appdirs import AppDirs # config file
from tabulate import tabulate # print nice table
from operator import itemgetter

#pip install pyyaml appdirs requests beautifulsoup4 tabulate click

@click.command()
def main():

    # set up lists for accounts and account providers

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

def print_table():

    totalAvailable = 0.0

    header = ['bank', 'name', 'available'] # 'sort', 'number',
    body = []

    for acc in accounts:

        row = []

        # for each table header item, insert entry from each account dictionary to row
        for entry in header:
            if entry in acc:
                row.append(acc[entry])
            else:
                row.append('')       
            

        body.append(row)

        totalAvailable += acc['available']

    
    footer = ['TOTAL', '', totalAvailable]

    table = []
    table.append(header)
    table.extend(sorted(body, key=itemgetter(0)))
    table.append(footer)

    print()
    print(tabulate(table, headers="firstrow"))
    print()

accounts = []
accProviderThreads = []

dirs = AppDirs("pybank", "rdkr.uk")
config = yaml.safe_load(open(dirs.user_config_dir + '/config.yml'))

if __name__ == '__main__':
    main()