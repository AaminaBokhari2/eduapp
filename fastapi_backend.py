#!/usr/bin/env python3
"""
FastAPI Backend for AI Study Assistant
This wraps your existing pipeline.py functionality in a REST API
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from typing import List, Dict, Optional
import json
from pydantic import BaseModel

# Import your existing classes
from pipeline import (
    OpenAIClient, EnhancedPDFProcessor, SummaryAgent, 
    FlashcardAgent, QuizAgent, EnhancedResearchDiscoveryAgent, 
    YouTubeDiscoveryAgent, WebResourceAgent
)

# Initialize FastAPI app
app = FastAPI(
    title="AI Study Assistant API",
    description="Backend API for AI-powered study material generation",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://bolt.new",       # Bolt.new
        "https://*.bolt.new",     # Bolt.new subdomains
        "*"  # Allow all origins for development (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class ProcessingStatus(BaseModel):
    status: str
    message: str
    word_count: int
    page_count: int
    methods_used: List[str]

class SummaryResponse(BaseModel):
    summary: str
    status: str

class FlashcardResponse(BaseModel):
    flashcards: List[Dict]
    count: int
    status: str

class QuizResponse(BaseModel):
    quiz: List[Dict]
    count: int
    status: str

class ResearchPapersResponse(BaseModel):
    papers: List[Dict]
    count: int
    status: str

class VideosResponse(BaseModel):
    videos: List[Dict]
    count: int
    status: str

class WebResourcesResponse(BaseModel):
    resources: List[Dict]
    count: int
    status: str

class QuestionRequest(BaseModel):
    question: str
    document_text: str

class AnswerResponse(BaseModel):
    answer: str
    status: str

# Global variables to store state (in production, use Redis or database)
study_sessions = {}

# Initialize agents
try:
    client = OpenAIClient()
    pdf_processor = EnhancedPDFProcessor()
    summary_agent = SummaryAgent(client)
    flashcard_agent = FlashcardAgent(client)
    quiz_agent = QuizAgent(client)
    research_agent = EnhancedResearchDiscoveryAgent(client)
    youtube_agent = YouTubeDiscoveryAgent(client)
    web_agent = WebResourceAgent(client)
    print("✅ All agents initialized successfully")
except Exception as e:
    print(f"❌ Error initializing agents: {e}")
    raise

@app.get("/")
async def root():
    return {"message": "AI Study Assistant API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": "initialized"}

@app.post("/upload-pdf", response_model=ProcessingStatus)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Process PDF
        result = pdf_processor.extract_text_with_ocr(temp_file_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Store session data (use session ID in production)
        session_id = "default"  # In production, generate unique session IDs
        study_sessions[session_id] = {
            "text": result["text"],
            "file_info": f"File: {file.filename} ({len(content)/1024/1024:.2f} MB)",
            "processing_result": result
        }
        
        return ProcessingStatus(
            status=result["status"],
            message=result["message"],
            word_count=result["word_count"],
            page_count=result["page_count"],
            methods_used=result["methods_used"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/generate-summary", response_model=SummaryResponse)
async def generate_summary(session_id: str = "default"):
    """Generate summary from processed document"""
    
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="No document found. Please upload a PDF first.")
    
    try:
        text = study_sessions[session_id]["text"]
        summary = summary_agent.generate_summary(text)
        
        return SummaryResponse(
            summary=summary,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@app.post("/generate-flashcards", response_model=FlashcardResponse)
async def generate_flashcards(session_id: str = "default", num_cards: int = 10):
    """Generate flashcards from processed document"""
    
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="No document found. Please upload a PDF first.")
    
    try:
        text = study_sessions[session_id]["text"]
        flashcards = flashcard_agent.generate_flashcards_structured(text, num_cards)
        
        return FlashcardResponse(
            flashcards=flashcards,
            count=len(flashcards),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {str(e)}")

@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(session_id: str = "default", num_questions: int = 8):
    """Generate quiz from processed document"""
    
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="No document found. Please upload a PDF first.")
    
    try:
        text = study_sessions[session_id]["text"]
        quiz = quiz_agent.generate_quiz_structured(text, num_questions)
        
        return QuizResponse(
            quiz=quiz,
            count=len(quiz),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

@app.post("/discover-research", response_model=ResearchPapersResponse)
async def discover_research(session_id: str = "default", max_papers: int = 10):
    """Discover research papers related to the document"""
    
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="No document found. Please upload a PDF first.")
    
    try:
        text = study_sessions[session_id]["text"]
        papers = research_agent.find_papers(text, max_papers)
        
        return ResearchPapersResponse(
            papers=papers,
            count=len(papers),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research discovery failed: {str(e)}")

@app.post("/discover-videos", response_model=VideosResponse)
async def discover_videos(session_id: str = "default", max_videos: int = 10):
    """Discover YouTube videos related to the document"""
    
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="No document found. Please upload a PDF first.")
    
    try:
        text = study_sessions[session_id]["text"]
        # Extract keywords for video search
        topic, research_keywords, all_keywords = research_agent.extract_smart_keywords_and_topic(text)
        videos = youtube_agent.find_videos(research_keywords, topic, max_videos)
        
        return VideosResponse(
            videos=videos,
            count=len(videos),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video discovery failed: {str(e)}")

@app.post("/discover-resources", response_model=WebResourcesResponse)
async def discover_resources(session_id: str = "default", max_resources: int = 12):
    """Discover web resources related to the document"""
    
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="No document found. Please upload a PDF first.")
    
    try:
        text = study_sessions[session_id]["text"]
        # Extract keywords for resource search
        topic, research_keywords, all_keywords = research_agent.extract_smart_keywords_and_topic(text)
        resources = web_agent.find_resources(research_keywords, topic, max_resources)
        
        return WebResourcesResponse(
            resources=resources,
            count=len(resources),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resource discovery failed: {str(e)}")

@app.post("/ask-question", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Answer questions about the document"""
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not request.document_text.strip():
        raise HTTPException(status_code=400, detail="No document text provided")
    
    try:
        # Limit text for analysis
        max_chars = 6000
        text_content = request.document_text[:max_chars]
        if len(request.document_text) > max_chars:
            text_content += "..."

        prompt = f"""Based on the following document content, please answer the question comprehensively and accurately.

Document Content:
{text_content}

Question: {request.question}

Instructions:
- Provide a detailed, accurate answer based on the document
- If the information isn't in the document, say so clearly
- Use specific examples from the document when possible
- Keep the answer well-structured and easy to understand"""

        response = client.chat_completion([{"role": "user", "content": prompt}], max_tokens=800)
        
        return AnswerResponse(
            answer=response,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")

@app.delete("/clear-session")
async def clear_session(session_id: str = "default"):
    """Clear session data"""
    
    if session_id in study_sessions:
        del study_sessions[session_id]
        return {"message": "Session cleared successfully", "status": "success"}
    else:
        return {"message": "No active session found", "status": "info"}

@app.get("/session-info")
async def get_session_info(session_id: str = "default"):
    """Get information about current session"""
    
    if session_id not in study_sessions:
        return {"active": False, "message": "No active session"}
    
    session_data = study_sessions[session_id]
    return {
        "active": True,
        "file_info": session_data.get("file_info", ""),
        "word_count": session_data.get("processing_result", {}).get("word_count", 0),
        "page_count": session_data.get("processing_result", {}).get("page_count", 0),
        "methods_used": session_data.get("processing_result", {}).get("methods_used", [])
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Study Assistant API...")
    print("📱 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    
    uvicorn.run(
        "api_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )