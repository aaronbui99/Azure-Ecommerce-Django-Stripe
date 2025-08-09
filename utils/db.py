"""Database router for read/write splitting"""

class ReadWriteRouter:
    """
    A router to control all database operations on models for different
    databases with read/write splitting.
    """

    def db_for_read(self, model, **hints):
        """Reading from the replica database."""
        return 'replica'

    def db_for_write(self, model, **hints):
        """Writing to the default (primary) database."""
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Relations between objects are allowed."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that migrations only happen on the default (primary) database."""
        return db == 'default'