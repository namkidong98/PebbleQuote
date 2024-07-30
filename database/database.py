import os
from dotenv import load_dotenv
from database.chroma_manager import ChromaManager

# .env 파일을 현재 작업 디렉토리에서 로드
load_dotenv() 

# Chroma DB
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = os.environ.get("CHROMA_PORT")

class ChromaManagerSingleton(ChromaManager):
    _manager = None

    @classmethod
    def get_client(cls):
        if cls._manager is None:
            cls._manager = cls._connect()
        return cls._manager

    @classmethod
    def _connect(cls):
        try:
            manager = ChromaManager(host=CHROMA_HOST, port=CHROMA_PORT)
            if manager.connected: # True일때 연결
                print("ChromaDB Connection Succeed")
            else:
                print("Failed to connect to ChromaDB")
            return manager
        except Exception:
            print("Failed to connect to ChromaDB")
            return None

    @classmethod
    def reconnect(cls):
        cls._manager = cls._connect()

def vector_connect(): 
    manager = ChromaManagerSingleton.get_client()
    # 연결 상태 확인 및 재연결
    if manager.connected:
        print("ChromaDB is active!\n")
    # ChromaDB 연결을 안한 상태로 할 때 지나치게 느려지는 것을 방지하기 위해 재연결은 일단 주석처리
    # else:
    #     print("Try to reconnect ChromaDB\n")
    #     ChromaManagerSingleton.reconnect()
    #     manager = ChromaManagerSingleton.get_client()
    return manager