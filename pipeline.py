#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path
import time
import json
import re

import openai
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

##### OPENAI CLIENT WITH IMPROVED ERROR HANDLING #####
class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_fallbacks = [
            "gpt-3.5-turbo",  # Most commonly available
            "gpt-3.5-turbo-1106",
            "gpt-4o-mini",  # Cheaper alternative
        ]

    def chat_completion(self, messages: List[Dict], model: str = None, max_tokens: int = None, retry_count: int = 3) -> str:
        if model is None:
            models_to_try = self.model_fallbacks
        else:
            models_to_try = [model] + [m for m in self.model_fallbacks if m != model]
        
        for attempt in range(retry_count):
            for model_name in models_to_try:
                try:
                    print(f"Trying model: {model_name} (attempt {attempt + 1})")
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=0.7
                    )
                    return response.choices[0].message.content.strip()
                
                except openai.RateLimitError as e:
                    print(f"Rate limit hit with {model_name}: {str(e)}")
                    if attempt < retry_count - 1:
                        wait_time = (attempt + 1) * 10
                        print(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    continue
                
                except openai.AuthenticationError as e:
                    return f"❌ Authentication Error: Please check your OpenAI API key. {str(e)}"
                
                except openai.InsufficientQuotaError as e:
                    print(f"Quota exceeded for {model_name}: {str(e)}")
                    continue
                
                except openai.BadRequestError as e:
                    print(f"Bad request with {model_name}: {str(e)}")
                    continue
                
                except Exception as e:
                    print(f"Unexpected error with {model_name}: {str(e)}")
                    continue
        
        return "❌ All AI models failed. Please check your OpenAI API key, quota, and internet connection."

##### ENHANCED PDF PROCESSOR WITH BETTER ERROR HANDLING #####
class EnhancedPDFProcessor:
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
        print(f"Tesseract available: {self.tesseract_available}")

    def _check_tesseract(self) -> bool:
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            print(f"Tesseract not available: {e}")
            return False

    def extract_text_with_ocr(self, file_path: str, max_pages: int = 20) -> Dict[str, any]:
        result = {
            "text": "",
            "page_count": 0,
            "extracted_pages": 0,
            "ocr_pages": 0,
            "word_count": 0,
            "status": "success",
            "methods_used": [],
            "message": "",
            "error_details": []
        }

        if not os.path.exists(file_path):
            result["status"] = "error"
            result["message"] = f"File not found: {file_path}"
            return result

        try:
            print(f"Processing PDF: {file_path}")
            text_content = ""
            ocr_content = ""

            # Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    result["page_count"] = len(pdf.pages)
                    pages_to_process = min(result["page_count"], max_pages)
                    print(f"PDF has {result['page_count']} pages, processing {pages_to_process}")

                    for page_num, page in enumerate(pdf.pages[:pages_to_process], 1):
                        try:
                            page_text = page.extract_text()
                            if page_text and len(page_text.strip()) > 20:  # Lowered threshold
                                text_content += f"\n--- Page {page_num} ---\n{page_text.strip()}\n"
                                result["extracted_pages"] += 1
                                print(f"Extracted text from page {page_num}: {len(page_text)} chars")
                            else:
                                print(f"Page {page_num}: No meaningful text found")
                        except Exception as e:
                            result["error_details"].append(f"Page {page_num}: {str(e)}")
                            continue

                    if result["extracted_pages"] > 0:
                        result["methods_used"].append("text_extraction")
                        print(f"Successfully extracted text from {result['extracted_pages']} pages")

            except Exception as e:
                result["error_details"].append(f"PDFPlumber error: {str(e)}")
                print(f"PDFPlumber failed: {e}")

            # Try OCR if text extraction failed or yielded poor results
            if (result["extracted_pages"] == 0 or 
                result["extracted_pages"] < result["page_count"] * 0.3):  # Less than 30% success
                
                if self.tesseract_available:
                    print("Attempting OCR extraction...")
                    try:
                        ocr_content = self._extract_with_ocr(file_path, max_pages=min(5, result["page_count"]))
                        if ocr_content:
                            result["methods_used"].append("ocr")
                            result["ocr_pages"] = ocr_content.count("--- Page")
                            print(f"OCR extracted text from {result['ocr_pages']} pages")
                    except Exception as e:
                        result["error_details"].append(f"OCR error: {str(e)}")
                        print(f"OCR failed: {e}")
                else:
                    result["error_details"].append("OCR not available (Tesseract not installed)")

            # Combine results
            final_text = text_content + ocr_content
            result["text"] = final_text.strip()
            result["word_count"] = len(final_text.split())

            # Set final status and message
            if result["word_count"] > 50:  # Minimum viable content
                methods = " + ".join(result["methods_used"])
                result["message"] = f"✅ Successfully extracted {result['word_count']} words using: {methods}"
                result["status"] = "success"
            elif result["word_count"] > 0:
                result["status"] = "warning"
                result["message"] = f"⚠️ Limited content extracted ({result['word_count']} words). PDF may be image-based or have formatting issues."
            else:
                result["status"] = "error"
                result["message"] = "❌ No text could be extracted. PDF might be image-based, protected, or corrupted."
                if result["error_details"]:
                    result["message"] += f"\nErrors: {'; '.join(result['error_details'][:3])}"

            print(f"Final result: {result['status']} - {result['word_count']} words")
            return result

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"❌ Critical error processing PDF: {str(e)}"
            result["error_details"].append(str(e))
            return result

    def _extract_with_ocr(self, file_path: str, max_pages: int = 5) -> str:
        if not self.tesseract_available:
            return ""

        ocr_text = ""
        temp_dir = tempfile.mkdtemp()

        try:
            print(f"Converting PDF to images for OCR (max {max_pages} pages)...")
            images = convert_from_path(
                file_path, 
                first_page=1, 
                last_page=max_pages, 
                output_folder=temp_dir,
                dpi=200  # Good balance of quality vs speed
            )
            
            for i, image in enumerate(images, 1):
                try:
                    print(f"Processing image {i} with OCR...")
                    # Use more aggressive OCR settings for better results
                    page_text = pytesseract.image_to_string(
                        image, 
                        lang='eng', 
                        config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\'-/\\@#$%^&*+=<>|`~_ \n\t'
                    )
                    if page_text.strip():
                        ocr_text += f"\n--- Page {i} (OCR) ---\n{page_text.strip()}\n"
                        print(f"OCR page {i}: {len(page_text)} chars")
                except Exception as e:
                    print(f"OCR failed on page {i}: {e}")
                    continue
            
            return ocr_text
        
        except Exception as e:
            print(f"OCR process failed: {e}")
            return ""
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

##### ENHANCED STUDY AGENTS WITH BETTER PROMPTS #####
class SummaryAgent:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def generate_summary(self, text: str) -> str:
        if not text.strip():
            return "❌ No content available to summarize."
        
        if len(text.split()) < 10:
            return "⚠️ Content too short for meaningful summary."
        
        # Truncate text if too long
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""
        Create a comprehensive, well-structured summary of the following academic content. Use clear headings and bullet points for easy reading.

        **Document Content:**
        {text}

        **Please structure your summary as follows:**

        ## 📋 DOCUMENT OVERVIEW
        - Main topic and purpose
        - Document type (lecture, textbook chapter, research paper, etc.)

        ## 🎯 KEY CONCEPTS & DEFINITIONS
        List the 5-8 most important concepts with brief explanations:
        - **Concept 1**: Brief definition and significance
        - **Concept 2**: Brief definition and significance
        [Continue for each key concept]

        ## 📝 DETAILED SUMMARY
        Write 2-3 paragraphs providing a comprehensive overview of the content, including:
        - Main arguments or points
        - Supporting evidence or examples
        - Relationships between concepts
        - Any conclusions or implications

        ## 🔑 CRITICAL TAKEAWAYS
        List 4-6 essential points that students must remember:
        1. Most important point
        2. Second most important point
        [Continue...]

        ## 📚 STUDY FOCUS AREAS
        Highlight areas that deserve extra attention:
        - Complex concepts that need deeper understanding
        - Topics likely to appear on exams
        - Practical applications

        Make the summary engaging, clear, and educational. Use formatting to make it easy to scan and study from.
        """
        
        return self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=1500)

class FlashcardAgent:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def generate_flashcards(self, text: str, num_cards=10) -> str:
        if not text.strip():
            return "❌ No content available for flashcards."
        
        if len(text.split()) < 20:
            return "⚠️ Content too short for meaningful flashcards."
        
        # Truncate text if too long
        max_chars = 7000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""
        Create {num_cards} high-quality study flashcards based on the following content. Make them diverse and educational, covering different aspects and difficulty levels.

        **Content to process:**
        {text}

        **Create a mix of the following types:**
        - Definitions (What is...?)
        - Applications (How is... used?)
        - Comparisons (What's the difference between...?)
        - Processes (How does... work?)
        - Examples (Give an example of...)
        - Analysis (Why is... important?)

        **For each flashcard, use this EXACT format:**

        CARD 1:
        Q: [Write a clear, specific question that tests understanding]
        A: [Provide a comprehensive answer with examples and context]
        DIFFICULTY: [Basic/Intermediate/Advanced]
        CATEGORY: [Main topic this relates to]
        HINT: [Optional helpful hint or memory aid]
        ---

        CARD 2:
        Q: [Next question]
        A: [Next answer]
        DIFFICULTY: [Basic/Intermediate/Advanced]
        CATEGORY: [Main topic this relates to]
        HINT: [Optional helpful hint or memory aid]
        ---

        [Continue for all {num_cards} cards]

        **Guidelines:**
        - Make questions specific and test actual understanding, not just memorization
        - Include relevant examples in answers
        - Vary difficulty: 40% Basic, 40% Intermediate, 20% Advanced
        - Add memory hints for complex concepts
        - Keep questions clear and answers comprehensive but concise
        """
        
        return self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=2500)

    def generate_flashcards_structured(self, text: str, num_cards=10) -> List[Dict]:
        """Generate structured flashcards data for the app interface"""
        if not text.strip():
            return []
        
        if len(text.split()) < 20:
            return []
        
        # Truncate text if too long
        max_chars = 7000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""
        Create {num_cards} high-quality study flashcards based on the following content. Return them as a JSON array.

        **Content to process:**
        {text}

        **Return format (valid JSON only):**
        [
            {{
                "question": "Clear, specific question",
                "answer": "Comprehensive answer with examples",
                "difficulty": "Basic|Intermediate|Advanced",
                "category": "Main topic category",
                "hint": "Optional memory aid or hint"
            }},
            ...
        ]

        **Guidelines:**
        - Create diverse question types (definitions, applications, comparisons, processes)
        - Test understanding, not just memorization
        - Include relevant examples in answers
        - Vary difficulty: 40% Basic, 40% Intermediate, 20% Advanced
        - Keep questions clear and answers comprehensive but concise
        """
        
        response = self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=2500)
        
        try:
            # Try to parse JSON response
            flashcards_data = json.loads(response)
            if isinstance(flashcards_data, list):
                return flashcards_data
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse text format
        return self._parse_flashcards_from_text(response)

    def _parse_flashcards_from_text(self, text: str) -> List[Dict]:
        """Parse flashcards from text format as fallback"""
        flashcards = []
        cards = text.split("---")
        
        for card in cards:
            if not card.strip():
                continue
                
            lines = card.strip().split("\n")
            flashcard = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith("Q:"):
                    flashcard["question"] = line[2:].strip()
                elif line.startswith("A:"):
                    flashcard["answer"] = line[2:].strip()
                elif line.startswith("DIFFICULTY:"):
                    flashcard["difficulty"] = line[11:].strip()
                elif line.startswith("CATEGORY:"):
                    flashcard["category"] = line[9:].strip()
                elif line.startswith("HINT:"):
                    flashcard["hint"] = line[5:].strip()
            
            if flashcard.get("question") and flashcard.get("answer"):
                flashcards.append(flashcard)
        
        return flashcards

class QuizAgent:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def generate_quiz(self, text: str, num_questions=8) -> str:
        if not text.strip():
            return "❌ No content available for quiz generation."
        
        if len(text.split()) < 30:
            return "⚠️ Content too short for meaningful quiz questions."
        
        # Truncate text if too long
        max_chars = 7000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""
        Create {num_questions} excellent multiple choice questions based on the following content. Focus on testing understanding and application, not just memorization.

        **Content:**
        {text}

        **Question Types to Include:**
        - Conceptual understanding
        - Application scenarios  
        - Analysis and comparison
        - Process understanding
        - Real-world applications

        **For each question, use this EXACT format:**

        QUESTION 1: [Write a clear, specific question]
        A) [First option - make it plausible]
        B) [Second option - make it plausible]  
        C) [Third option - make it plausible]
        D) [Fourth option - make it plausible]
        CORRECT ANSWER: [A, B, C, or D]
        EXPLANATION: [Explain why the correct answer is right and why the others are wrong. Include additional context to help learning.]
        DIFFICULTY: [Basic/Intermediate/Advanced]
        ---

        QUESTION 2: [Next question]
        A) [Option A]
        B) [Option B]
        C) [Option C] 
        D) [Option D]
        CORRECT ANSWER: [A, B, C, or D]
        EXPLANATION: [Detailed explanation]
        DIFFICULTY: [Basic/Intermediate/Advanced]
        ---

        [Continue for all {num_questions} questions]

        **Guidelines:**
        - Test understanding and application, not just recall
        - Make all options plausible but only one clearly correct
        - Include variety in question types and difficulty
        - Provide educational explanations that teach concepts
        - Mix difficulty: 30% Basic, 50% Intermediate, 20% Advanced
        - Avoid trivial questions or trick questions
        """
        
        return self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=3000)

    def generate_quiz_structured(self, text: str, num_questions=8) -> List[Dict]:
        """Generate structured quiz data for the app interface"""
        if not text.strip():
            return []
        
        if len(text.split()) < 30:
            return []
        
        # Truncate text if too long
        max_chars = 7000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""
        Create {num_questions} multiple choice questions based on the following content. Return them as a JSON array.

        **Content:**
        {text}

        **Return format (valid JSON only):**
        [
            {{
                "question": "Clear, specific question",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Detailed explanation of the correct answer",
                "difficulty": "Basic|Intermediate|Advanced"
            }},
            ...
        ]

        **Guidelines:**
        - Test understanding and application, not just memorization
        - Make all options plausible but only one clearly correct
        - Include variety in question types and difficulty
        - Provide educational explanations
        - Mix difficulty: 30% Basic, 50% Intermediate, 20% Advanced
        - correct_answer should be the index (0-3) of the correct option
        """
        
        response = self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=3000)
        
        try:
            # Try to parse JSON response
            quiz_data = json.loads(response)
            if isinstance(quiz_data, list):
                return quiz_data
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse text format
        return self._parse_quiz_from_text(response)

    def _parse_quiz_from_text(self, text: str) -> List[Dict]:
        """Parse quiz from text format as fallback"""
        questions = []
        question_blocks = text.split("---")
        
        for block in question_blocks:
            if not block.strip():
                continue
                
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            question_data = {}
            options = []
            
            for line in lines:
                if line.startswith("QUESTION"):
                    question_data["question"] = line.split(":", 1)[1].strip()
                elif line.startswith(("A)", "B)", "C)", "D)")):
                    options.append(line[2:].strip())
                elif line.startswith("CORRECT ANSWER:"):
                    correct_letter = line.split(":", 1)[1].strip()
                    correct_index = ord(correct_letter.upper()) - ord('A')
                    question_data["correct_answer"] = correct_index
                elif line.startswith("EXPLANATION:"):
                    question_data["explanation"] = line.split(":", 1)[1].strip()
                elif line.startswith("DIFFICULTY:"):
                    question_data["difficulty"] = line.split(":", 1)[1].strip()
            
            if question_data.get("question") and len(options) == 4:
                question_data["options"] = options
                questions.append(question_data)
        
        return questions

##### NEW DISCOVERY AGENTS #####
class ResearchDiscoveryAgent:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def find_papers(self, keywords: List[str], topic: str, max_papers: int = 8) -> List[Dict]:
        """Simulate finding research papers based on keywords and topic"""
        if not keywords:
            return []
        
        try:
            # Create a prompt to generate realistic research paper suggestions
            keywords_str = ", ".join(keywords[:5])  # Limit keywords
            
            prompt = f"""
            Based on the academic topic "{topic}" and keywords: {keywords_str}, suggest {max_papers} relevant research papers.
            
            Return as JSON array with this format:
            [
                {{
                    "title": "Realistic academic paper title",
                    "authors": "Author names (2-4 authors)",
                    "year": "Recent year (2018-2024)",
                    "source": "Journal or Conference name",
                    "abstract": "Brief abstract (100-200 words)",
                    "url": "https://example.com/paper-url",
                    "relevance_score": "High|Medium|Low"
                }},
                ...
            ]
            
            Make the papers realistic and relevant to the topic. Include a mix of foundational and recent papers.
            """
            
            response = self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=2000)
            
            try:
                papers = json.loads(response)
                if isinstance(papers, list):
                    return papers[:max_papers]
            except json.JSONDecodeError:
                pass
            
            # Fallback: generate basic paper suggestions
            return self._generate_fallback_papers(topic, keywords, max_papers)
            
        except Exception as e:
            print(f"Error in research discovery: {e}")
            return self._generate_fallback_papers(topic, keywords, max_papers)

    def _generate_fallback_papers(self, topic: str, keywords: List[str], max_papers: int) -> List[Dict]:
        """Generate fallback research papers"""
        papers = []
        for i in range(min(max_papers, 5)):
            papers.append({
                "title": f"Research in {topic}: A Comprehensive Study",
                "authors": "Smith, J., Johnson, A., Brown, M.",
                "year": "2023",
                "source": "Journal of Academic Research",
                "abstract": f"This paper explores key aspects of {topic} with focus on {', '.join(keywords[:3])}. The study provides comprehensive analysis and insights into current methodologies and future directions.",
                "url": f"https://academic-search.example.com/paper-{i+1}",
                "relevance_score": "High"
            })
        return papers

class YouTubeDiscoveryAgent:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def find_videos(self, keywords: List[str], topic: str, max_videos: int = 10) -> List[Dict]:
        """Simulate finding educational YouTube videos"""
        if not keywords:
            return []
        
        try:
            keywords_str = ", ".join(keywords[:5])
            
            prompt = f"""
            Based on the educational topic "{topic}" and keywords: {keywords_str}, suggest {max_videos} relevant educational YouTube videos.
            
            Return as JSON array with this format:
            [
                {{
                    "title": "Educational video title",
                    "channel": "Educational channel name",
                    "duration": "MM:SS format",
                    "views": "View count (e.g., 1.2M views)",
                    "description": "Brief description of video content",
                    "url": "https://youtube.com/watch?v=example",
                    "educational_score": "High|Medium|Low"
                }},
                ...
            ]
            
            Focus on educational channels like Khan Academy, Crash Course, MIT OpenCourseWare, etc.
            Make the suggestions realistic and educational.
            """
            
            response = self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=2000)
            
            try:
                videos = json.loads(response)
                if isinstance(videos, list):
                    return videos[:max_videos]
            except json.JSONDecodeError:
                pass
            
            return self._generate_fallback_videos(topic, keywords, max_videos)
            
        except Exception as e:
            print(f"Error in YouTube discovery: {e}")
            return self._generate_fallback_videos(topic, keywords, max_videos)

    def _generate_fallback_videos(self, topic: str, keywords: List[str], max_videos: int) -> List[Dict]:
        """Generate fallback YouTube videos"""
        channels = ["Khan Academy", "Crash Course", "MIT OpenCourseWare", "TED-Ed", "3Blue1Brown"]
        videos = []
        
        for i in range(min(max_videos, 8)):
            videos.append({
                "title": f"Understanding {topic}: Key Concepts Explained",
                "channel": channels[i % len(channels)],
                "duration": f"{10 + i*2}:{30 + i*5:02d}",
                "views": f"{100 + i*50}K views",
                "description": f"Educational video covering {topic} with focus on {', '.join(keywords[:2])}. Perfect for students and learners.",
                "url": f"https://youtube.com/watch?v=example{i+1}",
                "educational_score": "High"
            })
        
        return videos

class WebResourceAgent:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def find_resources(self, keywords: List[str], topic: str, max_resources: int = 12) -> List[Dict]:
        """Simulate finding web learning resources"""
        if not keywords:
            return []
        
        try:
            keywords_str = ", ".join(keywords[:5])
            
            prompt = f"""
            Based on the educational topic "{topic}" and keywords: {keywords_str}, suggest {max_resources} relevant web learning resources.
            
            Return as JSON array with this format:
            [
                {{
                    "title": "Resource title",
                    "type": "Tutorial|Course|Documentation|Interactive Tool|Reference",
                    "source": "Website name",
                    "description": "Brief description of the resource",
                    "url": "https://example.com/resource",
                    "quality_score": "High|Medium|Low"
                }},
                ...
            ]
            
            Include diverse resource types: online courses, tutorials, documentation, interactive tools, reference materials.
            Focus on reputable educational websites.
            """
            
            response = self.client.chat_completion([{"role": "user", "content": prompt}], max_tokens=2000)
            
            try:
                resources = json.loads(response)
                if isinstance(resources, list):
                    return resources[:max_resources]
            except json.JSONDecodeError:
                pass
            
            return self._generate_fallback_resources(topic, keywords, max_resources)
            
        except Exception as e:
            print(f"Error in web resource discovery: {e}")
            return self._generate_fallback_resources(topic, keywords, max_resources)

    def _generate_fallback_resources(self, topic: str, keywords: List[str], max_resources: int) -> List[Dict]:
        """Generate fallback web resources"""
        resource_types = ["Tutorial", "Course", "Documentation", "Interactive Tool", "Reference"]
        sources = ["Coursera", "edX", "Wikipedia", "Stack Overflow", "Mozilla MDN", "W3Schools"]
        resources = []
        
        for i in range(min(max_resources, 10)):
            resources.append({
                "title": f"{topic} - {resource_types[i % len(resource_types)]}",
                "type": resource_types[i % len(resource_types)],
                "source": sources[i % len(sources)],
                "description": f"Comprehensive {resource_types[i % len(resource_types)].lower()} covering {topic} concepts including {', '.join(keywords[:2])}.",
                "url": f"https://{sources[i % len(sources)].lower().replace(' ', '')}.com/resource-{i+1}",
                "quality_score": "High"
            })
        
        return resources

##### DIAGNOSTIC TOOLS #####
def diagnose_pdf(file_path):
    """Enhanced PDF diagnostic tool"""
    print(f"\n🔍 Diagnosing PDF: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ File not found!")
        return
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    print(f"📁 File size: {file_size:.2f} MB")
    
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"📄 Pages: {len(pdf.pages)}")
            print(f"📋 Metadata: {pdf.metadata}")
            
            total_chars = 0
            text_pages = 0
            
            for i, page in enumerate(pdf.pages[:5], 1):  # Check first 5 pages
                print(f"\n--- Page {i} Analysis ---")
                
                # Try different extraction methods
                text_standard = page.extract_text() or ""
                text_layout = page.extract_text(layout=True) or ""
                
                chars_count = len(page.chars) if hasattr(page, 'chars') else 0
                images_count = len(page.images) if hasattr(page, 'images') else 0
                
                print(f"Standard extraction: {len(text_standard)} chars")
                print(f"Layout extraction: {len(text_layout)} chars")
                print(f"Page chars: {chars_count}")
                print(f"Images: {images_count}")
                
                if len(text_standard) > 20:
                    text_pages += 1
                    total_chars += len(text_standard)
                    print(f"✅ Text found: {text_standard[:100]}...")
                else:
                    print("❌ Little/no text extracted")
            
            print(f"\n📊 Summary:")
            print(f"Text-extractable pages: {text_pages}/{min(5, len(pdf.pages))}")
            print(f"Total characters: {total_chars}")
            print(f"Recommendation: {'Text extraction should work' if text_pages > 0 else 'May need OCR'}")
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

def test_ocr_setup():
    """Test OCR capabilities"""
    print("\n🔍 Testing OCR Setup...")
    
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        # Create test image
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
            draw.text((10, 10), "OCR Test: Hello World! 123", fill='black', font=font)
        except:
            draw.text((10, 10), "OCR Test: Hello World! 123", fill='black')
        
        # Test OCR
        text = pytesseract.image_to_string(img)
        print(f"✅ OCR output: '{text.strip()}'")
        
        if "Hello World" in text or "OCR Test" in text:
            print("✅ OCR is working correctly!")
        else:
            print("⚠️ OCR may have issues with text recognition")
            
    except Exception as e:
        print(f"❌ OCR setup failed: {e}")
        print("💡 Try installing Tesseract: https://github.com/tesseract-ocr/tesseract")

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI Connection...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in environment variables")
        print("💡 Set OPENAI_API_KEY in your .env file")
        return
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    client = OpenAIClient()
    test_message = [{"role": "user", "content": "Say 'Hello World' to test the connection."}]
    
    response = client.chat_completion(test_message, max_tokens=50)
    
    if "❌" in response:
        print(f"❌ Connection failed: {response}")
    else:
        print(f"✅ Connection successful: {response}")

##### MAIN EXECUTION LOGIC #####
def run_study_assistant(pdf_path):
    """Main function to process PDF and generate study materials"""
    print(f"\n🎓 Processing: {pdf_path}")
    
    # Initialize components
    client = OpenAIClient()
    processor = EnhancedPDFProcessor()
    summary_agent = SummaryAgent(client)
    flashcard_agent = FlashcardAgent(client)
    quiz_agent = QuizAgent(client)

    # Extract text
    print("\n📄 Extracting text from PDF...")
    result = processor.extract_text_with_ocr(pdf_path)

    if result["status"] == "error":
        print(f"❌ PDF Processing Failed: {result['message']}")
        return

    print(f"\n{result['message']}")
    
    if result["word_count"] < 20:
        print("⚠️ Very little content extracted. Results may be limited.")

    # Generate study materials
    print("\n🧠 Generating study materials...")
    
    print("📘 Creating summary...")
    summary = summary_agent.generate_summary(result["text"])
    
    print("🃏 Creating flashcards...")
    flashcards = flashcard_agent.generate_flashcards(result["text"])
    
    print("📝 Creating quiz...")
    quiz = quiz_agent.generate_quiz(result["text"])

    # Display results
    print("\n" + "="*80)
    print("📘 SUMMARY")
    print("="*80)
    print(summary)
    
    print("\n" + "="*80)
    print("🃏 FLASHCARDS")
    print("="*80)
    print(flashcards)
    
    print("\n" + "="*80)
    print("📝 QUIZ")
    print("="*80)
    print(quiz)

if __name__ == "__main__":
    print("\n🎓 AI Study Assistant CLI - Enhanced Version")
    print("="*50)
    print("1. Run Study Assistant")
    print("2. Diagnose PDF")
    print("3. Test OCR Setup")
    print("4. Test OpenAI Connection")
    print("5. Exit")
    
    choice = input("\nChoose an option (1-5): ").strip()

    if choice == "1":
        pdf_path = input("Enter PDF file path: ").strip().strip('"')
        if os.path.exists(pdf_path):
            run_study_assistant(pdf_path)
        else:
            print(f"❌ File not found: {pdf_path}")
    
    elif choice == "2":
        pdf_path = input("Enter PDF file path: ").strip().strip('"')
        diagnose_pdf(pdf_path)
    
    elif choice == "3":
        test_ocr_setup()
    
    elif choice == "4":
        test_openai_connection()
    
    elif choice == "5":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid option. Please choose 1-5.")
