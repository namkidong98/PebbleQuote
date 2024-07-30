from django.apps import AppConfig
from database.database import vector_connect

class ConfigAppConfig(AppConfig):
    name = 'config'

    def ready(self):
        print("Initializing....")
        # ChromaDB 매니저 초기화
        vector_connect()