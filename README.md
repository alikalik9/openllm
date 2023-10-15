## OpenLLM

OpenLLM is a project that enables chatting with various LLM models. It uses the [Perplexity API](https://blog.perplexity.ai/blog/introducing-pplx-api), which provides access to some of the most well-known open-source models, such as the LLAMA models or Mistral 7B. Additionally, the OpenAI API is used to communicate with the well-known GPT models from OpenAI.

### Demo


https://github.com/alikalik9/openllm/assets/126254607/72760663-b583-4a84-ba11-a49741b3008f





### Features

- Intuitive chat interface
- Integration of various LLMs
- Seamless transition between LLMs! Write in a chat with different models
- Basic chat history, which is stored locally in JSON files
- Token counter

### ToDos and future features

- Robust error handling
- Embeddings
- Minor improvements and optimizations

### Technical basis

The project is mainly based on two Python libraries. The awesome [nicegui](https://nicegui.io/) package was used for the UI. [Langchain](https://www.langchain.com/) was used for communication with the LLMs.

### Installation

1. Clone the repo
2. Install requirements.txt
3. Store API keys for OpenAI and Perplexity
4. Run main.py
