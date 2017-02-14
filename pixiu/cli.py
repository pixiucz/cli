import click
import toml
import sys


VERSION = '0.1.0'
CONFIG = 'pixiu.toml'


class Config():
    """ Configuration file abstraction """

    def __init__(self):
        self.config = None
        self.refresh(False)


    def refresh(self, required=True):
        try:
            with open(CONFIG) as config_file:
                self.config = toml.loads(config_file.read())

        except ValueError as e:
            click.echo('Configuration file error: {0}'.format(e))
            sys.exit(-1)

        except IOError:
            if (required):
                click.echo('No configuration file. Did you forget to run \'--init\' ?')
                sys.exit(-1)

    @property
    def environments(self):
        return [env for env in self.config['deployment']]

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
        click.echo('Pixiu CLI v {0}'.format(VERSION))
    elif (update):
        click.echo('Updating CLI...')
    else:
        if (init):
            click.echo('Initializing \'{0}\' project...'.format(init))

        config.refresh()

        if (install):            
            click.echo('Installing \'{0}\'...'.format(config.name))

        if (not init and deploy):
            click.echo('Deploying \'{0}\' to \'{1}\'...'.format(config.name, deploy))
