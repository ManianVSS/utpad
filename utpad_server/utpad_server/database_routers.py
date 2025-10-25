# noinspection PyMethodMayBeStatic,PyProtectedMember
class ReplicaRouter:
    def db_for_read(self, model, **hints):
        return 'default'

    # def db_for_write(self, model, **hints):
    #     return 'default'
    #
    # def allow_relation(self, obj1, obj2, **hints):
    #     """
    #     Relations between objects are allowed if both objects are
    #     in the same pool.
    #     """
    #     # db_list = ('default', 'replica')
    #     if obj1._state.db == obj2._state.db:
    #         return True
    #     return None
    #
    # def allow_migrate(self, db, app_label, model_name=None, **hints):
    #     return True
