import gradio as gr

from .chat_manager import ChatManager


class ChatUI:
    """User interface for the recipe chat assistant.

    This class provides static methods for creating and launching
    a Gradio-based chat interface for the recipe assistant.
    """

    @staticmethod
    def _create_chat_interface(chat_manager: ChatManager) -> gr.Blocks:
        """Create a Gradio chat interface for the recipe assistant.

        This method sets up the UI components and event handlers
        for the chat interface.

        Args:
            chat_manager: The chat manager to handle message processing

        Returns:
            A Gradio Blocks interface
        """

        with gr.Blocks(title="Recipe Assistant") as interface:
            gr.Markdown("# Recipe Assistant")

            with gr.Row():
                with gr.Column(scale=8):
                    gr.Markdown("Ask me about recipes, cooking instructions, or nutritional information!")
                with gr.Column(scale=1):
                    streaming_toggle = gr.Checkbox(label="Stream", value=True, interactive=True)

            chatbot = gr.Chatbot(
                label="Chat",
                height=800,
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="What recipe would you like to know about?",
                    label="Your message",
                    scale=9,
                    container=False,
                )
                submit = gr.Button("Send", scale=1, variant="primary")

            with gr.Row():
                clear = gr.Button("Clear Chat")

            def handle_submit(message: str, chat_history, streaming_enabled: bool):
                """Handle message submission with validation."""
                # Skip processing if message is empty or only whitespace
                if not message or not message.strip():
                    return chat_history, ""

                # Add user message and clear input
                updated_history, cleared_input = chat_manager.add_user_message(message, chat_history)

                # Process the message
                if streaming_enabled:
                    for result in chat_manager.stream_user_message(message, updated_history):
                        yield result, cleared_input
                else:
                    for result in chat_manager.process_user_message(message, updated_history):
                        yield result, cleared_input

            submit.click(
                fn=handle_submit,
                inputs=[msg, chatbot, streaming_toggle],
                outputs=[chatbot, msg],
                queue=True,
            )

            msg.submit(
                fn=handle_submit,
                inputs=[msg, chatbot, streaming_toggle],
                outputs=[chatbot, msg],
                queue=True,
            )

            clear.click(
                fn=chat_manager.clear_history,
                inputs=None,
                outputs=[chatbot],
                queue=False,
            ).then(
                fn=lambda: "",
                inputs=None,
                outputs=[msg],
            )

            # Add some examples:
            gr.Examples(
                examples=[
                    "What's a good recipe for chicken parmesan?",
                    "How do I make a chocolate cake?",
                    "What are some healthy breakfast options?",
                    "Can you suggest a vegetarian dinner recipe?",
                    "What nutritional benefits does spinach have?",
                ],
                inputs=msg,
            )

        return interface

    @staticmethod
    def launch_chat_interface(
        chat_manager: ChatManager,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        share: bool = False,
    ) -> None:
        """Launch the chat interface.

        This method creates and launches the Gradio interface
        with the specified server configuration.

        Args:
            chat_manager: The chat manager to handle message processing
            server_name: The server hostname (default: "127.0.0.1")
            server_port: The server port (default: 7860)
            share: Whether to create a public link (default: False)
        """
        interface = ChatUI._create_chat_interface(chat_manager)
        interface.launch(server_name=server_name, server_port=server_port, share=share)
