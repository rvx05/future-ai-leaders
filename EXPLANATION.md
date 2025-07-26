# Technical Explanation

## 1. Agent Workflow

The Educational Buddy system processes user input through a sophisticated multi-agent workflow:

1. **Receive user input** - User submits a message through the React frontend chat interface
2. **Orchestrator Analysis** - The main orchestrator agent analyzes the request and determines which specialized agents to coordinate
3. **Database-First Approach** - Knowledge Base Agent checks/creates course data before any processing
4. **Agent Coordination** - Orchestrator delegates to appropriate specialized agents:
   - Knowledge Base Agent for course/user data management
   - Course Planning Agent for study plan generation and content analysis
   - Research Agent for external information gathering
5. **File Processing** (if applicable) - Extract and analyze uploaded documents
6. **Response Synthesis** - Orchestrator combines agent outputs into coherent response
7. **Database Updates** - Store results and update user progress
8. **Return final output** - Deliver comprehensive response to user

## 2. Key Modules

### **Orchestrator Agent** (`src/agents/orchestrator_agent.py`)
- **Purpose**: Main coordination hub using Google's Agent Development Kit (ADK)
- **Responsibilities**: 
  - Analyzes user intent and routes requests
  - Coordinates between specialized agents
  - Manages file processing workflow
  - Enforces database-first workflow patterns
- **Key Features**: Agent-to-Agent communication, workflow state management, file ingestion

### **Knowledge Base Agent** (`src/agents/knowledge_base_agent.py`)
- **Purpose**: Centralized data management and user context
- **Responsibilities**:
  - Course creation and management
  - User profile and progress tracking
  - Material storage and retrieval
  - Database operations (CRUD)
- **Key Features**: Automatic user context, course verification, progress tracking

### **Course Planning Agent** (`src/agents/course_planning_agent.py`)
- **Purpose**: Educational content analysis and study plan generation
- **Responsibilities**:
  - Course content analysis and topic extraction
  - Personalized study plan creation with detailed session guides
  - Content organization and scheduling
  - Progress adaptation and plan updates
- **Key Features**: Detailed session planning, calendar integration, adaptive scheduling

### **Research Agent** (`src/agents/research_agent.py`)
- **Purpose**: External information gathering and real-world context
- **Responsibilities**:
  - Web search for current information
  - Real-world examples and applications
  - Academic source verification
  - Context enrichment for educational content
- **Key Features**: Google Search integration, source citation, content synthesis

### **Database Layer** (`src/models.py`)
- **Purpose**: SQLite-based data persistence
- **Models**: User, Course, StudyPlan, StudySession, CourseMateria
- **Features**: Comprehensive progress tracking, session management, material organization

## 3. Tool Integration

### **File Processing Tools** (`src/tools/file_ingestion_tools.py`)
- **PDF Processing**: `extract_text_from_pdf()` - PyPDF2-based text extraction
- **Word Documents**: `extract_text_from_docx()` - python-docx integration
- **Text Files**: `extract_text_from_txt()` - UTF-8 text processing
- **Content Analysis**: `analyze_content_structure()` - Document organization analysis
- **Usage**: Automatic file processing when users upload course materials

### **Google ADK Integration**
- **Agent Framework**: Google's Agent Development Kit for agent coordination
- **Session Management**: Persistent conversation context across interactions
- **Function Tools**: Structured tool calling for agent capabilities
- **Agent Tools**: Inter-agent communication and delegation

### **Database Tools**
- **SQLite**: Lightweight, file-based database for development
- **ORM Layer**: Custom database abstraction for course and user management
- **Progress Tracking**: Comprehensive analytics and progress monitoring
- **Session Persistence**: User authentication and session management

## 4. Observability & Testing

### **Logging System**
- **Agent Interactions**: Detailed logging of agent-to-agent communication
- **Database Operations**: Transaction logging and error tracking
- **File Processing**: Upload and processing status tracking
- **User Actions**: Authentication and interaction logging
- **Error Handling**: Comprehensive exception tracking and recovery

### **Development Tools**
- **Health Check Endpoint**: `/api/health` - System status and component availability
- **Debug Mode**: Detailed console logging for development
- **Session Management**: User session tracking and debugging
- **API Testing**: RESTful endpoints for all major functionality

### **Testing Approach**
- **Manual Testing**: Interactive chat interface for agent testing
- **API Testing**: Direct endpoint testing for backend functionality
- **File Upload Testing**: Document processing verification
- **Theme Testing**: UI component functionality verification

## 5. Known Limitations

### **Performance Bottlenecks**
- **Large File Processing**: PDF/DOCX processing can be slow for large documents
- **Agent Coordination**: Multiple agent calls can increase response time
- **Database Queries**: Complex progress calculations may impact performance
- **Session Management**: In-memory session storage not suitable for production scale

### **Scalability Concerns**
- **SQLite Database**: File-based database limits concurrent users
- **In-Memory Storage**: Recent uploads stored in memory, not persistent
- **Session Service**: ADK InMemorySessionService not production-ready
- **File Storage**: No cloud storage integration for uploaded files

### **Edge Cases**
- **Ambiguous User Input**: Complex requests may confuse agent routing
- **File Format Support**: Limited to PDF, DOCX, TXT formats
- **Theme Persistence**: Browser-dependent localStorage for theme preferences
- **Error Recovery**: Limited graceful degradation for agent failures

### **Security Considerations**
- **File Upload Security**: Basic file type validation only
- **Authentication**: Simple password hashing, no advanced security features
- **API Security**: No rate limiting or advanced protection
- **Data Privacy**: No encryption for stored course materials

### **Production Readiness**
- **Environment Variables**: API keys stored in .env files
- **Database Migration**: No automated schema migration system
- **Monitoring**: No production monitoring or alerting
- **Deployment**: Development-focused configuration only

## 6. Architecture Highlights

### **Multi-Agent Coordination**
The system uses Google's ADK to coordinate multiple specialized agents, each with distinct responsibilities. This allows for modular, scalable agent development while maintaining coherent user experiences.

### **Database-First Workflow**
All course-related operations must go through the Knowledge Base Agent first, ensuring data consistency and preventing duplicate course creation.

### **Adaptive Study Planning**
The Course Planning Agent generates detailed, personalized study plans that adapt to user progress and content availability, with comprehensive session guides and calendar integration.

### **File Processing Pipeline**
Automated document processing extracts and analyzes uploaded course materials, making them immediately available for study plan generation and agent context.

### **Progressive Web App**
React frontend with dark/light theme support, responsive design, and modern UI components for optimal user experience across devices.
