import sys
from concurrent.futures import ThreadPoolExecutor

import gradio as gr

from vecsync.chat.clients.openai import OpenAIClient, OpenAIHandler
from vecsync.chat.formatter import ConsoleFormatter, GradioFormatter


class ConsoleInterface:
    def __init__(self, client: OpenAIClient):
        self.client = client
        self.executor = ThreadPoolExecutor(max_workers=1)

    def prompt(self, prompt_text: str):
        fmt = ConsoleFormatter()
        handler = OpenAIHandler(self.client.files, fmt)

        self.client.send_message(prompt_text)

        self.executor.submit(self.client.stream_response, self.client.thread_id, self.client.assistant_id, handler)
        for chunk in handler.consume_queue():
            sys.stdout.write(chunk)
            sys.stdout.flush()


class GradioInterface:
    def __init__(self, client: OpenAIClient):
        self.client = client
        self.executor = ThreadPoolExecutor(max_workers=1)

    def chat_interface(self):
        def gradio_prompt(message, history):
            fmt = GradioFormatter()
            handler = OpenAIHandler(self.client.files, fmt)

            self.client.send_message(message)

            self.executor.submit(self.client.stream_response, self.client.thread_id, self.client.assistant_id, handler)
            response = ""

            for chunk in handler.consume_queue():
                response += chunk
                yield response

        # Gradio doesn't automatically scroll to the bottom of the chat window to accomodate
        # chat history so we add some JavaScript to perform this action on load
        # See: https://github.com/gradio-app/gradio/issues/11109

        js = """
                function Scrolldown() {
                const targetNode = document.querySelector('[aria-label="chatbot conversation"]');
                if (!targetNode) return;

                targetNode.scrollTop = targetNode.scrollHeight;

                const observer = new MutationObserver(() => {
                    targetNode.scrollTop = targetNode.scrollHeight;
                });

                observer.observe(targetNode, { childList: true, subtree: true });
                }

            """
        history = self.client.load_history()

        with gr.Blocks(theme=gr.themes.Base(), js=js) as demo:
            bot = gr.Chatbot(value=history, height="70vh", type="messages")

            gr.Markdown(
                """
                <center><h1>Vecsync Assistant</h1></center>
                """
            )

            gr.ChatInterface(
                fn=gradio_prompt,
                type="messages",
                chatbot=bot,
            )

            demo.launch()
