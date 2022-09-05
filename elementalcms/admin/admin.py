import json

import pycountry
from bson import json_util
from flask import render_template, Blueprint, g, abort, current_app, request, redirect, session

from elementalcms.services import UseCaseResult
from elementalcms.services.pages import GetMeForLanguage

admin = Blueprint('admin', __name__, template_folder='templates')


@admin.before_request
def before_request():
    lang_code = g.get('lang_code', None)
    if lang_code is None and current_app.config['LANGUAGE_MODE'] == 'single':
        return
    if lang_code is None:
        abort(404)
    if lang_code in current_app.config['LANGUAGES']:
        return
    return redirect(request.full_path.replace(lang_code,
                                              session.get('lang_code', current_app.config["DEFAULT_LANGUAGE"])))


@admin.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session.get('langCode', current_app.config["DEFAULT_LANGUAGE"]))


@admin.url_value_preprocessor
def pull_lang_code(endpoint, values):

    lang_code = values.get('lang_code', None)
    if lang_code is None:
        return

    country = pycountry.languages.get(alpha_2=lang_code)
    if country is None:
        return

    g.lang_code = lang_code


@admin.route('/<slug>/edit/', methods=['GET'])
def index(slug: str, lang_code: str = None):
    admin_identity = session.get('adminIdentity', None)
    if not admin_identity:
        abort(401)

    if lang_code is None and current_app.config['LANGUAGE_MODE'] == 'single':
        lang_code = session.get('langCode', current_app.config['DEFAULT_LANGUAGE'])

    result: UseCaseResult = GetMeForLanguage(current_app.config['CMS_DB_CONTEXT']).execute(slug,
                                                                                           lang_code,
                                                                                           True)
    if result.is_failure():
        abort(404)

    session['langCode'] = lang_code
    return render_template('admin/index.html',
                           page=json.loads(json_util.dumps(result.value())))
