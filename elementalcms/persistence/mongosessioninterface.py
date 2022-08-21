from datetime import datetime, timedelta
from uuid import uuid4

from flask.sessions import SessionInterface

from elementalcms.persistence.models import MongoSession
from elementalcms.services.sessions import GetMe, UpsertMe
from elementalcms.core import MongoDbContext


class MongoSessionInterface(SessionInterface):

    def __init__(self, db_context: MongoDbContext):
        self.db_context = db_context

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid is None:
            print(f'puta: {request.path}')
            # New cookie, new session
            sid = str(uuid4())
            return MongoSession(sid=sid)
        return MongoSession(sid=sid)

    def save_session(self, app, session: MongoSession, response):
        domain = self.get_cookie_domain(app)
        if not session:
            # I do not understand this line ...
            # response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        expiration = datetime.utcnow() + timedelta(minutes=app.config.get('SESSION_TIMEOUT_IN_MINUTES', 60))
        UpsertMe(self.db_context).execute({
                                              'sid': session.sid,
                                              'data': session,
                                              'expiration': expiration
                                          })
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=expiration,
                            httponly=True, domain=domain)
