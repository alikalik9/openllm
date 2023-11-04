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
    """
    This class is used to create and load embeddings, and to query them using langchain.
    """
    def __init__(self):
        """
        Initializes the Embedding class with the necessary directories and services.
        """
        os.environ[
            "OPENAI_API_KEY"
        ] = "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"
        current_directory = os.getcwd()
        self.embedding_file_dir = os.path.join(current_directory, 'embedding_files')   
        self.vector_dir = os.path.join(current_directory, "index_files")
        self.llm_predictor = LLMPredictor(
            llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", request_timeout=120)
        )
        self.service_context = ServiceContext.from_defaults(
            llm_predictor=self.llm_predictor
        )
    async def create_index(self):
        """
        Asynchronously creates an index from the documents in the embedding file directory.
        """
        self.documents = SimpleDirectoryReader(self.embedding_file_dir, recursive=True).load_data()
        self.index = GPTVectorStoreIndex.from_documents(
            self.documents, service_context=self.service_context
        )
        self.index.storage_context.persist(persist_dir=self.vector_dir)
       
    def load_index(self):
        
        """
        Loads an index from the vector directory.
        Returns:
            The loaded index.
        """
        storagecontext = StorageContext.from_defaults(persist_dir=self.vector_dir)
        self.index = load_index_from_storage(storagecontext)
        return self.index
    async def querylangchain(self, prompt):
        """
        Uses the embedding from llamaindex with langchain.
        Creates a langchain agent that uses the embedding. Asynchronously queries the langchain with a given prompt.
        
        Parameters:
            prompt (str): The prompt to query the langchain with.
        Returns:
            The response from the langchain.
        """
        llm = ChatOpenAI(temperature=0)
        index = self.load_index()
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