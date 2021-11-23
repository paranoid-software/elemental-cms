import pycountry
from flask import render_template, Blueprint, request, g, current_app, redirect, url_for, abort, session, \
    render_template_string

from elementalcms.services import UseCaseResult
from elementalcms.services.pages import GetHome, GetMe


presenter = Blueprint('presenter', __name__, template_folder='templates')


@presenter.before_request
def before_request():
    if g.lang_code in current_app.config['LANGUAGES']:
        return
    adapter = current_app.url_map.bind('')
    try:
        country = pycountry.countries.get(alpha_2=request.full_path.lstrip('/').rstrip('/ ?'))
        if country is None:
            endpoint, args = adapter.match(f'/{current_app.config["DEFAULT_LANGUAGE"]}{request.full_path.rstrip("?")}')
            return redirect(url_for(endpoint, **args), 301)
        return redirect(f'/{current_app.config["DEFAULT_LANGUAGE"]}')
    except Exception as e:
        print(e)
        abort(404)


@presenter.url_defaults
def add_language_code(endpoint, values):
    if current_app.config['LANGUAGE_MODE'] == 'single':
        values.setdefault(current_app.config["DEFAULT_LANGUAGE"])
        return
    values.setdefault('lang_code', g.lang_code)


@presenter.url_value_preprocessor
def pull_lang_code(endpoint, values):
    session['lang_code'] = values.pop('lang_code', current_app.config["DEFAULT_LANGUAGE"])
    g.lang_code = session.get('lang_code', current_app.config["DEFAULT_LANGUAGE"])


@presenter.route('/')
def index():
    draft = request.args.get('draft')
    result: UseCaseResult = GetHome(current_app.config['CMS_DB_CONTEXT']).execute(g.lang_code,
                                                                                  draft=(draft == '1'))
    if result.is_failure():
        abort(404)
    return render_template('presenter/index.html',
                           page=get_page_model(result.value()))


@presenter.route('/<slug>/')
def render(slug: str):
    draft = request.args.get('draft')
    result: UseCaseResult = GetMe(current_app.config['CMS_DB_CONTEXT']).execute(slug,
                                                                                g.lang_code,
                                                                                draft=(draft == '1'))
    if result.is_failure():
        abort(404)
    return render_template('presenter/index.html',
                           page=get_page_model(result.value()))


def get_page_model(page_spec):
    styles = get_styles(page_spec['cssDeps'])
    scripts = get_scripts(page_spec['jsDeps'])
    content = render_template_string(page_spec['content'], page=page_spec)
    return {
        'title': page_spec['title'],
        'name': page_spec['name'],
        'description': page_spec['description'],
        'content': content,
        'styles': ''.join(styles),
        'scripts': ''.join(scripts)
    }


def get_styles(deps):
    styles = []
    for dep in deps:
        if 'http' in dep['url']:
            styles.append(f'<link rel="stylesheet" type="text/css" href="{dep["url"]}">')
            continue
        href = f'{current_app.config["STATIC_URL"]}/{current_app.config["APP_NAME"]}/{dep["url"]}'
        styles.append(f'<link rel="stylesheet" type="text/css" href="{href}">')
    return styles


def get_scripts(deps):
    scripts = []
    for dep in deps:
        if dep['url'].startswith('http'):
            scripts.append(f'<script src="{dep["url"]}" type="{dep["type"]}"></script>')
            continue
        src = f'{current_app.config["STATIC_URL"]}/{current_app.config["APP_NAME"]}/{dep["url"]}'
        scripts.append(f'<script src="{src}" type="{dep["type"]}"></script>')
    return scripts
