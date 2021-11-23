import os
import pathlib
from flask import Flask, request, send_from_directory, redirect, g, render_template_string
from flask_babel import Babel
from jinja2 import Markup

from elementalcms.core import ElementalContext

from elementalcms.admin.views import admin
from elementalcms.persistence import MongoSessionInterface
from elementalcms.presenter.views import presenter
from elementalcms.services.snippets import GetMe

__version__ = "1.0.61"


class Elemental:
    def __init__(self, app: Flask, context: ElementalContext):

        app.config.from_object(context.cms_core_context)

        # Passing DB Context to Blueprints
        app.config['CMS_DB_CONTEXT'] = context.cms_db_context

        # Support for package translations
        translations_paths = [
            'translations',
            f'{pathlib.Path(__file__).resolve().parent}/translations'
        ]
        app.config['BABEL_TRANSLATION_DIRECTORIES'] = ';'.join(translations_paths)

        admin.url_prefix = None if context.cms_core_context.LANGUAGE_MODE == 'single' else '/<lang_code>'
        app.register_blueprint(admin)
        presenter.url_prefix = None if context.cms_core_context.LANGUAGE_MODE == 'single' else '/<lang_code>'
        app.register_blueprint(presenter)
        app.session_interface = MongoSessionInterface(context.cms_db_context)

        babel = Babel(app)

        @babel.localeselector
        def get_locale():
            if not g.get('lang_code', None):
                g.lang_code = request.accept_languages.best_match(context.cms_core_context.LANGUAGES)
            return g.lang_code

        @app.before_request
        def before_request():
            path = request.full_path

            if 'media' in path:
                if context.cms_core_context.DEBUG:
                    path_parts = path.strip('?').split('/')
                    folders = '/'.join(path_parts[0:len(path_parts) - 1])
                    local_path = os.path.join(app.root_path, folders.lstrip('/'))
                    return send_from_directory(local_path, path_parts[-1])
                return redirect(f'{context.cms_core_context.MEDIA_URL}{path.replace("/media", "")}')

            if 'static' in path:
                if context.cms_core_context.DEBUG and ('static/admin' in path or 'static/presenter' in path):
                    path_parts = path.strip('?').split('/')
                    local_path = pathlib.Path(__file__).resolve().parent
                    return send_from_directory(local_path, '/'.join(path_parts[1:]))
                return

            if request.full_path == '/?':
                if context.cms_core_context.LANGUAGE_MODE == 'single':
                    return
                return redirect(f'/{context.cms_core_context.DEFAULT_LANGUAGE}')

        @app.context_processor
        def elemental_static_url_for_processor():
            def elemental_static_url_for(file_path=''):
                return f'{context.cms_core_context.STATIC_URL}/{file_path}'

            return dict(elemental_static_url_for=elemental_static_url_for)

        @app.context_processor
        def elemental_media_url_for_processor():
            def elemental_media_url_for(file_path=''):
                return f'{context.cms_core_context.MEDIA_URL}/{file_path}'

            return dict(elemental_media_url_for=elemental_media_url_for)

        @app.context_processor
        def render_snippet_processor():
            def render_snippet(name):
                get_me_result = GetMe(context.cms_db_context).execute(name)
                if get_me_result.is_failure():
                    raise Exception(f'There is no snippet under the name {name}')
                content = render_template_string(get_me_result.value()['content'])
                return Markup(content)

            return dict(render_snippet=render_snippet)
