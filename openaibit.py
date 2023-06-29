import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
print(OPENAI_API_KEY)
import nest_asyncio
nest_asyncio.apply()

import sys


from llama_index import SimpleDirectoryReader, ServiceContext, LLMPredictor
from llama_index import GPTVectorStoreIndex, GPTListIndex, GPTSimpleKeywordTableIndex
from llama_index.composability import ComposableGraph
from langchain.chat_models import ChatOpenAI

def warming_llm_engine():
    documents = SimpleDirectoryReader(input_dir='text_data').load_data()
    index = GPTVectorStoreIndex.from_documents(documents)

    # Parse into Nodes
    from llama_index.node_parser import SimpleNodeParser
    nodes = SimpleNodeParser().get_nodes_from_documents(documents=documents)

    # Add to Docstore
    from llama_index.storage.docstore import SimpleDocumentStore
    docstore = SimpleDocumentStore()
    docstore.add_documents(nodes)

    # Define Indexes
    from llama_index.storage.storage_context import StorageContext

    storage_context = StorageContext.from_defaults(docstore=docstore)
    list_index = GPTListIndex(nodes, storage_context=storage_context)

    # Setting LLM predictor and service
    llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
    service_context_chatgpt = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt, chunk_size_limit=1024)

    query_engine = list_index.as_query_engine()
    # print(query_engine.query("The data is a reference sheet for commands. What command does the statement 'you should smite 7 times' most resemble? Do not include anything after the colon in response. If any amount or number is specified, replace the section of the command in brackets with that number."))
    print("Successfully created CMD parsing section")
    return query_engine
