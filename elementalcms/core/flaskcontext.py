class FlaskContext(object):

    def __init__(self, settings: dict):
        self.DEBUG = settings.get('DEBUG', True)
        self.ENV = settings.get('ENV', 'development')
        self.SECRET_KEY = settings.get('SECRET_KEY', '2+2==10')
        self.SITE_NAME = settings.get('SITE_NAME', 'My Elemental CMS')
        self.GOOGLE_SITE_VERIFICATION_TOKEN = settings.get('GOOGLE_SITE_VERIFICATION_TOKEN', None)
        self.COMPANY = settings.get('COMPANY', 'Paranoid Software')
        self.CANONICAL_URL = settings.get('CANONICAL_URL', 'https://elemental.cms')
        self.LANGUAGES = settings.get('LANGUAGES', ['en', 'es'])
        self.DEFAULT_LANGUAGE = settings.get('DEFAULT_LANGUAGE', 'es')
        self.LANGUAGE_MODE = settings.get('LANGUAGE_MODE', 'multi')
        self.STATIC_FOLDER = settings.get('STATIC_FOLDER', 'static').strip() or 'static'
        self.MEDIA_FOLDER = settings.get('MEDIA_FOLDER', 'media').strip() or 'media'
        self.STATIC_BUCKET = settings.get('STATIC_BUCKET', '').strip() or None
        self.MEDIA_BUCKET = settings.get('MEDIA_BUCKET', '').strip() or None
        self.STATIC_URL = settings.get('STATIC_URL', '/static') or '/static'
        self.MEDIA_URL = settings.get('MEDIA_URL', '/media') or '/media'
        self.GLOBAL_DEPS_FOLDER = settings.get('GLOBAL_DEPS_FOLDER', 'workspace/global_deps')
        self.PAGES_FOLDER = settings.get('PAGES_FOLDER', 'workspace/pages')
        self.SNIPPETS_FOLDER = settings.get('SNIPPETS_FOLDER', 'workspace/snippets')
        self.GOOGLE_SERVICE_ACCOUNT_INFO = settings.get('GOOGLE_SERVICE_ACCOUNT_INFO', {})
        self.USER_IDENTITY_SESSION_KEY = settings.get('USER_IDENTITY_SESSION_KEY', 'userIdentity')
        self.SESSION_STORAGE_ENABLED = settings.get('SESSION_STORAGE_ENABLED', True)
        self.SESSION_TIMEOUT_IN_MINUTES = settings.get('SESSION_TIMEOUT_IN_MINUTES', 60)
        self.DESIGN_MODE_ENABLED = settings.get('DESIGN_MODE_ENABLED', False)
