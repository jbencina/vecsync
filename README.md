# vecsync
[![GitHub](https://img.shields.io/badge/GitHub-repo-green.svg)](https://github.com/jbencina/vecsync)
[![PyPI](https://img.shields.io/pypi/v/vecsync)](https://pypi.org/project/vecsync)
[![image](https://img.shields.io/pypi/l/vecsync.svg)](https://pypi.python.org/pypi/vecsync)
[![image](https://img.shields.io/pypi/pyversions/vecsync.svg)](https://pypi.python.org/pypi/vecsync)
[![Actions status](https://github.com/jbencina/vecsync/actions/workflows/ci.yaml/badge.svg)](https://github.com/jbencina/vecsync/actions)

A simple command-line utility for synchronizing documents to vector storage for LLM interaction. Vecsync helps you
quickly chat with papers, journals, and other documents with minimal overhead.

- 📄 Upload a local collection of PDFs to a remote vector store
- ✅ Automatically add and remove remote files to match local documents
- ☺️ Simplify platform specific complexities
- 👀 Synchronize with a Zotero collection
- 💬 Chat with documents from command line or local Gradio UI

![demo](docs/images/demo.gif)

Local [Gradio](https://www.gradio.app) instance available for assistant interaction. Chat history across sessions is saved.
![chat](docs/images/demo_chat.png)

## Getting Started
> **OpenAI API Requirements**
>
> Currently vecsync only supports OpenAI for remote operations and requires a valid OpenAI key with credits. Visit https://openai.com/api/ for more information. Future improvements will allow more platform options and self-hosted models.

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

### Development
This project is still in early alpha, and users should frequent updates. Breaking changes will be avoided where possible.
To use the latest code, clone the repository and install locally. In progress work uses the branch naming convention
of `dev-0.0.1` and will have an accompanying open PR.
```bash
git clone -b dev-0.0.1 git@github.com:jbencina/vecsync.git
cd vecsync
uv sync && source .venv/bin/activate
```

### Usage

#### Synching Collections
Use the `vs sync` command for all synching operations.

Sync from local file path.
```bash
cd path/to/pdfs && vs sync

Synching 2 files from local to OpenAI
Uploading 2 files to OpenAI file storage
Attaching 2 files to OpenAI vector store

🏁 Sync results:
Saved: 2 | Deleted: 0 | Skipped: 0 
Remote count: 2
Duration: 8.93 seconds
```

 Sync from a Zotero collection. Interactive selections are remembered for future sessions.
```bash
vs sync -s zotero

Enter the path to your Zotero directory (Default: /Users/jbencina/Zotero): 

Available collections:
[1]: My research
Enter the collection ID to sync (Default: 1): 

Synching 15 files from local to OpenAI
Uploading 15 files to OpenAI file storage
Attaching 15 files to OpenAI vector store

🏁 Sync results:
Saved: 15 | Deleted: 0 | Skipped: 0 
Remote count: 15
Duration: 57.99 seconds
```

#### Settings

Settings are persisted in a local json file which can be purged.
```bash
vs settings clear
```

#### Chat Interactions
Use `vs assistant chat` to chat with uploaded documents via the command line. The responding assistant is automatically linked to your
vector store. Alternatively, you can use `vs assistant ui` to spawn a local Gradio instance.

```bash
vs assistant chat
✅ Assistant found: asst_123456789
Type "exit" to quit at any time.

> Give a one sentence summary of your vector store collection contents.
💬 Conversation started: thread_123456789

The contents of the vector store collection primarily focus on machine learning techniques for causal effect inference,particularly through adversarial representation learning methods that address challenges in treatment selection bias and information loss in observational data
```

Conversations are remembered across sessions.
```bash
vs assistant chat   
✅ Assistant found: asst_123456789
✅ Thread found: thread_123456789
Type "exit" to quit at any time.

> What was my last question to you? 
Your last question to me was asking for a one sentence summary of the contents of my vector store collection.
```

Threads can be cleared using the `-n` flag.
```bash
vs assistant chat -n
✅ Assistant found: asst_123456789
Type "exit" to quit at any time.

> What was my last question to you?
💬 Conversation started: thread_987654321

Your last question was about searching for relevant information from a large number of journals and papers, emphasizing the importance of citing information from the provided sources without making up any content.

# Assistant response is in reference to the system prompt
```

