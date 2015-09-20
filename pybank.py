### built in
import operator # sort table
import os # config paths
import threading

### setuptools
import yaml # config file
import click # cli
from appdirs import AppDirs # config file
from tabulate import tabulate # click.echo( nice table )



#pip install pyyaml appdirs requests beautifulsoup4 tabulate click

dirs = AppDirs("pybank", "rdkr.uk")
settingsConfigFilename = os.path.join(dirs.user_config_dir, 'settings.yml')
accountsConfigFilename = os.path.join(dirs.user_config_dir, 'accounts.yml')

accountsConfig = yaml.safe_load(open(accountsConfigFilename))


def get_accounts():

    accounts = []
    accProviderThreads = []

    # set up lists for accounts and account providers

    for accProvider, accProviderDetails in accountsConfig.items():

        exec( 'from banks.' + accProvider + ' import ' + accProvider )
        
        accProviderThread = eval( accProvider + '()')
        accProviderThread.set_login_params(accProviderDetails)

        accProviderThreads.append(accProviderThread)
        accProviderThread.start()

    for accProviderThread in accProviderThreads:
        accProviderThread.join()
        accounts.extend(accProviderThread.get_accounts())

    print_table(accounts)

def print_table(accounts):

    totalAvailable = 0.0

    header = ['bank', 'name', 'available'] # 'sort', 'number',
    body = []

    for acc in accounts:

        try:

            row = []

            # for each table header item, insert entry from each account dictionary to row
            for entry in header:
                if entry in acc:
                    row.append(acc[entry])
                else:
                    row.append('')       
                

            body.append(row)

            totalAvailable += acc['available']

        except:
            pass

    footer = ['TOTAL', '', totalAvailable]

    table = []
    table.append(header)
    table.extend(sorted(body, key=operator.itemgetter(0)))
    table.append(footer)

    click.echo()
    click.echo(tabulate(table, headers="firstrow"))
    click.echo()

@click.group()
@click.option('--verbose', is_flag=True, help='Runs in vebrose mode')
def cli(verbose):
    pass    

@cli.command()
def get():
    get_accounts()

@cli.command()
def setup():
    pass
    # if command == 'setup':
    #     setup()
    # else:

    #     try:
    #         settingsConfig = yaml.safe_load(open(settingsConfigFilename))
    #     except:
    #         click.echo('Could not open settings config (' + settingsConfigFilename + ')')

    #     try:
    #         accountsConfig = yaml.safe_load(open(accountsConfigFilename))
    #     except:
    #         click.echo('Could not open accounts config (' + accountsConfigFilename + ')')