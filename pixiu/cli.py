import click
import toml
import sys
import os
import pkg_resources


VERSION = pkg_resources.require('pixiu-cli')[0].version # version from setup.py
CONFIG = 'pixiu.toml' # projects config filename
TEMP_DIR = 'pixiu-cli-temp' # temporary fir for updating CLI
def BOOTSTRAP(platform):
    """ Config init template """
    import datetime

    return {
        'project': {
            'initialized': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'platform': platform,
            'name': os.getcwd().split(os.sep)[-1]
        },
        'database': {
            'localhost': {
                'engine': 'sqlite'
            }
        },
        'deployment': {
            'test_localhost': {
                'database': 'database.localhost'
            }
        }
    }
def REPO():
    """ 
    Url from setup.py 
    Implementation from http://stackoverflow.com/a/38659619 
    """
    d = pkg_resources.get_distribution('pixiu-cli')
    metadata = d._get_metadata(d.PKG_INFO)
    home_page = [m for m in metadata if m.startswith('Home-page:')]
    return home_page[0].split(':', 1)[1].strip()


# helper functions
def error(msg):
    click.echo(click.style(msg, bg='red', fg='white'))
    sys.exit(-1)


class Updater():
    """ Self updater """

    def __init__(self):    
        self.version = VERSION


    def update(self):
        import subprocess
        import shutil

        if (0 != subprocess.call(['git', 'clone', REPO(), TEMP_DIR])):
            raise Exception('Failed to clone')

        if (0 != subprocess.call(['pipsi', 'upgrade', TEMP_DIR])):
            raise Exception('Failed to upgrade package with pipsi')

        shutil.rmtree(TEMP_DIR)


class Config():
    """ Configuration file abstraction """

    def __init__(self):
        self.config = None
        self.sync(False)


    def sync(self, required=True):
        try:
            # write sync
            if (self.config): 
                with open(CONFIG, 'w') as config_file:
                    config_file.write(toml.dumps(self.config))
            # read sync
            else: 
                with open(CONFIG) as config_file:
                    self.config = toml.loads(config_file.read())

        except ValueError as e:
            error('Configuration file error: {0}'.format(e))            

        except IOError:
            if (required):
                error('No configuration file. Did you forget to run \'--init\' ?')


    def bootstrap(self, platform):
        self.config = BOOTSTRAP(platform)


    @property
    def environments(self):
        return [env for env in self.config['deployment']] if self.config else []


    @property
    def name(self):
        return self.config['project']['name']

config = Config()


@click.command()
@click.option('--init', '-i', type=click.Choice(['october', 'django']), help='Initialize new project.')
@click.option('--install', '-n', is_flag=True, help='Install project and it\'s dependencies.')
@click.option('--deploy', '-d', type=click.Choice(config.environments), help='Deploy to environment.')
@click.option('--info', '-f', is_flag=True, help='Print information about deployed environment.')
@click.option('--update', '-u', is_flag=True, help='Update and upgrade CLI.')
@click.option('--version', '-e', is_flag=True, help='Show CLI version.')
def main(init, install, deploy, info, update, version):
    if (version):
        click.echo('Pixiu CLI v{0}'.format(VERSION))

    elif (update):
        click.echo('Updating CLI (current v{0})...'.format(VERSION))
        updater = Updater()
        try:
            updater.update()
        except Exception as e:
            error('Failed to update: {0}'.format(e))

    else:
        if (init):
            click.echo('Initializing \'{0}\' project...'.format(init))
            config.bootstrap(init)
            config.sync()        

        if (install):            
            click.echo('Installing \'{0}\'...'.format(config.name))

        if (not init and deploy):
            click.echo('Deploying \'{0}\' to \'{1}\'...'.format(config.name, deploy))
            config.sync()
