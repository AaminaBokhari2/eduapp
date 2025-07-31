import gradio as gr
import os
from pipeline import OpenAIClient, EnhancedPDFProcessor, SummaryAgent, FlashcardAgent, QuizAgent

class StudyAssistantOrchestrator:
    def __init__(self):
        self.client = OpenAIClient()
        self.processor = EnhancedPDFProcessor()
        self.summary_agent = SummaryAgent(self.client)
        self.flashcard_agent = FlashcardAgent(self.client)
        self.quiz_agent = QuizAgent(self.client)
        self.last_processed_text = ""
        self.last_file_info = ""

    def process_pdf(self, file):
        """Process uploaded PDF and generate study materials"""
        if file is None:
            return (
                "❌ No file uploaded.",
                "❌ No file uploaded.",
                "❌ No file uploaded.",
                "❌ Please upload a PDF file first."
            )

        try:
            file_path = file.name if hasattr(file, "name") else file
            
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                return (
                    "❌ File not found.",
                    "❌ File not found.",
                    "❌ File not found.",
                    "❌ File not found. Please try uploading again."
                )

            # Get file info
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            self.last_file_info = f"📁 File: {os.path.basename(file_path)} ({file_size:.2f} MB)"

            print(f"Processing file: {file_path}")
            
            # Extract text from PDF
            result = self.processor.extract_text_with_ocr(file_path)

            if result["status"] == "error":
                error_msg = f"❌ {result.get('message', 'Failed to process PDF.')}"
                return (
                    error_msg,
                    error_msg,
                    error_msg,
                    f"{self.last_file_info}\n{error_msg}"
                )

            # Store the extracted text
            self.last_processed_text = result["text"]
            
            # Generate progress message
            info_msg = f"{self.last_file_info}\n{result['message']}"
            
            if result["word_count"] < 50:
                info_msg += "\n⚠️ Limited content extracted. Results may be basic."

            # Generate study materials with progress updates
            try:
                print("Generating summary...")
                summary = self.summary_agent.generate_summary(result["text"])
                if summary.startswith("❌"):
                    summary = f"Summary generation failed.\n{summary}"
            except Exception as e:
                summary = f"❌ Summary generation failed: {str(e)}"

            try:
                print("Generating flashcards...")
                flashcards = self.flashcard_agent.generate_flashcards(result["text"])
                if flashcards.startswith("❌"):
                    flashcards = f"Flashcard generation failed.\n{flashcards}"
            except Exception as e:
                flashcards = f"❌ Flashcard generation failed: {str(e)}"

            try:
                print("Generating quiz...")
                quiz = self.quiz_agent.generate_quiz(result["text"])
                if quiz.startswith("❌"):
                    quiz = f"Quiz generation failed.\n{quiz}"
            except Exception as e:
                quiz = f"❌ Quiz generation failed: {str(e)}"

            return summary, flashcards, quiz, info_msg

        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(f"Error in process_pdf: {e}")
            return (
                error_msg,
                error_msg,
                error_msg,
                f"{self.last_file_info}\n{error_msg}"
            )

    def handle_question(self, question):
        """Handle Q&A questions about the document"""
        if not question.strip():
            return "❓ Please enter a question."

        if not self.last_processed_text:
            return "❌ Please upload and process a PDF document first."

        if len(self.last_processed_text.split()) < 10:
            return "⚠️ Document content too limited for meaningful Q&A."

        try:
            # Truncate text if too long to avoid token limits
            max_chars = 6000
            text_content = self.last_processed_text[:max_chars]
            if len(self.last_processed_text) > max_chars:
                text_content += "..."

            prompt = f"""
            Based on the following document content, please answer the question comprehensively and accurately.

            Document Content:
            {text_content}

            Question: {question}

            Instructions:
            - Provide a detailed, accurate answer based on the document
            - If the information isn't in the document, say so clearly
            - Use specific examples from the document when possible
            - Keep the answer well-structured and easy to understand
            """

            response = self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=1000)
            
            if response.startswith("❌"):
                return f"❌ Failed to generate answer: {response}"
            
            return response

        except Exception as e:
            return f"❌ Error processing question: {str(e)}"

    def clear_session(self):
        """Clear the current session"""
        self.last_processed_text = ""
        self.last_file_info = ""
        return (
            "Session cleared. Upload a new PDF to start.",
            "Session cleared. Upload a new PDF to start.",
            "Session cleared. Upload a new PDF to start.",
            "🔄 Session cleared. Ready for new document.",
            ""
        )

# Initialize the orchestrator
orchestrator = StudyAssistantOrchestrator()

