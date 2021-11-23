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
        if sid:
            get_me_result = GetMe(self.db_context).execute(sid)
            if not get_me_result.is_failure():
                stored_session = get_me_result.value()
                if stored_session.get('expiration') > datetime.utcnow():
                    return MongoSession(initial=stored_session['data'],
                                        sid=stored_session['sid'])
        sid = str(uuid4())
        return MongoSession(sid=sid)

    def save_session(self, app, session: MongoSession, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        if self.get_expiration_time(app, session):
            expiration = self.get_expiration_time(app, session)
        else:
            expiration = datetime.utcnow() + timedelta(hours=1)
        UpsertMe(self.db_context).execute({
                                              'sid': session.sid,
                                              'data': session,
                                              'expiration': expiration
                                          })
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain)
