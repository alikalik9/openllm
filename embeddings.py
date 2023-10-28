import os
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
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool
import asyncio
from langchain.agents import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from llama_index.langchain_helpers.memory_wrapper import GPTIndexChatMemory





class Embedding:
    def __init__(self):
        os.environ[
            "OPENAI_API_KEY"
        ] = "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"
        self.llm_predictor = LLMPredictor(
            llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", request_timeout=120)
        )
        self.service_context = ServiceContext.from_defaults(
            llm_predictor=self.llm_predictor
        )
    def create_index(self, doc_path, index_path):
        self.documents = SimpleDirectoryReader(doc_path, recursive=True).load_data()
        self.index = GPTVectorStoreIndex.from_documents(
            self.documents, service_context=self.service_context
        )
        self.index.storage_context.persist(persist_dir=index_path)
       
    def load_index(self, indexpath):
        storagecontext = StorageContext.from_defaults(persist_dir=indexpath)
        self.index = load_index_from_storage(storagecontext)
        return self.index
    async def querylangchain(self, prompt):
        current_directory = os.getcwd()
        vector_dir = os.path.join(current_directory, "index_files")
        llm = ChatOpenAI(temperature=0)
        index = self.load_index(vector_dir)
        memory = ConversationBufferMemory(memory_key="chat_history")

        self.tools = [
                Tool(
                    name="LlamaIndex",
                    func=lambda q: str(index.as_query_engine().query(q)),
                    description="useful for when you want to answer questions about the author. The input to this tool should be a complete english sentence.",
                    return_direct=True,
                ),
            ]      
        agent_executor = initialize_agent(
        self.tools, llm, agent="conversational-react-description", memory=memory)
        response = await agent_executor.arun(prompt)
        return response


    
emb = Embedding()
current_directory = os.getcwd()
embedding_dir = os.path.join(current_directory, 'embedding_files')   
vector_dir = os.path.join(current_directory, "index_files")

#index = emb.load_index(vector_dir)
#response = emb.querylangchain(vector_dir=vector_dir,prompt="wer ist alek")
#print(response)