# OpenLLM: Chat with Various LLM Models

OpenLLM is a versatile project that allows users to interact with different language models (LLMs). It leverages the [Perplexity API](https://blog.perplexity.ai/blog/introducing-pplx-api) for access to well-known open-source models like the LLAMA models or Mistral 7B. Additionally, OpenAI's API is used to communicate with GPT models. There is also simple functinality for file embeddings.

## Features

- **Intuitive Chat Interface**: Users can seamlessly chat with various LLMs.
- **Chat History**: Basic chat history is stored locally in JSON files.
- **Token Counter**: Keep track of tokens used during interactions.
- **Simple embeddings with llama-index**: Chat to your files.
- **Simple authentification**: Set a password as an env variable and only users that enter the password correctly can access the site. Authentification is stored in a user-coockie, so you dont have to enter the password one.




## Demo


https://github.com/alikalik9/openllm/assets/126254607/d7d48784-094f-4a31-9350-49e0440f9e31



## Future Enhancements

- **Robust Error Handling**: Improve error handling for a smoother experience.
- **Optimizations**: Minor improvements and optimizations.

## Technical Details

OpenLLM relies on two Python libraries:
- [nicegui](https://nicegui.io/): Used for the user interface.
- [Langchain](https://www.langchain.com/): Facilitates communication with LLMs.
- [LlamaIndex](https://www.llamaindex.ai/): Facilitates Embeddings with LLMs.


## Installation

1. Clone the repository.
2. Install dependencies from `requirements.txt`.
3. Set the env variables listed in the env_vars_github.txt.
4. Run `main.py`.
