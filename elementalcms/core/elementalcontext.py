from elementalcms.core import FlaskContext, MongoDbContext


class ElementalContext(object):

    def __init__(self,
                 cms_core_context: FlaskContext,
                 cms_db_context: MongoDbContext):

        self.cms_core_context: FlaskContext = cms_core_context
        self.cms_db_context: MongoDbContext = cms_db_context
