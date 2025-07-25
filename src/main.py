"""
Agentic AI App - Main Flask Application
Hackathon Template for Google Gemini Integration

This integrates the core agentic architecture:
- Planner: Breaks down user goals into sub-tasks
- Executor: Calls tools and LLMs 
- Memory: Stores and retrieves context
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Import our agentic modules
from planner import AgentPlanner
from executor import AgentExecutor
from memory import AgentMemory

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize agentic components
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    print("Warning: GEMINI_API_KEY not found in environment variables")

planner = AgentPlanner(gemini_api_key) if gemini_api_key else None
executor = AgentExecutor(gemini_api_key) if gemini_api_key else None
memory = AgentMemory()

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.exists(os.path.join(static_dir, 'index.html')):
        return send_from_directory(static_dir, 'index.html')
    else:
        return jsonify({
            'message': 'Agentic AI Backend is running!',
            'status': 'Frontend not built yet',
            'endpoints': ['/api/health', '/api/chat', '/api/agent']
        })

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Agentic AI Backend is running!',
        'gemini_configured': bool(gemini_api_key),
        'components': {
            'planner': planner is not None,
            'executor': executor is not None,
            'memory': memory is not None
        },
        'memory_summary': memory.get_memory_summary() if memory else None
    })

@app.route('/api/agent', methods=['POST'])
def agentic_workflow():
    """
    Main agentic workflow endpoint.
    
    This follows the core agent workflow:
    1. Receive user input
    2. Retrieve relevant memory
    3. Plan sub-tasks
    4. Execute tasks (call tools/APIs)
    5. Generate final response
    """
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        if not all([planner, executor, memory]):
            return jsonify({'error': 'Agentic components not properly initialized'}), 500
        
        # Step 1: Receive user input ✓
        
        # Step 2: Retrieve relevant memory
        context = memory.get_relevant_context(user_input)
        
        # Step 3: Plan sub-tasks
        plan = planner.create_plan(user_input, context)
        optimized_plan = planner.optimize_plan(plan)
        
        # Step 4: Execute tasks (call tools/APIs including Gemini)
        execution_results = executor.execute_plan(optimized_plan, context)
        
        # Step 5: Generate final response
        final_response = executor.synthesize_results(execution_results, user_input)
        
        # Store the complete interaction in memory
        memory.store_interaction(
            user_input=user_input,
            agent_response=final_response,
            plan=optimized_plan,
            execution_results=execution_results
        )
        
        return jsonify({
            'response': final_response,
            'plan': optimized_plan,
            'execution_results': execution_results,
            'memory_context_used': bool(context.get('recent_interactions')),
            'timestamp': None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def simple_chat():
    """Simple chat endpoint for direct Gemini interaction (fallback)"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not executor:
            return jsonify({'error': 'Gemini not configured'}), 500
        
        # Simple task for direct Gemini call
        simple_task = {
            'id': 'direct_chat',
            'description': message,
            'tool': 'gemini',
            'priority': 1,
            'dependencies': []
        }
        
        result = executor.execute_task(simple_task)
        
        return jsonify({
            'response': result.get('result', 'No response generated'),
            'timestamp': None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory_info():
    """Get information about the agent's memory"""
    if not memory:
        return jsonify({'error': 'Memory not initialized'}), 500
    
    return jsonify(memory.get_memory_summary())

@app.route('/api/memory/clear', methods=['POST'])
def clear_session_memory():
    """Clear the current session memory"""
    if not memory:
        return jsonify({'error': 'Memory not initialized'}), 500
    
    memory.clear_session_memory()
    return jsonify({'message': 'Session memory cleared'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Agentic AI App...")
    print(f"🔧 Gemini API configured: {bool(gemini_api_key)}")
    print(f"🧠 Components initialized: Planner={planner is not None}, Executor={executor is not None}, Memory={memory is not None}")
    print(f"🌐 Server running on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
