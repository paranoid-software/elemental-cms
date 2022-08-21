import re
import pycountry
from flask import render_template, Blueprint, request, g, current_app, redirect, abort, session, \
    render_template_string, url_for

from elementalcms.services import UseCaseResult
from elementalcms.services.pages import GetHome, GetMe
from elementalcms.services.snippets import GetMany


presenter = Blueprint('presenter', __name__, template_folder='templates')


@presenter.before_request
def before_request():
    lang_code = g.get('lang_code', None)
    if lang_code is None and current_app.config['LANGUAGE_MODE'] == 'single':
        return
    if lang_code is None:
        abort(404)
    if lang_code in current_app.config['LANGUAGES']:
        return
    return redirect(request.full_path.replace(lang_code,
                                              session.get('langCode', current_app.config["DEFAULT_LANGUAGE"])))


@presenter.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session.get('langCode', current_app.config["DEFAULT_LANGUAGE"]))


@presenter.url_value_preprocessor
def pull_lang_code(endpoint, values):

    lang_code = values.get('lang_code', None)
    if lang_code is None:
        return

    country = pycountry.languages.get(alpha_2=lang_code)
    if country is None:
        return

    g.lang_code = lang_code


@presenter.route('/', methods=['GET'])
def index(lang_code: str = None):

    draft = request.args.get('draft')
    lang_mode = current_app.config['LANGUAGE_MODE']

    if lang_code is None and lang_mode == 'single':
        lang_code = session.get('langCode', current_app.config['DEFAULT_LANGUAGE'])

    result: UseCaseResult = GetHome(current_app.config['CMS_DB_CONTEXT']).execute(lang_code,
                                                                                  draft=(draft == '1'))
    if result.is_failure():
        abort(404)

    if 'langCode' not in session or session['langCode'] != lang_mode:
        session['langCode'] = lang_code

    return render_template('presenter/index.html',
                           page=get_page_model(result.value()))


@presenter.route('/<slug>/', methods=['GET'])
def render(slug: str, lang_code: str = None):

    draft = request.args.get('draft')
    lang_mode = current_app.config['LANGUAGE_MODE']

    if lang_code is None and lang_mode == 'single':
        lang_code = session.get('langCode', current_app.config['DEFAULT_LANGUAGE'])

    result: UseCaseResult = GetMe(current_app.config['CMS_DB_CONTEXT']).execute(slug,
                                                                                lang_code,
                                                                                draft=(draft == '1'))
    if result.is_failure():
        abort(404)

    if 'langCode' not in session or session['langCode'] != lang_mode:
        session['langCode'] = lang_code

    return render_template('presenter/index.html',
                           page=get_page_model(result.value()))


def get_page_model(page_spec):

    styles = get_styles(page_spec['cssDeps'])

    scripts = get_scripts(page_spec['jsDeps'])
    content = render_template_string(page_spec['content'], page=page_spec)

    snippets_names = re.findall("<!--(.*)-->", content)
    get_many_snippets_result = GetMany(current_app.config['CMS_DB_CONTEXT']).execute(snippets_names)
    snippets = [] if get_many_snippets_result.is_failure() else get_many_snippets_result.value()

    snippets_styles = []
    snippets_scripts = []
    for snippet in snippets:
        snippets_styles += snippet['cssDeps']
        snippets_scripts += snippet['jsDeps']

    styles += get_styles(snippets_styles)
    scripts += get_scripts(snippets_scripts)

    return {
        'title': page_spec['title'],
        'name': page_spec['name'],
        'description': page_spec['description'],
        'content': content,
        'base_template': page_spec.get('baseTemplate', 'base.html'),
        'styles': '\n'.join(list(dict.fromkeys(styles).keys())),
        'scripts': '\n'.join(list(dict.fromkeys(scripts).keys()))
    }


def get_styles(deps):
    styles = []
    for dep in deps:

        props = []
        for key in dep.get('meta', {}).keys():
            props.append(f'{key}=\"{dep["meta"][key]}\"')

        if 'http' in dep['url']:
            styles.append(f'<link rel="stylesheet" type="text/css" href="{dep["url"]}" {" ".join(props)}>')
            continue
        href = f'{current_app.config["STATIC_URL"]}/{current_app.config["APP_NAME"]}/{dep["url"]}'
        styles.append(f'<link rel="stylesheet" type="text/css" href="{href}" {" ".join(props)}>')
    return styles


def get_scripts(deps):
    scripts = []
    for dep in deps:

        props = []
        for key in dep.get('meta', {}).keys():
            props.append(f'{key}=\"{dep["meta"][key]}\"')

        if dep['url'].startswith('http'):
            scripts.append(f'<script src="{dep["url"]}" type="{dep["type"]}" {" ".join(props)}></script>')
            continue
        src = f'{current_app.config["STATIC_URL"]}/{current_app.config["APP_NAME"]}/{dep["url"]}'
        scripts.append(f'<script src="{src}" type="{dep["type"]}" {" ".join(props)}></script>')
    return scripts
