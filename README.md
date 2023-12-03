# OpenLLM: Chat with various LLM Models

OpenLLM is a versatile project that allows users to interact with different language models (LLMs). It leverages the [Perplexity API](https://blog.perplexity.ai/blog/introducing-pplx-api) for access to well-known open-source models like the LLAMA models or Mistral 7B. Additionally, OpenAI's API is used to communicate with GPT models. There is also simple functinality for file embeddings.

## Features

- **Intuitive Chat Interface**: Users can seamlessly chat with various LLMs.
- **Chat History**: Basic chat history is stored locally in JSON files.
- **Token Counter**: Keep track of tokens used during interactions.
- **Online LLMs!**: Using the newest perplexity online-models that are grounded on internet data. So no cutoff-date! Very new models so definetly expect errors.
- **Basic embeddings with llama-index**: Upload your files and chat to them.
- **Basic authentification**: Set a password as an env variable and only users that enter that password correctly can access the site. Authentification is stored in a user-coockie, so you dont  to enter the password only once->Very basic, no password encoding implemented.




## Demo

https://github.com/alikalik9/openllm/assets/126254607/82e26710-0dc1-4e6c-8530-2b8f2028954a

Online-LLM


https://github.com/alikalik9/openllm/assets/126254607/2244c9b9-c6cc-4362-be81-a7bf1f23fa75





## Future Enhancements

- **Robust Error Handling**: Improve error handling for a smoother experience.
- **Optimizations**: Minor improvements and optimizations.

## Technical Details

OpenLLM relies on two Python libraries:
- [NiceGUI](https://nicegui.io/): Used for the user interface.
- [Langchain](https://www.langchain.com/): Facilitates communication with LLMs.
- [LlamaIndex](https://www.llamaindex.ai/): Facilitates Embeddings with LLMs.


## Installation

1. Clone the repository.
2. Install dependencies from `requirements.txt`.
3. Set the env variables listed in the env_vars_github.txt. Or create a file called "var.env" where you set the env variables found in the env_vars_github.txt. The code will automatically use the vars stored in the var.env
4. Run `main.py`.
