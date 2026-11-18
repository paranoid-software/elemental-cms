import io
import json
import os

import pytest
from assertpy import assert_that
from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from flask import Flask

from elementalcms import Elemental, ElementalContext
from elementalcms.core import FlaskContext, MongoDbContext

SOURCE = 'Sign out'
SPANISH = 'Cerrar sesión'


def write(path, content, mode='w'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(content)


def build_site(root, language_mode, languages, default_language, translated=True):
    """A site on disk, served in design mode: one home page per language whose only content is a
    translatable string, and a Spanish catalog for it unless the site carries no translations."""
    root = str(root)
    write(f'{root}/templates/base.html', '{% block content %}{% endblock %}')
    for language in languages:
        write(f'{root}/workspace/pages/{language}/home.json', json.dumps({
            'name': 'home', 'language': language, 'title': 'Home', 'description': '',
            'isHome': True, 'baseTemplate': 'base.html', 'cssDeps': [], 'jsDeps': []
        }))
        write(f'{root}/workspace/pages/{language}/home.html',
              f'<p id="page">{language}</p><p id="string">{{{{ _("{SOURCE}") }}}}</p>')
    os.makedirs(f'{root}/workspace/global_deps', exist_ok=True)
    os.makedirs(f'{root}/workspace/snippets', exist_ok=True)
    if translated:
        catalog = Catalog(locale='es')
        catalog.add(SOURCE, SPANISH)
        buffer = io.BytesIO()
        write_mo(buffer, catalog)
        write(f'{root}/translations/es/LC_MESSAGES/messages.mo', buffer.getvalue(), mode='wb')

    app = Flask('site', root_path=root, template_folder='templates')
    Elemental(app, ElementalContext(
        FlaskContext({
            'LANGUAGES': languages,
            'DEFAULT_LANGUAGE': default_language,
            'LANGUAGE_MODE': language_mode,
            'DESIGN_MODE_ENABLED': True,
            'SESSION_STORAGE_ENABLED': False,
            'GLOBAL_DEPS_FOLDER': f'{root}/workspace/global_deps',
            'PAGES_FOLDER': f'{root}/workspace/pages',
            'SNIPPETS_FOLDER': f'{root}/workspace/snippets',
        }),
        MongoDbContext({'id': 'site', 'connectionString': 'mongodb://localhost:27017', 'databaseName': 'site'})))

    # A route outside the presenter, as an applet's would be.
    @app.route('/api/string')
    def string():
        from flask_babel import gettext
        return gettext(SOURCE)

    return app


def get(app, path, accept_language=None):
    headers = {'Accept-Language': accept_language} if accept_language else {}
    with app.test_client() as client:
        return client.get(path, headers=headers, follow_redirects=True)


class TestRenderingStringsShould:

    @pytest.mark.parametrize('accept_language', ['en-US,en;q=0.9', 'fr-FR,fr;q=0.9', None])
    def test_use_the_sites_language_in_single_mode_for_a_browser_it_cannot_match(self, tmp_path, accept_language):
        app = build_site(tmp_path, 'single', ['es'], 'es')
        html = get(app, '/', accept_language).get_data(as_text=True)
        assert_that(html).contains('<p id="page">es</p>')
        assert_that(html).contains(f'<p id="string">{SPANISH}</p>')

    def test_use_the_sites_language_in_single_mode_outside_the_presenter_too(self, tmp_path):
        app = build_site(tmp_path, 'single', ['es'], 'es')
        assert_that(get(app, '/api/string', 'en-US').get_data(as_text=True)).is_equal_to(SPANISH)

    def test_use_the_language_the_browser_asks_for_in_single_mode_when_the_site_has_it(self, tmp_path):
        app = build_site(tmp_path, 'single', ['es'], 'es')
        html = get(app, '/', 'es-EC,es;q=0.9,en;q=0.8').get_data(as_text=True)
        assert_that(html).contains(f'<p id="string">{SPANISH}</p>')

    def test_keep_matching_the_browser_first_in_single_mode(self, tmp_path):
        app = build_site(tmp_path, 'single', ['es', 'en'], 'es')
        html = get(app, '/', 'en-US,en;q=0.9').get_data(as_text=True)
        assert_that(html).contains('<p id="page">es</p>')
        assert_that(html).contains(f'<p id="string">{SOURCE}</p>')

    def test_render_the_source_strings_in_single_mode_when_the_site_has_no_translations(self, tmp_path):
        app = build_site(tmp_path, 'single', ['es'], 'es', translated=False)
        html = get(app, '/', 'en-US').get_data(as_text=True)
        assert_that(html).contains(f'<p id="string">{SOURCE}</p>')

    @pytest.mark.parametrize('accept_language', ['en-US,en;q=0.9', 'es-EC,es;q=0.9', None])
    def test_follow_the_language_of_the_address_in_multi_mode(self, tmp_path, accept_language):
        app = build_site(tmp_path, 'multi', ['es', 'en'], 'es')
        spanish = get(app, '/es/', accept_language).get_data(as_text=True)
        english = get(app, '/en/', accept_language).get_data(as_text=True)
        assert_that(spanish).contains('<p id="page">es</p>').contains(f'<p id="string">{SPANISH}</p>')
        assert_that(english).contains('<p id="page">en</p>').contains(f'<p id="string">{SOURCE}</p>')

    def test_leave_a_route_outside_the_presenter_to_the_browser_in_multi_mode(self, tmp_path):
        app = build_site(tmp_path, 'multi', ['es'], 'es')
        assert_that(get(app, '/api/string', 'es-EC').get_data(as_text=True)).is_equal_to(SPANISH)
        assert_that(get(app, '/api/string', 'en-US').get_data(as_text=True)).is_equal_to(SOURCE)
        assert_that(get(app, '/api/string').get_data(as_text=True)).is_equal_to(SOURCE)
