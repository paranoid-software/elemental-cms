import pycountry
from flask import render_template, Blueprint, request, g, current_app, redirect, abort, session, \
    render_template_string, url_for

from elementalcms.services import UseCaseResult
from elementalcms.services.pages import GetHome, GetMe


presenter = Blueprint('presenter', __name__, template_folder='templates')


@presenter.before_request
def before_request():
    lang_code = g.get('lang_code', None)
    if lang_code is None:
        abort(404)
    if lang_code in current_app.config['LANGUAGES']:
        return
    return redirect(request.full_path.replace(lang_code,
                                              session.get('langCode', current_app.config["DEFAULT_LANGUAGE"])), 301)


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
def index(lang_code: str):
    draft = request.args.get('draft')
    result: UseCaseResult = GetHome(current_app.config['CMS_DB_CONTEXT']).execute(lang_code,
                                                                                  draft=(draft == '1'))
    if result.is_failure():
        abort(404)

    requires_user_identity = result.value().get('requiresUserIdentity', False)
    redirect_users_to = result.value().get('redirectUsersTo', '').strip() or None
    has_user_identity = session.get('userIdentity', None)

    if redirect_users_to and has_user_identity:
        url = url_for('presenter.render', **{'lang_code': lang_code, 'slug': redirect_users_to})
        if draft == '1':
            url = url_for('presenter.render', **{'lang_code': lang_code, 'slug': redirect_users_to}, draft=1)
        return redirect(url)

    if requires_user_identity and not has_user_identity:
        abort(401)

    session['langCode'] = lang_code
    return render_template('presenter/index.html',
                           page=get_page_model(result.value()))


@presenter.route('/<slug>/', methods=['GET'])
def render(lang_code: str, slug: str):
    draft = request.args.get('draft')
    result: UseCaseResult = GetMe(current_app.config['CMS_DB_CONTEXT']).execute(slug,
                                                                                lang_code,
                                                                                draft=(draft == '1'))
    if result.is_failure():
        abort(404)

    requires_user_identity = result.value().get('requiresUserIdentity', False)
    redirect_users_to = result.value().get('redirectUsersTo', '').strip() or None
    has_user_identity = session.get('userIdentity', None)

    if redirect_users_to and has_user_identity:
        url = url_for('presenter.render', **{'lang_code': lang_code, 'slug': redirect_users_to})
        if draft == '1':
            url = url_for('presenter.render', **{'lang_code': lang_code, 'slug': redirect_users_to}, draft=1)
        return redirect(url)

    if requires_user_identity and not has_user_identity:
        abort(401)

    session['langCode'] = lang_code
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
