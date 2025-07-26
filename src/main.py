"""
Agentic AI App - Main Flask Application
Hackathon Template for Google Gemini Integration with Google ADK

This integrates the core agentic architecture:
- Orchestrator: Main coordination agent using Google ADK
- Knowledge Agent: Handles student context and course materials
- Research Agent: Conducts web searches and research
"""

import os
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from flask_login import logout_user, current_user
from dotenv import load_dotenv
import json
import asyncio
from datetime import datetime

# Simple in-memory storage for recently uploaded file content
# In production, this should be replaced with proper database storage or Redis
recent_uploads = {}

# Session management for persistent agent memory
user_sessions = {}

# Import Google ADK components
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai

# Import new Google ADK agents
from agents.orchestrator_agent import orchestrator_agent

# Import authentication and models
from auth import init_auth, register_user, authenticate_user, get_current_user_data, update_user_profile, get_user_progress, add_study_session, api_login_required
from models import db

# Load environment variables
load_dotenv()

# Use Flask static_folder to serve built React assets from src/static
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'), static_url_path='/static')
CORS(app, supports_credentials=True)

# Initialize authentication
init_auth(app)

# Initialize agentic components
google_api_key = os.getenv('GOOGLE_API_KEY')
firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')

if not google_api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables")

# Initialize Google ADK Runner and Session Service
adk_runner = None
session_service = None

if google_api_key:
    try:
        # Create session service for managing conversations
        session_service = InMemorySessionService()
        
        # Create ADK Runner with the orchestrator agent
        adk_runner = Runner(
            agent=orchestrator_agent,
            app_name="Educational Buddy",
            session_service=session_service
        )
        print("✅ ADK Runner created successfully with orchestrator agent")
    except Exception as e:
        print(f"⚠️ ADK Runner creation failed: {e}")
        adk_runner = None
        session_service = None
else:
    print("⚠️ ADK Runner not available - missing API key")

