# vecsync
[![PyPI](https://img.shields.io/pypi/v/vecsync)](https://pypi.org/project/vecsync)

A simple command-line utility for synchronizing documents to vector storage for LLM interaction. Vecsync helps you
quickly chat with papers, journals, and other documents with minimal overhead.

- 📄 Upload a local collection of PDFs to a remote vector store
- ✅ Automatically add and remove remote files to match local documents
- ☺️ Simplify platform specific complexities
- 👀 Synchronize with a Zotero collection
- 💬 Chat with documents from command line

Currently vecsync only supports OpenAI vector stores and chat assistants in early development.

## Getting Started

### Installation
Install vecsync from PyPI.
```
pip install vecsync
```

Set your OpenAI API key environment.
```
export OPENAI_API_KEY=...
```
You can also define the key via `.env` file using [dotenv](https://pypi.org/project/python-dotenv/)
```
echo "OPENAI_API_KEY=…" > .env
```

### Usage
Sync from local file path
```bash
cd path/to/pdfs

vecsync

Syncing 2 files from local to OpenAI
Uploading 2 files to OpenAI file storage
Attaching 2 files to OpenAI vector store

🏁 Sync results:
Saved: 2 | Deleted: 0 | Skipped: 0 
Remote count: 2
Duration: 8.93 seconds
 ```

 Sync from a Zotero collection
 ```
vecsync -s zotero

Enter the path to your Zotero directory (Default: /Users/jbencina/Zotero): 

Available collections:
[1]: My research
Enter the collection ID to sync (Default: 1): 

Syncing 15 files from local to OpenAI
Uploading 15 files to OpenAI file storage
Attaching 15 files to OpenAI vector store

🏁 Sync results:
Saved: 15 | Deleted: 0 | Skipped: 0 
Remote count: 15
Duration: 57.99 seconds
```

Interactive setup options are saved and omitted from future syncs
```bash
❯ vecsync -s zotero       

Syncing 15 files from local to OpenAI

🏁 Sync results:
Saved: 0 | Deleted: 0 | Skipped: 15 
Remote count: 15
Duration: 0.36 seconds
```

Settings can be purged for reconfiguration
```bash
vecsync settings delete
```

Uploaded documents can be interacted with via command line. The responding assistant is automatically linked to your
vector store.


```bash
vecsync assistant chat

✅ Assistant found: asst_12345

Enter your prompt (or 'exit' to quit): Give me a one sentence description of DragonNet

DragonNet is a neural network model designed for estimating treatment effects from observational data, utilizing an 
end-to-end architecture that focuses on the efficiency of the propensity score and incorporates targeted 
regularization techniques to enhance estimation accuracy

Enter your prompt (or 'exit' to quit): what was my last question to you in this chat?

Your last question was to explain "dragonnet" in one sentence.
```

