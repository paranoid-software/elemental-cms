import json

import pycountry
from bson import json_util
from flask import render_template, Blueprint, g, abort, current_app, request, redirect, url_for, session

from elementalcms.services import UseCaseResult
from elementalcms.services.pages import GetMe

admin = Blueprint('admin', __name__, template_folder='templates')


@admin.before_request
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


@admin.url_defaults
def add_language_code(endpoint, values):
    if current_app.config['LANGUAGE_MODE'] == 'single':
        values.setdefault(current_app.config["DEFAULT_LANGUAGE"])
        return
    values.setdefault('lang_code', g.lang_code)


@admin.url_value_preprocessor
def pull_lang_code(endpoint, values):
    session['lang_code'] = values.pop('lang_code', current_app.config["DEFAULT_LANGUAGE"])
    g.lang_code = session.get('lang_code', current_app.config["DEFAULT_LANGUAGE"])


@admin.route('/<slug>/edit/')
def index(slug):
    result: UseCaseResult = GetMe(current_app.config['CMS_DB_CONTEXT']).execute(slug, g.lang_code, True)
    if result.is_failure():
        abort(404)
    return render_template('admin/index.html',
                           page=json.loads(json_util.dumps(result.value())))
