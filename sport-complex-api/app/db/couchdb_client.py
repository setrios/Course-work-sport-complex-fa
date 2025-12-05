import couchdb
from typing import Optional

# Hardcoded for now since Config is skipped
COUCHDB_HOST = "localhost"
COUCHDB_PORT = 5984
COUCHDB_USER = "admin"
COUCHDB_PASSWORD = "password"

class CouchDBClient:
    _server: Optional[couchdb.Server] = None
    
    @classmethod
    def get_server(cls) -> couchdb.Server:
        """
        Returns a CouchDB server instance (singleton pattern).
        """
        if cls._server is None:
            url = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@{COUCHDB_HOST}:{COUCHDB_PORT}/"
            cls._server = couchdb.Server(url)
        return cls._server
    
    @classmethod
    def get_db(cls, db_name: str):
        """
        Returns a specific CouchDB database.
        Creates it if it doesn't exist.
        """
        server = cls.get_server()
        if db_name not in server:
            return server.create(db_name)
        return server[db_name]

def get_couchdb_server() -> couchdb.Server:
    """
    Dependency that provides a CouchDB server instance.
    """
    return CouchDBClient.get_server()
