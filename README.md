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

#### Syncing Collections
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

Setup choices are saved and omitted from future syncs
```bash
❯ vecsync -s zotero       

Syncing 15 files from local to OpenAI

🏁 Sync results:
Saved: 0 | Deleted: 0 | Skipped: 15 
Remote count: 15
Duration: 0.36 seconds
```

#### Settings

Settings are persisted in a local json file. These can be purged at any point.
```bash
vecsync settings delete
```

#### Chat Interactions
Uploaded documents can be interacted with via command line. The responding assistant is automatically linked to your
vector store.

```bash
vecsync assistant chat
✅ Assistant found: asst_123456789
Type "exit" to quit at any time.

> Give a one sentence summary of your vector store collection contents.
💬 Conversation started: thread_123456789

The contents of the vector store collection primarily focus on machine learning techniques for causal effect inference,particularly through adversarial representation learning methods that address challenges in treatment selection bias and information loss in observational data
```

Subsequent interactions resume the current conversation.
```bash
vecsync assistant chat   
✅ Assistant found: asst_123456789
✅ Thread found: thread_123456789
Type "exit" to quit at any time.

> What was my last question to you? 
Your last question to me was asking for a one sentence summary of the contents of my vector store collection.
```

Threads can be cleared using the `-n` flag. Here the assistant defaulted to the system prompt as a question since no
thread history was available.
```bash
vecsync assistant chat -n
✅ Assistant found: asst_123456789
Type "exit" to quit at any time.

> What was my last question to you?
💬 Conversation started: thread_987654321

Your last question was about searching for relevant information from a large number of journals and papers, emphasizing the importance of citing information from the provided sources without making up any content.
```

