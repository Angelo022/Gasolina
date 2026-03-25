import os

class Config:
    DB_SERVER = os.getenv('DB_SERVER', '')
    DB_NAME = os.getenv('DB_NAME', 'gasola_test')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = os.getenv('DB_PORT', '')

    @classmethod
    def get_connection_params(cls):
        return {
            "host": cls.DB_SERVER,
            "database": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "port": cls.DB_PORT
        }
