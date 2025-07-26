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

# Import Google ADK components
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai

# Import new Google ADK agents
from agents.orchestrator_agent import orchestrator_agent

# Import authentication
from auth import init_auth, register_user, authenticate_user, get_current_user_data, update_user_profile, get_user_progress, add_study_session, api_login_required

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
    """Helper function to run agent queries using ADK Runner"""
    if not adk_runner or not session_service:
        raise Exception("ADK Runner or SessionService not available")
    
    user_content = genai.types.Content(
        role='user', 
        parts=[genai.types.Part(text=user_input)]
    )
    
    # Create session for this user - ADK will handle session ID generation
    app_name = "Educational Buddy"
    
    try:
        # Create a new session with proper ADK parameters
        # Note: InMemorySessionService auto-generates session ID
        print(f"Creating new session for user {user_id}")
        session = await session_service.create_session(
            app_name=app_name,
            user_id=str(user_id),
            state={}  # Initialize with empty state
        )
        
        if not session or not hasattr(session, 'id'):
            raise Exception("Session creation failed - invalid session object returned")
        
        print(f"✅ Session created successfully with ID: {session.id}")
        
    except Exception as session_error:
        print(f"❌ Session creation failed: {session_error}")
        raise Exception(f"Failed to create session: {session_error}")
    
    # Now run the agent with the valid session
    final_response = None
    try:
        async for event in adk_runner.run_async(
            user_id=str(user_id), 
            session_id=session.id,
            new_message=user_content
        ):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break
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
        
        try:
            # Use ADK Runner to process the message
            async def run_agent():
                return await run_agent_query(user_input, str(user_id))
            
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
    """Get user learning progress"""
    try:
        progress_data = get_user_progress()
        return jsonify(progress_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory', methods=['GET'])
@api_login_required
def get_chat_memory():
    """Get user's chat history/memory"""
    try:
        # For now, return empty memory - can be enhanced later
        return jsonify({
            'messages': [],
            'session_id': f"user_{current_user.id}_session",
            'total_messages': 0
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
