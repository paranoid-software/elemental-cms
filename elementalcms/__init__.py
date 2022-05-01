import os
import pathlib
from flask import Flask, Blueprint, request, send_from_directory, redirect, g, render_template_string, session, url_for
from flask_babel import Babel
from markupsafe import Markup

from elementalcms.core import ElementalContext
from elementalcms.extends import Applet, ActionsMapper

from elementalcms.persistence import MongoSessionInterface
from elementalcms.services.snippets import GetMe

from elementalcms.admin import admin
from elementalcms.presenter import presenter
from elementalcms.identity import identity

__version__ = "1.0.93"


class Elemental:

    def __init__(self, app: Flask, context: ElementalContext, applets: [Applet] = None):

        app.config.from_object(context.cms_core_context)

        # Passing DB Context to Blueprints
        app.config['CMS_DB_CONTEXT'] = context.cms_db_context

        translations_paths = [
            'translations',
            # Support for package translations
            f'{pathlib.Path(__file__).resolve().parent}/translations'
        ]
        app.config['BABEL_TRANSLATION_DIRECTORIES'] = ';'.join(translations_paths)

        admin.url_prefix = None if context.cms_core_context.LANGUAGE_MODE == 'single' else '/<lang_code>'
        app.register_blueprint(admin)
        presenter.url_prefix = None if context.cms_core_context.LANGUAGE_MODE == 'single' else '/<lang_code>'
        app.register_blueprint(presenter)

        app.register_blueprint(identity)

        app.register_blueprint(Blueprint('media', __name__, static_url_path='/media', static_folder=os.path.join(app.root_path, 'media')))

        for applet in applets or []:
            ActionsMapper(app).register_actions(applet.get_controllers())

        # Session support using MongoDB
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

            if 'static' in path:
                if context.cms_core_context.DEBUG and ('static/admin' in path or 'static/presenter' in path):
                    path_parts = path.strip('?').split('/')
                    index = path_parts.index('static')
                    local_path = pathlib.Path(__file__).resolve().parent
                    return send_from_directory(local_path, '/'.join(path_parts[index:]), cache_timeout=360)
                return

            if request.full_path == '/?':
                if context.cms_core_context.LANGUAGE_MODE == 'single':
                    return
                return redirect(url_for('presenter.index',
                                        lang_code=session.get("langCode", context.cms_core_context.DEFAULT_LANGUAGE)))

            if request.full_path == '/?draft=1':
                if context.cms_core_context.LANGUAGE_MODE == 'single':
                    return
                return redirect(url_for('presenter.index',
                                        lang_code=session.get("langCode", context.cms_core_context.DEFAULT_LANGUAGE),
                                        draft=1))

        @app.context_processor
        def elemental_url_for_static_processor():
            def elemental_url_for_static(file_path=''):
                return f'{context.cms_core_context.STATIC_URL}/{file_path}'
            return dict(elemental_url_for_static=elemental_url_for_static)

        @app.context_processor
        def elemental_url_for_media_processor():
            def elemental_url_for_media(file_path=''):
                return f'{context.cms_core_context.MEDIA_URL}/{file_path}'
            return dict(elemental_url_for_media=elemental_url_for_media)

        @app.context_processor
        def elemental_url_for_slug_processor():
            def elemental_url_for_slug(lang_code=None, slug=None):
                url = url_for('presenter.index',
                              lang_code=None if context.cms_core_context.LANGUAGE_MODE == 'single' else
                              (lang_code or session.get('langCode', context.cms_core_context.DEFAULT_LANGUAGE)),
                              draft=None if 'draft' not in request.args else '1')
                if slug is not None and slug.strip():
                    url = url_for('presenter.render',
                                  slug=slug,
                                  lang_code=None if context.cms_core_context.LANGUAGE_MODE == 'single' else
                                  (lang_code or session.get('langCode', context.cms_core_context.DEFAULT_LANGUAGE)),
                                  draft=None if 'draft' not in request.args else '1')
                return url
            return dict(elemental_url_for_slug=elemental_url_for_slug)

        @app.context_processor
        def render_snippet_processor():
            def render_snippet(name):
                get_me_result = GetMe(context.cms_db_context).execute(name)
                if get_me_result.is_failure():
                    raise Exception(f'There are no snippets under the name {name}')
                content = render_template_string(f'<!--{name}-->\n{get_me_result.value()["content"]}')
                return Markup(content)
            return dict(render_snippet=render_snippet)

        @app.context_processor
        def lang_code_processor():
            code = ''
            if context.cms_core_context.LANGUAGE_MODE == 'multi':
                code = session.get('langCode', context.cms_core_context.DEFAULT_LANGUAGE)
            return dict(lang_code=code)
