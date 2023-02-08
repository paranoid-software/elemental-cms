import json
import os
import pathlib
from datetime import datetime
from shutil import copyfile

import click
from click import Context

from elementalcms import ElementalContext, __version__
from elementalcms.core import FlaskContext, MongoDbContext

from elementalcms.management import GlobalDeps, Pages, Snippets, Static, Media
from elementalcms.persistence import MongoDbConnectionManager
from elementalcms.services.sessions import CreateExpirationIndex


@click.group()
@click.pass_context
def cli(ctx: Context):
    """Elemental CMS management CLI"""
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand in ['version', 'init']:
        return

    if not os.path.exists('.elemental'):
        click.echo('It appears the CMS is not initialized, please run init command.')
        exit(1)

    with open('.elemental', encoding='utf-8') as init_file_content:
        init_metadata = json.load(init_file_content)
        if 'configFilePath' not in init_metadata:
            click.echo('Initialization meta appears to be wrong, please run init command again.')
            return

    config_filepath = init_metadata['configFilePath']

    if not os.path.exists(config_filepath):
        click.echo(f'Init meta reference {config_filepath} file which does not exist.')
        exit(1)

    with open(config_filepath, encoding='utf-8') as config_file_content:
        config_file = json.load(config_file_content)

        if 'cmsCoreContext' not in config_file:
            click.echo('Incomplete settings file. cmsCoreContext section is missing.')
            exit(1)

        if 'cmsDbContext' not in config_file:
            click.echo('Incomplete settings file. cmsDbContext section is missing.')
            exit(1)

        cms_core_context = FlaskContext(config_file['cmsCoreContext'])
        cms_db_context = MongoDbContext(config_file['cmsDbContext'])
        ctx.obj['elemental_context'] = ElementalContext(cms_core_context, cms_db_context)


@cli.command('version')
def version():
    click.echo(__version__)


@cli.command('init')
@click.option('--with-config-file',
              '-c',
              'config_filepath',
              nargs=1,
              required=True,
              help='Path for the config file that will be used to create the context for every following '
                   'command.')
def init(config_filepath):

    if not os.path.exists(config_filepath):
        click.echo(f'{config_filepath} does not exist.')
        return

    init_metadata = {
        'configFilePath': config_filepath
    }

    with open(config_filepath, encoding='utf-8') as config_file_content:
        config_file = json.load(config_file_content)

        if 'cmsCoreContext' not in config_file:
            click.echo('Incomplete settings file. cmsCoreContext section is missing.')
            exit(1)

        if 'cmsDbContext' not in config_file:
            click.echo('Incomplete settings file. cmsDbContext section is missing.')
            exit(1)

        cms_core_context = FlaskContext(config_file['cmsCoreContext'])
        cms_db_context = MongoDbContext(config_file['cmsDbContext'])

    context: ElementalContext = ElementalContext(cms_core_context, cms_db_context)

    db_name = MongoDbConnectionManager.get_db_name(context.cms_db_context)
    if db_name is None:
        click.echo('The database context has some problems, check your config file and or mongo server state.')
        return

    click.echo(f'Initializing Elemental CMS for db {db_name}...')

    CreateExpirationIndex(context.cms_db_context).execute()

    for path in [context.cms_core_context.MEDIA_FOLDER,
                 context.cms_core_context.STATIC_FOLDER,
                 'templates',
                 'translations',
                 context.cms_core_context.GLOBAL_DEPS_FOLDER.replace('/', os.path.sep),
                 context.cms_core_context.SNIPPETS_FOLDER.replace('/', os.path.sep),
                 context.cms_core_context.PAGES_FOLDER.replace('/', os.path.sep)]:
        os.makedirs(path, exist_ok=True)

    lib_root_path = pathlib.Path(__file__).resolve().parent
    path_parts = str(lib_root_path).split(os.sep)
    lib_path = os.sep.join(path_parts[1:-1])
    if not os.path.exists(os.path.join('templates', 'base.html')):
        copyfile(os.path.join(os.path.sep, lib_path, 'templates', 'base.html'),
                 os.path.join('templates', 'base.html'))
    init_metadata['lastUpdateTime'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    init_file = open('.elemental', mode='w', encoding='utf-8')
    init_file.write(json.dumps(init_metadata, indent=4))
    init_file.close()
    click.echo('Initialization completed...')


cli.add_command(GlobalDeps())
cli.add_command(Snippets())
cli.add_command(Pages())
cli.add_command(Static())
cli.add_command(Media())
