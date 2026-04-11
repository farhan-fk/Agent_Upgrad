# =========================================
# RAG Chatbot with Gradio UI
# =========================================
# Chat works with or without document upload
# =========================================

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import gradio as gr

load_dotenv()
client = OpenAI()

# Global state
current_vector_store_id = None
current_filename = None


def create_vector_store(name="chatbot_docs"):
    """Step 1: Create a vector store to hold your documents"""
    try:
        vector_store = client.beta.vector_stores.create(name=name)
    except AttributeError:
        vector_store = client.vector_stores.create(name=name)
    
    return vector_store.id


def upload_document(vector_store_id, file_path):
    """Step 2: Upload and index a document into the vector store"""
    with Path(file_path).open("rb") as f:
        try:
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
            )
        except AttributeError:
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
            )


def ask_question_with_rag(vector_store_id, question):
    """Ask a question about the document using RAG"""
    response = client.responses.create(
        model="gpt-5-nano",
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }],
    )
    return response.output_text


def ask_question_general(question):
    """Ask a general question without document context"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using a standard chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You can answer general questions and have conversations with users."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content


def upload_and_index(file):
    """Handle document upload"""
    global current_vector_store_id, current_filename
    
    if file is None:
        return "⚠️ Please select a PDF file first"
    
    try:
        current_vector_store_id = create_vector_store()
        upload_document(current_vector_store_id, file.name)
        current_filename = Path(file.name).name
        
        return f"✅ SUCCESS!\n\nDocument '{current_filename}' has been uploaded and indexed.\n\nNow I can answer questions about this document!"
    
    except Exception as e:
        return f"❌ ERROR:\n{str(e)}"


def clear_document():
    """Clear the uploaded document"""
    global current_vector_store_id, current_filename
    current_vector_store_id = None
    current_filename = None
    return "🔄 Document cleared. I'm now in general chat mode."


def chat_with_doc(message, history):
    """Chat function - works with or without document"""
    global current_vector_store_id, current_filename
    
    if not message.strip():
        return history
    
    try:
        # Check if document is uploaded
        if current_vector_store_id is None:
            # General chat mode
            answer = ask_question_general(message)
            prefix = "💬 "
        else:
            # Document Q&A mode
            answer = ask_question_with_rag(current_vector_store_id, message)
            prefix = f"📄 [{current_filename}] "
        
        history.append([message, prefix + answer])
        return history
    
    except Exception as e:
        history.append([message, f"❌ Error: {str(e)}"])
        return history


def get_current_mode():
    """Get the current chat mode"""
    global current_vector_store_id, current_filename
    
    if current_vector_store_id is None:
        return "💬 **Mode:** General Chat\n\nI can answer general questions and have conversations. Upload a PDF to ask questions about a specific document."
    else:
        return f"📄 **Mode:** Document Q&A\n\n**Current Document:** {current_filename}\n\nI'm now answering questions based on your document. Click 'Clear Document' to return to general chat mode."


# =========================================
# MAIN INTERFACE
# =========================================

with gr.Blocks(title="RAG Chatbot") as demo:
    
    gr.Markdown(
        """
        # 🤖 Smart AI Chatbot with Document Q&A
        ### Chat normally OR upload a PDF to ask questions about it
        """
    )
    
    with gr.Row():
        # Left Column: Document Management
        with gr.Column(scale=1):
            gr.Markdown("### 📁 Document Management (Optional)")
            
            mode_status = gr.Markdown(
                "💬 **Mode:** General Chat\n\nUpload a PDF to enable document Q&A mode."
            )
            
            gr.Markdown("---")
            
            file_input = gr.File(
                label="Upload PDF (Optional)",
                file_types=[".pdf"]
            )
            
            upload_button = gr.Button("📤 Upload & Index", variant="primary")
            
            upload_status = gr.Textbox(
                label="Upload Status",
                lines=3,
                interactive=False,
                placeholder="No document uploaded yet"
            )
            
            gr.Markdown("---")
            
            clear_button = gr.Button("🔄 Clear Document", variant="secondary")
            
            refresh_mode = gr.Button("🔄 Refresh Mode Status", size="sm")
        
        # Right Column: Chat Interface
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat")
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=450
            )
            
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Ask me anything or upload a PDF to ask about a specific document...",
                lines=2
            )
            
            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear_chat = gr.Button("Clear Chat")
            
            gr.Markdown(
                """
                **💡 Tips:**
                - Without document: Ask general questions, have conversations
                - With document: Ask specific questions about the uploaded PDF
                
                **Example questions (general):**
                - What can you help me with?
                - Explain quantum computing
                - Write a poem about AI
                
                **Example questions (with document):**
                - What is this document about?
                - Summarize the key points
                - Find information about [specific topic]
                """
            )
    
    # Event Handlers
    upload_button.click(
        fn=upload_and_index,
        inputs=[file_input],
        outputs=[upload_status]
    ).then(
        fn=get_current_mode,
        outputs=[mode_status]
    )
    
    clear_button.click(
        fn=clear_document,
        outputs=[upload_status]
    ).then(
        fn=get_current_mode,
        outputs=[mode_status]
    )
    
    refresh_mode.click(
        fn=get_current_mode,
        outputs=[mode_status]
    )
    
    # Chat functionality
    submit.click(
        fn=chat_with_doc,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    ).then(
        lambda: "",
        outputs=[msg]
    )
    
    msg.submit(
        fn=chat_with_doc,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    ).then(
        lambda: "",
        outputs=[msg]
    )
    
    clear_chat.click(
        lambda: [],
        outputs=[chatbot]
    )
    
    # Footer
    gr.Markdown(
        """
        ---
        ### 🧠 How it works:
        - **General Mode**: Uses GPT-4o-mini for normal conversations
        - **Document Mode**: Uses GPT-5-nano with RAG to answer questions based on your PDF
        - Switch between modes anytime by uploading or clearing documents
        
        **Powered by:** OpenAI API with intelligent context switching
        """
    )


if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7861
    )