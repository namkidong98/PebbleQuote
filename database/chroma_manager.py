import os
from dotenv import load_dotenv
import chromadb
from langchain_chroma import Chroma
from langchain.schema import Document
# from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_upstage import UpstageEmbeddings

load_dotenv()

QUOTE_COLLECTION = 'Quote'
UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class ChromaManager():
    def __init__(self, host: str, port: str) -> None:
        self.connected = False
        self.embedding_function_doc = UpstageEmbeddings(
            model="solar-embedding-1-large-passage", upstage_api_key=UPSTAGE_API_KEY)
        self.embedding_function_query = UpstageEmbeddings(
            model="solar-embedding-1-large-query", upstage_api_key=UPSTAGE_API_KEY)
        self.__connect_db__(host, port)

    def __connect_db__(self, host, port):
        try:
            self.client = chromadb.HttpClient(host=host, port=port)  # DB 접속 시도
            print(f'chromadb [version : {self.client.get_version()}] connected.')
            self.connected = True
        except Exception as e:
            print(e)
            return 

        # get collection
        self.quotes = self.__get_collection__(QUOTE_COLLECTION)
        self.quote_db = Chroma(
            client=self.client,
            collection_name=QUOTE_COLLECTION,
            embedding_function=self.embedding_function_doc # 문서에 대한 임베딩은 "solar-embedding-1-large-passage"를 사용
        )

    def __get_collection__(self, name: str):
        if any(collection.name == name for collection in self.client.list_collections()):
            print(f'{name} Collection Found\n')
            return self.client.get_collection(name)
        else:
            print(f"{name} Collection Not Found. Creating the Collection\n")
            try:
                collection = self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"},
                    embedding_function=self.embedding_function_doc, # 문서에 대한 임베딩은 "solar-embedding-1-large-passage"를 사용
                )
                print("Collection created:", collection)
                return collection
            except KeyError as e:
                print(f"KeyError: {e}")
                raise

    def add_quote(self, description: str, quote_id: str, quote: str, author: str):
        try:
            doc = Document(
                page_content=description,   # quote의 description 기반으로 검색하고
                metadata={
                    'quote_id': quote_id,   # quote의 고유 ID(PK)
                    'quote': quote,         # quote의 content 확인용
                    'author': author,       # quote의 원저작자 확인용
                }
            )
            # print("Document to be added:", doc)
            result = self.quote_db.add_documents([doc])
            return result
        except Exception as e:
            print(f"Error in add_quote : {e}")
            raise

    def delete_quote_by_quote_id(self, quote_id: str):
        self.quotes.delete(where={'quote_id': quote_id})

    def get_quote_by_quote_id(self, quote_id: str):
        return self.quotes.get(where={'quote_id': quote_id})

    def search_quote(self, query: str, quote_num : int):
        query_vector = self.embedding_function_query.embed_query(query) # List[Float]
        retrieved_quotes = self.quote_db.similarity_search_by_vector_with_relevance_scores(
            embedding = query_vector,
            k = quote_num
        )
        # retrieved_quote = self.quote_db.similarity_search( # query에 대한 임베딩은 'solar-embedding-1-large-query'를 사용
        #     query=query, k=1, embedding_function=self.embedding_function_query
        # )
        retrieved_quotes = sorted(retrieved_quotes, key=lambda x:x[1]) # score를 기준으로 오름차순 정렬(스코어가 낮은 명언들부터 앞으로 오게)
        return retrieved_quotes  # List[Tuple[Document, float]]