def create_interface():
    """Create the Gradio interface with improved error handling"""

    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px;
        margin: auto;
    }
    .error-text {
        color: #ff4444 !important;
    }
    .success-text {
        color: #44ff44 !important;
    }
    .warning-text {
        color: #ffaa44 !important;
    }
    """

    with gr.Blocks(
        title="AI Study Assistant", 
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:
        
        gr.Markdown("""
        # 📚 AI Study Assistant (Enhanced Multi-Agent System)
        
        Upload your lecture PDFs and get instant summaries, flashcards, quizzes, and ask questions!
        
        **✨ Features:**
        - Smart text extraction with OCR fallback
        - AI-powered summaries and study materials
        - Interactive Q&A system
        - Multiple AI model fallbacks for reliability
        """)

        # Add status indicator
        with gr.Row():
            api_status = gr.Textbox(
                label="🔧 System Status",
                value="Ready to process documents",
                interactive=False,
                max_lines=2
            )

        with gr.Tab("📄 Document Processing"):
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="📎 Upload Lecture PDF",
                        file_types=[".pdf"],
                        file_count="single",
                        height=100
                    )
                    
                    with gr.Row():
                        process_btn = gr.Button("🚀 Process Document", variant="primary", size="sm")
                        clear_btn = gr.Button("🔄 Clear Session", variant="secondary", size="sm")
                    
                    doc_info = gr.Textbox(
                        label="📊 Document Information",
                        lines=6,
                        interactive=False,
                        placeholder="Document information will appear here..."
                    )

                with gr.Column(scale=2):
                    with gr.Tab("📌 Summary"):
                        summary_output = gr.Textbox(
                            label="📝 Key Points Summary",
                            lines=20,
                            interactive=False,
                            placeholder="Summary will appear here after processing..."
                        )

                    with gr.Tab("🧠 Flashcards"):
                        flashcards_output = gr.Textbox(
                            label="🃏 Study Flashcards",
                            lines=20,
                            interactive=False,
                            placeholder="Flashcards will appear here after processing..."
                        )

                    with gr.Tab("📝 Quiz"):
                        quiz_output = gr.Textbox(
                            label="❓ Practice Quiz",
                            lines=20,
                            interactive=False,
                            placeholder="Quiz will appear here after processing..."
                        )

        with gr.Tab("💬 Q&A Chat"):
            gr.Markdown("### 💡 Ask questions about your uploaded document")

            with gr.Row():
                with gr.Column(scale=3):
                    question_input = gr.Textbox(
                        placeholder="Ask anything about the lecture content...",
                        label="🤔 Your Question",
                        lines=3
                    )
                    
                    with gr.Row():
                        ask_btn = gr.Button("🎯 Ask Question", variant="primary")
                        example_btn = gr.Button("💡 Example Questions", variant="secondary")

                with gr.Column(scale=4):
                    answer_output = gr.Textbox(
                        label="🎓 Answer",
                        lines=15,
                        interactive=False,
                        placeholder="Answers will appear here..."
                    )

            # Example questions section
            with gr.Row():
                example_questions = gr.Markdown("""
                **Example Questions to Try:**
                - "What are the main concepts covered in this document?"
                - "Can you explain [specific term] in simple terms?"
                - "What are the key takeaways from this lecture?"
                - "How does [concept A] relate to [concept B]?"
                - "What examples are provided for [topic]?"
                """, visible=False)

        with gr.Tab("🔧 Diagnostics"):
            gr.Markdown("### 🔍 System Diagnostics and Troubleshooting")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    **Common Issues and Solutions:**
                    
                    🔴 **OpenAI Quota/Rate Limit Errors:**
                    - Check your API key in the .env file
                    - Verify you have sufficient credits
                    - Wait a few minutes and try again
                    
                    🔴 **Text Extraction Problems:**
                    - Ensure PDF is not password protected
                    - Try PDFs with clear, readable text
                    - Image-based PDFs may need OCR (slower)
                    
                    🔴 **OCR Issues:**
                    - Install Tesseract if using image-based PDFs
                    - Check if system has sufficient memory
                    """)
                
                with gr.Column():
                    diagnostic_output = gr.Textbox(
                        label="🔍 Diagnostic Results",
                        lines=10,
                        interactive=False,
                        placeholder="Click buttons below to run diagnostics..."
                    )
                    
                    with gr.Row():
                        test_api_btn = gr.Button("🔑 Test OpenAI API", size="sm")
                        test_ocr_btn = gr.Button("👁️ Test OCR", size="sm")
                        system_info_btn = gr.Button("💻 System Info", size="sm")

        with gr.Tab("ℹ️ About & Help"):
            gr.Markdown("""
            ## 🚀 How to Use:
            
            ### 1. **Upload PDF Document**
            - Go to "Document Processing" tab
            - Click "📎 Upload Lecture PDF" and select your file
            - Click "🚀 Process Document" or it will auto-process
            - Wait for processing to complete (may take 30-60 seconds)
            
            ### 2. **Review Generated Content**
            - **📌 Summary**: Structured overview with key concepts
            - **🧠 Flashcards**: Study cards with different difficulty levels  
            - **📝 Quiz**: Multiple choice questions with explanations
            
            ### 3. **Ask Questions**
            - Switch to "💬 Q&A Chat" tab
            - Type specific questions about the document content
            - Get detailed, context-aware answers
            
            ## ✨ Features:
            
            **🤖 Smart Processing:**
            - Automatic text extraction from PDFs
            - OCR fallback for image-based documents
            - Multiple AI model fallbacks for reliability
            
            **📚 Study Materials:**
            - Structured summaries with key concepts
            - Mixed-difficulty flashcards
            - Practice quizzes with explanations
            - Interactive Q&A system
            
            **🛠️ Robust Error Handling:**
            - Clear error messages and troubleshooting tips
            - Automatic retry with different AI models
            - Graceful fallbacks for various file types
            
            ## 💡 Tips for Best Results:
            
            **📄 PDF Requirements:**
            - Use clear, text-based PDFs when possible
            - Ensure documents are not password-protected
            - Smaller files (< 20MB) process faster
            
            **🎯 Question Tips:**
            - Ask specific questions for detailed answers
            - Reference concepts mentioned in the document
            - Use clear, well-formed questions
            
            **⚡ Performance:**
            - Processing may take 30-60 seconds depending on document length
            - Large documents are automatically truncated for efficiency
            - OCR processing (for image PDFs) takes longer
            
            ## 🔧 Troubleshooting:
            
            If you encounter issues:
            1. Check the "🔧 Diagnostics" tab for system tests
            2. Ensure your OpenAI API key is properly configured
            3. Try with a different PDF if extraction fails
            4. Clear session and restart if needed
            
            ## 🎓 Educational Use:
            This tool is designed to enhance learning by:
            - Creating structured study materials
            - Generating practice questions
            - Providing instant answers to questions
            - Supporting active recall and spaced repetition techniques
            """)

        # Diagnostic functions
        def test_openai_api():
            try:
                test_client = OpenAIClient()
                response = test_client.chat_completion([
                    {"role": "user", "content": "Say 'API test successful' to confirm connection."}
                ], max_tokens=20)
                
                if "❌" in response:
                    return f"❌ API Test Failed:\n{response}"
                else:
                    return f"✅ OpenAI API Test Successful!\nResponse: {response}"
            except Exception as e:
                return f"❌ API Test Error: {str(e)}"

        def test_ocr_system():
            try:
                processor = EnhancedPDFProcessor()
                if processor.tesseract_available:
                    return "✅ OCR (Tesseract) is available and working!"
                else:
                    return "⚠️ OCR (Tesseract) is not available. Image-based PDFs won't work."
            except Exception as e:
                return f"❌ OCR Test Error: {str(e)}"

        def get_system_info():
            import platform
            import sys
            
            info = f"""
            🖥️ System Information:
            - OS: {platform.system()} {platform.release()}
            - Python: {sys.version.split()[0]}
            - Architecture: {platform.machine()}
            
            📦 Key Dependencies:
            - OpenAI API: {'✅ Connected' if os.getenv('OPENAI_API_KEY') else '❌ No API Key'}
            - OCR Support: {'✅ Available' if orchestrator.processor.tesseract_available else '❌ Not Available'}
            
            💾 Current Session:
            - Document Loaded: {'✅ Yes' if orchestrator.last_processed_text else '❌ No'}
            - Content Length: {len(orchestrator.last_processed_text.split()) if orchestrator.last_processed_text else 0} words
            """
            return info

        def show_example_questions():
            return gr.update(visible=True)

        # Event handlers
        file_input.upload(
            orchestrator.process_pdf,
            inputs=[file_input],
            outputs=[summary_output, flashcards_output, quiz_output, doc_info]
        )

        process_btn.click(
            orchestrator.process_pdf,
            inputs=[file_input],
            outputs=[summary_output, flashcards_output, quiz_output, doc_info]
        )

        clear_btn.click(
            orchestrator.clear_session,
            outputs=[summary_output, flashcards_output, quiz_output, doc_info, answer_output]
        )

        question_input.submit(
            orchestrator.handle_question,
            inputs=[question_input],
            outputs=[answer_output]
        )

        ask_btn.click(
            orchestrator.handle_question,
            inputs=[question_input],
            outputs=[answer_output]
        )

        example_btn.click(
            show_example_questions,
            outputs=[example_questions]
        )

        # Diagnostic button handlers
        test_api_btn.click(
            test_openai_api,
            outputs=[diagnostic_output]
        )

        test_ocr_btn.click(
            test_ocr_system,
            outputs=[diagnostic_output]
        )

        system_info_btn.click(
            get_system_info,
            outputs=[diagnostic_output]
        )

    return demo

if __name__ == "__main__":
    # Check for API key before starting
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ WARNING: No OpenAI API key found!")
        print("💡 Please set OPENAI_API_KEY in your .env file")
        print("Example .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("\n🚀 Starting anyway - you can test the interface...")
    
    demo = create_interface()
    
    print("\n🎓 AI Study Assistant Starting...")
    print("📱 Interface will be available at: http://localhost:7860")
    print("🔧 Check the Diagnostics tab if you encounter issues")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )