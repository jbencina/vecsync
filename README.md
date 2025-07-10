# vecsync
[![GitHub](https://img.shields.io/badge/GitHub-repo-green.svg)](https://github.com/jbencina/vecsync)
[![PyPI](https://img.shields.io/pypi/v/vecsync)](https://pypi.org/project/vecsync)
[![image](https://img.shields.io/pypi/l/vecsync.svg)](https://pypi.python.org/pypi/vecsync)
[![image](https://img.shields.io/pypi/pyversions/vecsync.svg)](https://pypi.python.org/pypi/vecsync)
[![Actions status](https://github.com/jbencina/vecsync/actions/workflows/ci.yaml/badge.svg)](https://github.com/jbencina/vecsync/actions)

A fast command-line utility for synchronizing journals and papers to OpenAI vector storage for chat interaction. Vecsync helps you research topics by simpliyfing your workflow.

- 📄 Synchronize a local collection of PDFs to a remote vector store
- ✅ Automatically manage OpenAI files, vector store, and assistant
- 💬 Quickly chat with documents from command line or local Gradio UI
- 👀 Connect to a local [Zotero](https://www.zotero.org/) collection


**Sync and chat**
```bash
vs sync && vs chat
```
![demo](docs/images/demo.gif)

**Chat with [Gradio](https://www.gradio.app)**
```bash
vs chat --ui
```
![chat](docs/images/demo_chat.png)

## Getting Started
> **OpenAI API Requirements**
>
> Currently vecsync only supports OpenAI for remote operations and requires a valid OpenAI key with credits. Visit https://openai.com/api/ for more information.

> **Costs**
>
> Vecsync uses OpenAI gpt-4o-mini which is Input: $0.15/million tokens and Output: $0.60/million tokens. These costs are tied to your OpenAI API account. See [pricing](https://platform.openai.com/docs/pricing) for details.

### Installation
Install vecsync from PyPI.
```
pip install vecsync
```

Set your OpenAI API key environment.
```
export OPENAI_API_KEY=...
```
You can also define the key via `.env` file in the working directory.
```
echo "OPENAI_API_KEY=…" > .env
```

### Usage

#### Syncing Collections
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
vs sync -source zotero

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

#### Chat Interactions
Use `vs chat` to chat with uploaded documents via the command line. The responding assistant is automatically linked to your
vector store. Alternatively, you can use `vs chat --ui` to spawn a local Gradio instance.

```bash
vs chat
✅ Assistant found: asst_123456789
Type "exit" to quit at any time.

> Give a one sentence summary of your vector store collection contents.
💬 Conversation started: thread_123456789

The contents of the vector store collection primarily focus on machine learning techniques for causal effect inference,particularly through adversarial representation learning methods that address challenges in treatment selection bias and information loss in observational data
```

Conversations are remembered across sessions.
```bash
vs chat   
✅ Assistant found: asst_123456789
✅ Thread found: thread_123456789
Type "exit" to quit at any time.

> What was my last question to you? 
Your last question to me was asking for a one sentence summary of the contents of my vector store collection.
```
