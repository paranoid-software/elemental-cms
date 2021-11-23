import json
import os
import pathlib
from datetime import datetime
from shutil import copyfile

import click

from elementalcms import ElementalContext, __version__
from elementalcms.core import FlaskContext, MongoDbContext

from elementalcms.management import GlobalDeps, Pages, Snippets, Static, Media
from elementalcms.persistence import MongoDbConnectionManager
from elementalcms.services.sessions import CreateExpirationIndex


@click.group()
@click.option('--debug/--no-debug', default=True)
@click.pass_context
def cli(ctx, debug):
    """Elemental CMS management CLI"""
    ctx.ensure_object(dict)

    ctx.obj['debug'] = debug

    if not os.path.exists('settings'):
        click.echo('Settings folder do not exist, you need to create a settings folder and at least a debug.json '
                   'settings file to start using the CLI.')
        exit(1)

    if debug:
        if not os.path.exists('settings/debug.json'):
            click.echo('Settings file do not exist. Please create a debug settings file in order to be able to use '
                       'the CLI.')
            exit(1)
    else:
        if not os.path.exists('settings/prod.json'):
            click.echo('Settings file do not exist. Please create a production settings file in order to be able to '
                       'use the CLI.')
            exit(1)

    with open(f'settings/{"debug" if debug else "prod"}.json') as config_file:
        settings = json.load(config_file)
        if 'cmsCoreContext' not in settings:
            click.echo('Settings file incomplete.')
            exit(1)
        if 'cmsDbContext' not in settings:
            click.echo('Settings file incomplete.')
            exit(1)
        cms_core_context = FlaskContext(settings['cmsCoreContext'])
        cms_db_context = MongoDbContext(settings['cmsDbContext'])
        ctx.obj['elemental_context'] = ElementalContext(cms_core_context, cms_db_context)


@cli.command('version')
def version():
    click.echo(__version__)


@cli.command('init')
@click.pass_context
def init(ctx):

    if os.path.exists('.elemental'):
        click.echo('Elemental CMS has been already initialized.')
        return

    context: ElementalContext = ctx.obj['elemental_context']
    db_name = MongoDbConnectionManager.get_db_name(context.cms_db_context)
    if db_name is None:
        click.echo('The database context has something wrong.')
        return

    click.echo(f'Initializing Elemental CMS for db {db_name}...')

    CreateExpirationIndex(context.cms_db_context).execute()

    for path in ['media',
                 'static',
                 f'static/{context.cms_core_context.APP_NAME}',
                 'templates',
                 'translations',
                 'workspace',
                 'workspace/global_deps',
                 'workspace/snippets',
                 'workspace/pages']:
        create_folder(path)

    lib_root_path = pathlib.Path(__file__).resolve().parent
    path_parts = str(lib_root_path).split(os.sep)
    lib_path = os.sep.join(path_parts[1:-1])
    if not os.path.exists('templates/base.html'):
        copyfile(f'/{lib_path}/templates/base.html', 'templates/base.html')
    init_file = open('.elemental', mode="w", encoding="utf-8")
    init_file.write(json.dumps({
        'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, indent=4))
    init_file.close()
    click.echo('Initialization completed...')


def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)


cli.add_command(GlobalDeps())
cli.add_command(Snippets())
cli.add_command(Pages())
cli.add_command(Static())
cli.add_command(Media())