async def run_agent_query(user_input: str, user_id: str = "anonymous") -> str:
    """Helper function to run agent queries using ADK Runner with persistent sessions"""
    if not adk_runner or not session_service:
        raise Exception("ADK Runner or SessionService not available")
    
    user_content = genai.types.Content(
        role='user', 
        parts=[genai.types.Part(text=user_input)]
    )
    
    # Use persistent session for this user
    app_name = "Educational Buddy"
    
    try:
        # For now, create a new session each time but store context differently
        # The ADK InMemorySessionService doesn't support session retrieval by ID
        # We'll implement our own context persistence through the enhanced input
        print(f"Creating session for user {user_id}")
        session = await session_service.create_session(
            app_name=app_name,
            user_id=str(user_id),
            state={}  # Initialize with empty state
        )
        
        if not session or not hasattr(session, 'id'):
            raise Exception("Session creation failed - invalid session object returned")
        
        print(f"✅ Session ready with ID: {session.id}")
        
    except Exception as session_error:
        print(f"❌ Session creation failed: {session_error}")
        raise Exception(f"Failed to create session: {session_error}")
    
    # Now run the agent with the valid session
    final_response = None
    event_count = 0
    try:
        print(f"🤖 Running ADK agent for user {user_id}, session {session.id}")
        async for event in adk_runner.run_async(
            user_id=str(user_id), 
            session_id=session.id,
            new_message=user_content
        ):
            event_count += 1
            print(f"📤 Event {event_count}: {type(event).__name__}, is_final: {event.is_final_response()}")
            
            if event.is_final_response():
                print(f"📋 Final response event: {event}")
                # Add safety checks for response content
                if event.content and hasattr(event.content, 'parts') and event.content.parts:
                    final_response = event.content.parts[0].text
                    print(f"✅ Extracted response text: {final_response[:100]}...")
                    break
                else:
                    print(f"⚠️ Received final response event with empty content")
                    print(f"   Event content: {event.content}")
                    print(f"   Event dir: {dir(event)}")
                    # Try to extract any available text from the event
                    if hasattr(event, 'text'):
                        final_response = event.text
                        print(f"✅ Using event.text: {final_response[:100]}...")
                        break
                    elif hasattr(event, 'content') and event.content:
                        final_response = str(event.content)
                        print(f"✅ Using str(event.content): {final_response[:100]}...")
                        break
                    else:
                        print(f"❌ No usable content found in event")
        
        print(f"📊 Processed {event_count} events total")
    except Exception as runner_error:
        print(f"❌ ADK Runner execution failed: {runner_error}")
        raise Exception(f"Agent execution failed: {runner_error}")
    
    if not final_response:
        raise Exception("No response received from agent")
    
    return final_response

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Agentic AI Backend is running!',
        'gemini_configured': bool(google_api_key),
        'user_authenticated': current_user.is_authenticated if current_user else False,
        'components': {
            'adk_runner': adk_runner is not None,
            'session_service': session_service is not None
        },
        'agents': {
            'orchestrator': 'ADK Runner' if adk_runner else None,
            'google_adk': True if adk_runner else False,
            'agent_name': orchestrator_agent.name if adk_runner else None
        } if adk_runner else None
    })

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not all([email, username, password]):
            return jsonify({'error': 'Email, username, and password are required'}), 400
        
        success, message = register_user(email, username, password)
        
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        success, message, user_data = authenticate_user(email, password)
        
        if success:
            return jsonify({
                'message': message,
                'user': user_data
            }), 200
        else:
            return jsonify({'error': message}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@api_login_required
def auth_logout():
    """User logout endpoint"""
    try:
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user info"""
    try:
        if current_user.is_authenticated:
            user_data = get_current_user_data()
            return jsonify({
                'authenticated': True,
                'user': user_data
            }), 200
        else:
            return jsonify({
                'authenticated': False,
                'user': None
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@api_login_required
def get_profile():
    """Get current user profile"""
    try:
        profile_data = get_current_user_data()
        return jsonify(profile_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['PUT'])
@api_login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        success, message = update_user_profile(data)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Main chat endpoint using Google ADK Orchestrator
@app.route('/api/chat', methods=['POST'])
@app.route('/api/chat/orchestrator', methods=['POST'])
@api_login_required
def chat():
    """
    Enhanced chat endpoint using Google ADK orchestrator
    
    The process flow:
    1. Receive user input
    2. Use Google ADK Runner to handle the request
    3. Return the orchestrated response
    """
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        user_id = data.get('user_id', current_user.id if current_user.is_authenticated else 'anonymous')
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        if not adk_runner:
            return jsonify({'error': 'ADK Runner not configured. Please check API keys.'}), 500
        
        print(f"🎯 Processing user input: {user_input[:100]}...")
        print(f"🤖 Using ADK Runner with orchestrator agent...")
        
        # Check if user mentions uploaded files and include the content
        # Also check for study plan requests and course-related queries
        enhanced_input = user_input
        user_key = str(current_user.id) if current_user.is_authenticated else 'anonymous'
        
        # Always check for uploaded files and include them in context
        if user_key in recent_uploads:
            upload_data = recent_uploads[user_key]
            file_contents = []
            for file_info in upload_data['content']:
                file_contents.append(f"""
File: {file_info['filename']}
Content: {file_info['content'][:4000]}{'...' if len(file_info['content']) > 4000 else ''}
""")
            
            if file_contents:
                # Include file content for study plan requests or course-related queries
                if any(keyword in user_input.lower() for keyword in ['study plan', 'create', 'course', 'database', 'comp 353', 'syllabus', 'outline']):
                    enhanced_input = f"""
{user_input}

CONTEXT - PREVIOUSLY UPLOADED FILE CONTENT:
{''.join(file_contents)}

Please use this uploaded content to fulfill the user's request. The file was already processed and contains the course information.
"""
                    print(f"📄 Including file content context for course-related request")
                # Also include for file-related queries
                elif "Files uploaded:" in user_input or "file" in user_input.lower():
                    enhanced_input = f"""
{user_input}

UPLOADED FILE CONTENT:
{''.join(file_contents)}

Please process this content for the user's request.
"""
                    print(f"📄 Including content from {len(file_contents)} uploaded file(s)")
        
        try:
            # Use ADK Runner to process the message
            async def run_agent():
                return await run_agent_query(enhanced_input, str(user_id))
            
            # Run the async agent function
            response_text = asyncio.run(run_agent())
            
            if not response_text:
                raise Exception("No response received from agent")
                
            print("✅ ADK Runner succeeded")
                
        except Exception as adk_error:
            print(f"⚠️ ADK Runner failed: {adk_error}")
            return jsonify({
                'error': f'Agent execution failed: {str(adk_error)}',
                'fallback_response': f"I understand you're asking about: {user_input}. I'm here to help with your educational needs!",
                'debug_info': {
                    'error_type': type(adk_error).__name__,
                    'adk_runner_available': adk_runner is not None
                }
            }), 500
        
        return jsonify({
            'response': response_text,
            'status': 'success',
            'model_used': 'gemini-2.0-flash',
            'processing_method': 'google_adk_runner',
            'intent_analysis': {
                'id': f'intent_{datetime.now().timestamp()}',
                'description': f'Process educational query: {user_input[:50]}...',
                'tool': 'orchestrator_agent'
            },
            'agent_responses': {
                'orchestrator': response_text[:200] + '...' if len(response_text) > 200 else response_text
            }
        })
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Learning Progress endpoints
@app.route('/api/progress', methods=['GET'])
@api_login_required
def get_progress():
    """Get comprehensive user learning progress"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get overall progress
        progress_data = db.get_user_progress(user_id)
        
        # Get course-specific progress
        courses = db.get_user_courses(user_id)
        course_progress = []
        for course in courses:
            course_prog = db.get_course_progress(course.id)
            course_prog['course_title'] = course.title
            course_progress.append(course_prog)
        
        progress_data['course_progress'] = course_progress
        
        return jsonify(progress_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory', methods=['GET'])
@api_login_required
def get_chat_memory():
    """Get user's chat history/memory"""
    try:
        user_key = str(current_user.id) if current_user.is_authenticated else 'anonymous'
        
        # Check for uploaded files (this is our main persistence mechanism)
        file_info = {}
        if user_key in recent_uploads:
            upload_data = recent_uploads[user_key]
            file_info['has_uploaded_files'] = True
            file_info['file_count'] = len(upload_data['content'])
            file_info['files'] = [f['filename'] for f in upload_data['content']]
            file_info['upload_timestamp'] = upload_data['timestamp']
        else:
            file_info['has_uploaded_files'] = False
        
        return jsonify({
            'messages': [],
            'file_info': file_info,
            'total_messages': 0,
            'user_key': user_key
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/clear', methods=['POST'])
@api_login_required  
def clear_session():
    """Clear user's uploaded files for testing"""
    try:
        user_key = str(current_user.id) if current_user.is_authenticated else 'anonymous'
            
        # Clear uploaded files  
        if user_key in recent_uploads:
            del recent_uploads[user_key]
            
        return jsonify({
            'message': 'Uploaded files cleared successfully',
            'user_key': user_key
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flashcards', methods=['GET'])
@api_login_required
def get_flashcards():
    """Get user's flashcards"""
    try:
        # For now, return empty flashcards - can be enhanced later
        return jsonify({
            'flashcards': [],
            'total_count': 0,
            'categories': []
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/session', methods=['POST'])
@api_login_required
def record_study_session():
    """Record a study session"""
    try:
        data = request.get_json()
        duration = data.get('duration', 0)
        topics = data.get('topics', [])
        
        success, message = add_study_session(duration, topics)
        
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Course upload endpoint
@app.route('/api/upload/course', methods=['POST'])
@api_login_required
def upload_course():
    """Upload course materials"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Here you would process the file upload
        # For now, just return success
        return jsonify({
            'message': 'Course uploaded successfully',
            'filename': file.filename
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Chat document upload endpoint
@app.route('/api/upload/chat', methods=['POST'])
@api_login_required
def upload_chat_documents():
    """Upload documents for chat analysis"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Import file processing tools
        from tools.file_ingestion_tools import process_uploaded_file
        import tempfile
        
        uploaded_files = []
        processed_content = []
        
        for file in files:
            if file.filename and file.filename != '':
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                    file.save(temp_file.name)
                    
                    # Process the file
                    result = process_uploaded_file(temp_file.name, file.filename)
                    
                    if result.get("status") == "success":
                        uploaded_files.append({
                            'filename': file.filename,
                            'size': len(file.read()),
                            'type': file.content_type,
                            'word_count': result.get('word_count', 0),
                            'content_type': result.get('content_type', 'unknown')
                        })
                        
                        # Store the extracted content for agent use
                        processed_content.append({
                            'filename': file.filename,
                            'content': result.get('content', ''),
                            'metadata': result.get('metadata', {}),
                            'processed_at': result.get('processed_at')
                        })
                    else:
                        uploaded_files.append({
                            'filename': file.filename,
                            'error': result.get('error', 'Processing failed'),
                            'type': file.content_type
                        })
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                    
                    file.seek(0)  # Reset file pointer
        
        # Store processed content in session or database for agent access
        # For now, we'll store it in a simple way - in production, use proper storage
        session_data = {
            'uploaded_files': processed_content,
            'upload_timestamp': datetime.now().isoformat()
        }
        
        # Store in our in-memory cache for agent access
        user_key = str(current_user.id) if current_user.is_authenticated else 'anonymous'
        recent_uploads[user_key] = {
            'content': processed_content,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'message': f'Successfully processed {len([f for f in uploaded_files if "error" not in f])} file(s)',
            'files': uploaded_files,
            'processed_content_available': len(processed_content) > 0,
            'session_data': session_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Course Management Endpoints
@app.route('/api/courses', methods=['POST'])
@api_login_required  
def create_course():
    """Create a new course with agent assistance"""
    try:
        data = request.get_json()
        course_title = data.get('title', '').strip()
        course_description = data.get('description', '').strip()
        course_outline = data.get('outline', '').strip()
        
        if not all([course_title, course_outline]):
            return jsonify({'error': 'Course title and outline are required'}), 400
        
        if not adk_runner:
            return jsonify({'error': 'ADK Runner not configured'}), 500
        
        # Use the agent to help create and analyze the course
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        course_prompt = f"""
        Please help me create a new course with the following details:
        Title: {course_title}
        Description: {course_description}
        Course Outline: {course_outline}
        
        I need you to:
        1. Analyze the course content and structure
        2. Create a course in the system
        3. Ask me any questions needed for creating a study plan
        4. Guide me through the next steps
        
        My user ID is: {user_id}
        """
        
        try:
            response_text = asyncio.run(run_agent_query(course_prompt, str(user_id)))
            
            return jsonify({
                'response': response_text,
                'message': 'Course creation initiated through agent',
                'next_steps': [
                    'The agent will guide you through course setup',
                    'Provide any additional information requested',
                    'Upload your first course materials when ready'
                ]
            }), 201
                
        except Exception as e:
            return jsonify({
                'error': f'Course creation failed: {str(e)}',
                'fallback': 'Please try creating the course again or contact support'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses', methods=['GET'])
@api_login_required
def get_courses():
    """Get all courses for the current user"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        courses = db.get_user_courses(user_id)
        courses_data = [course.to_dict() for course in courses]
        
        # Get progress for each course
        for course_data in courses_data:
            progress = db.get_course_progress(course_data['id'])
            course_data['progress'] = progress
        
        return jsonify({
            'courses': courses_data,
            'total_count': len(courses_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_id>', methods=['GET'])
@api_login_required
def get_course_details(course_id):
    """Get detailed course information"""
    try:
        course = db.get_course(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Verify user owns this course
        if course.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get course materials
        materials = db.get_course_materials(course_id)
        
        # Get study plan if exists
        study_plan = db.get_course_study_plan(course_id)
        study_sessions = []
        if study_plan:
            study_sessions = [session.to_dict() for session in db.get_study_sessions(study_plan.id)]
        
        # Get progress
        progress = db.get_course_progress(course_id)
        
        course_data = course.to_dict()
        course_data.update({
            'materials': materials,
            'study_plan': study_plan.to_dict() if study_plan else None,
            'study_sessions': study_sessions,
            'progress': progress
        })
        
        return jsonify(course_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_id>/materials', methods=['POST'])
@api_login_required
def upload_course_material(course_id):
    """Upload course material for a specific course"""
    try:
        # Verify course exists and user owns it
        course = db.get_course(course_id)
        if not course or course.user_id != current_user.id:
            return jsonify({'error': 'Course not found or access denied'}), 403
        
        data = request.get_json()
        material_title = data.get('title', '').strip()
        content_text = data.get('content', '').strip()
        week_number = data.get('week_number')
        content_type = data.get('content_type', 'lecture_notes')
        
        if not all([material_title, content_text]):
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Use agent to analyze and process the content
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        upload_prompt = f"""
        I'm uploading new course material for my course:
        Course ID: {course_id}
        Material Title: {material_title}
        Week Number: {week_number}
        Content Type: {content_type}
        Content: {content_text[:500]}...
        
        Please:
        1. Analyze this content and add it to my course
        2. Update my study plan if needed
        3. Let me know what study sessions this affects
        4. Provide any recommendations for studying this material
        """
        
        try:
            response_text = asyncio.run(run_agent_query(upload_prompt, str(user_id)))
            
            # Also add to database directly
            material_id = db.add_course_material(
                course_id, user_id, material_title, content_type,
                content_text, None, week_number, []
            )
            
            return jsonify({
                'material_id': material_id,
                'agent_response': response_text,
                'message': 'Course material uploaded and analyzed successfully'
            }), 201
                
        except Exception as e:
            return jsonify({
                'error': f'Material upload failed: {str(e)}',
                'fallback': 'Material uploaded but agent analysis failed'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/study-plans/<plan_id>/sessions/<session_id>/complete', methods=['POST'])
@api_login_required
def complete_study_session(plan_id, session_id):
    """Complete a study session with validation"""
    try:
        data = request.get_json()
        validation_score = data.get('validation_score')
        notes = data.get('notes', '')
        
        # Use agent to handle session completion
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        completion_prompt = f"""
        I just completed a study session:
        Session ID: {session_id}
        Study Plan ID: {plan_id}
        Validation Score: {validation_score}
        Notes: {notes}
        
        Please:
        1. Mark this session as completed
        2. Update my progress
        3. Give me feedback on my performance
        4. Suggest what to focus on in the next session
        5. Generate validation questions to test my understanding
        """
        
        try:
            response_text = asyncio.run(run_agent_query(completion_prompt, str(user_id)))
            
            # Update in database
            success = db.complete_study_session(session_id, validation_score, notes)
            
            if success:
                return jsonify({
                    'message': 'Study session completed successfully',
                    'agent_feedback': response_text,
                    'status': 'completed'
                }), 200
            else:
                return jsonify({'error': 'Failed to update session status'}), 500
                
        except Exception as e:
            return jsonify({
                'error': f'Session completion failed: {str(e)}',
                'fallback': 'Session marked as completed but agent feedback failed'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Flashcard generation endpoint
@app.route('/api/flashcards/generate', methods=['POST'])
@api_login_required
def generate_flashcards():
    """Generate flashcards from course content"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        if not adk_runner:
            return jsonify({'error': 'ADK Runner not configured'}), 500
        
        # Use ADK Runner to generate flashcards
        flashcards_prompt = f"Generate flashcards from this content: {content}"
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        try:
            response_text = asyncio.run(run_agent_query(flashcards_prompt, str(user_id)))
                
        except Exception as e:
            return jsonify({
                'error': f'Flashcard generation failed: {str(e)}',
                'fallback': f"Generated flashcards for: {content[:50]}... (Fallback mode)"
            }), 500
        
        return jsonify({
            'flashcards': response_text,
            'message': 'Flashcards generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Exam generation endpoint  
@app.route('/api/exam/generate', methods=['POST'])
@api_login_required
def generate_exam():
    """Generate practice exam questions"""
    try:
        data = request.get_json()
        topics = data.get('topics', [])
        difficulty = data.get('difficulty', 'medium')
        
        if not topics:
            return jsonify({'error': 'Topics are required'}), 400
        
        if not adk_runner:
            return jsonify({'error': 'ADK Runner not configured'}), 500
        
        # Use ADK Runner to generate exam
        exam_prompt = f"Generate practice exam questions for topics: {', '.join(topics)} at {difficulty} difficulty"
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        try:
            response_text = asyncio.run(run_agent_query(exam_prompt, str(user_id)))
                
        except Exception as e:
            return jsonify({
                'error': f'Exam generation failed: {str(e)}',
                'fallback': f"Generated practice exam for topics: {', '.join(topics)} (Fallback mode)"
            }), 500
        
        return jsonify({
            'exam': response_text,
            'message': 'Exam generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Study plan generation endpoint
@app.route('/api/study-plan/generate', methods=['POST'])
@api_login_required
def generate_study_plan():
    """Generate personalized study plan"""
    try:
        data = request.get_json()
        subjects = data.get('subjects', [])
        timeframe = data.get('timeframe', '1 week')
        
        if not subjects:
            return jsonify({'error': 'Subjects are required'}), 400
        
        if not adk_runner:
            return jsonify({'error': 'ADK Runner not configured'}), 500
        
        # Use ADK Runner to generate study plan
        plan_prompt = f"Create a study plan for subjects: {', '.join(subjects)} over {timeframe}"
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        try:
            response_text = asyncio.run(run_agent_query(plan_prompt, str(user_id)))
                
        except Exception as e:
            return jsonify({
                'error': f'Study plan generation failed: {str(e)}',
                'fallback': f"Generated study plan for subjects: {', '.join(subjects)} over {timeframe} (Fallback mode)"
            }), 500
        
        return jsonify({
            'study_plan': response_text,
            'message': 'Study plan generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve React frontend
@app.route('/')
def serve_react_app():
    """Serve the React frontend"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except FileNotFoundError:
        return jsonify({
            'message': 'Frontend not built yet. Please run the frontend separately.',
            'backend_status': 'running',
            'api_endpoints': [
                '/api/health',
                '/api/auth/register',
                '/api/auth/login',
                '/api/chat'
            ]
        }), 200

@app.route('/<path:path>')
def serve_react_routes(path):
    """Serve React routes"""
    try:
        if path.startswith('api/'):
            abort(404)
        return send_from_directory(app.static_folder, 'index.html')
    except FileNotFoundError:
        return jsonify({'error': 'Frontend not found'}), 404

if __name__ == '__main__':
    # Print startup information
    print("🚀 Starting Agentic AI App...")
    print(f"🔑 Google API Key: {'✅ Configured' if google_api_key else '❌ Missing'}")
    print(f"🌊 Firecrawl API Key: {'✅ Configured' if firecrawl_api_key else '❌ Missing'}")
    print(f"🤖 Google ADK Runner: {'✅ Initialized' if adk_runner else '❌ Not Available'}")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Server starting on http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
