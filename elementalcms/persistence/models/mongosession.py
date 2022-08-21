from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict


class MongoSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, refresh=False):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.modified = False
        self.refresh = refresh
