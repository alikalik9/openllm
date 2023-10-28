from llama_index import (
    GPTVectorStoreIndex,
    SimpleDirectoryReader,
    download_loader,
    LLMPredictor,
    ServiceContext,
    MockLLMPredictor,
    load_index_from_storage
    )
from llama_index.storage.storage_context import StorageContext
from chat import ChatApp

class Embedding(ChatApp):
    def __init__(self):
        super().__init__()  # Call the initializer of the parent class
        # Add any additional initialization code here
        self.llm_predictor = LLMPredictor(
            llm=self.llm
        )
        self.service_context = ServiceContext.from_defaults(
            llm_predictor=self.llm_predictor
        )

    # Add any additional methods here
    def create_index(self, index_path):
        self.documents = SimpleDirectoryReader("embedding_files", recursive=True).load_data()
        self.index = GPTVectorStoreIndex.from_documents(
            self.documents, service_context=self.service_context
        )
        self.index.storage_context.persist(persist_dir="index_path")
       
    async def load_index(self, indexpath):
        storagecontext = StorageContext.from_defaults(persist_dir="indexpath")
        self.index = load_index_from_storage(storagecontext)
        return self.index
    def chat(self, index,prompt):
        query_engine = index.as_query_engine()
        self.response = query_engine.query(prompt)
