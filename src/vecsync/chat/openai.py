from openai import OpenAI
from vecsync.store.openai import OpenAiVectorStore
import sys


class OpenAiChat:
    def __init__(self, store_name: str):
        self.client = OpenAI()
        self.vector_store = OpenAiVectorStore(store_name)
        self.vector_store.get()

    def create(self, name: str):
        instructions = """You are a helpful research assistant that can search through a large number
        of journals and papers to find revelant information. It is very important that you
        remain factual and cite information from the sources provided to you in the 
        vector store. You are not allowed to make up information"""

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=[{"type": "file_search"}],  # Required to use vector stores
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_store.store.id],
                }
            },
            model="gpt-4o-mini",
        )

        print(f"✅ Assistant created: {assistant.id}")

        # (Optional) Generate a fake "URL" if you had a frontend
        print(
            f"🔗 Assistant URL: https://platform.openai.com/assistants/{assistant.id}"
        )

    def chat(self, prompt: str) -> str:
        stream = self.client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [self.vector_store.store.id],
                }
            ],
            stream=True,
        )
        full_text = ""

        for event in stream:
            if event.type == "response.output_text.delta":
                delta = event.delta
                full_text += delta
                # print each new character immediately
                for ch in delta:
                    sys.stdout.write(ch)
                    sys.stdout.flush()
