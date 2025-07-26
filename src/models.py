"""
Database models for the AI Study Buddy application
"""
import sqlite3
import hashlib
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask_login import UserMixin
from enum import Enum

class ContentUploadStatus(Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    MISSING = "missing"

class StudySessionStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"  
    COMPLETED = "completed"
    SKIPPED = "skipped"

class User(UserMixin):
    """User model for authentication and profile management"""
    
    def __init__(self, user_id: str, email: str, username: str, password_hash: str, 
                 created_at: str, profile_data: Optional[str] = None):
        self.id = user_id
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at
        self.profile_data = profile_data or "{}"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches the stored hash"""
        return self.password_hash == self.hash_password(password)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at,
            'profile_data': self.profile_data
        }

class Course:
    """Course model representing a complete course with all materials and study plan"""
    
    def __init__(self, course_id: str, user_id: str, title: str, description: str,
                 course_outline: str, created_at: str, metadata: str = "{}"):
        self.id = course_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.course_outline = course_outline  # JSON string with course structure
        self.created_at = created_at
        self.metadata = json.loads(metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'course_outline': json.loads(self.course_outline) if isinstance(self.course_outline, str) else self.course_outline,
            'created_at': self.created_at,
            'metadata': self.metadata
        }

class StudyPlan:
    """Study plan model with scheduled sessions and content requirements"""
    
    def __init__(self, plan_id: str, course_id: str, user_id: str, plan_data: str,
                 created_at: str, updated_at: str, status: str = "active"):
        self.id = plan_id
        self.course_id = course_id
        self.user_id = user_id
        self.plan_data = json.loads(plan_data) if isinstance(plan_data, str) else plan_data
        self.created_at = created_at
        self.updated_at = updated_at
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'plan_data': self.plan_data,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status
        }

class StudySession:
    """Individual study session within a study plan"""
    
    def __init__(self, session_id: str, study_plan_id: str, course_id: str, user_id: str,
                 session_number: int, title: str, topics: str, scheduled_date: str,
                 estimated_duration: int, content_requirements: str, study_guide: str,
                 status: str = "scheduled", completed_at: str = None, 
                 validation_score: float = None, notes: str = None):
        self.id = session_id
        self.study_plan_id = study_plan_id
        self.course_id = course_id
        self.user_id = user_id
        self.session_number = session_number
        self.title = title
        self.topics = json.loads(topics) if isinstance(topics, str) else topics
        self.scheduled_date = scheduled_date
        self.estimated_duration = estimated_duration
        self.content_requirements = json.loads(content_requirements) if isinstance(content_requirements, str) else content_requirements
        self.study_guide = study_guide
        self.status = status
        self.completed_at = completed_at
        self.validation_score = validation_score
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'study_plan_id': self.study_plan_id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'session_number': self.session_number,
            'title': self.title,
            'topics': self.topics,
            'scheduled_date': self.scheduled_date,
            'estimated_duration': self.estimated_duration,
            'content_requirements': self.content_requirements,
            'study_guide': self.study_guide,
            'status': self.status,
            'completed_at': self.completed_at,
            'validation_score': self.validation_score,
            'notes': self.notes
        }

class Database:
    """Enhanced SQLite database manager for course and study plan management"""
    
    def __init__(self, db_path: str = "study_buddy.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    profile_data TEXT DEFAULT '{}'
                )
            ''')
            
            # Courses table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    course_outline TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Course materials table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS course_materials (
                    id TEXT PRIMARY KEY,
                    course_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    file_path TEXT,
                    content_text TEXT,
                    uploaded_at TEXT NOT NULL,
                    week_number INTEGER,
                    topics TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (course_id) REFERENCES courses (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Study plans table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS study_plans (
                    id TEXT PRIMARY KEY,
                    course_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    plan_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (course_id) REFERENCES courses (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Study sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    study_plan_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    topics TEXT NOT NULL,
                    scheduled_date TEXT NOT NULL,
                    estimated_duration INTEGER NOT NULL,
                    content_requirements TEXT NOT NULL,
                    study_guide TEXT NOT NULL,
                    status TEXT DEFAULT 'scheduled',
                    completed_at TEXT,
                    validation_score REAL,
                    notes TEXT,
                    FOREIGN KEY (study_plan_id) REFERENCES study_plans (id),
                    FOREIGN KEY (course_id) REFERENCES courses (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Legacy study sessions table for tracking progress
            conn.execute('''
                CREATE TABLE IF NOT EXISTS legacy_study_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_type TEXT NOT NULL,
                    duration_minutes INTEGER,
                    score REAL,
                    completed_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, email: str, username: str, password: str) -> Optional[User]:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        password_hash = User.hash_password(password)
        created_at = datetime.utcnow().isoformat()
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO users (id, email, username, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, email, username, password_hash, created_at))
                conn.commit()
                
                return User(user_id, email, username, password_hash, created_at)
        except sqlite3.IntegrityError:
            return None  # User already exists
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
            ).fetchone()
            
            if row:
                return User(
                    row['id'], row['email'], row['username'], 
                    row['password_hash'], row['created_at'], row['profile_data']
                )
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM users WHERE email = ?', (email,)
            ).fetchone()
            
            if row:
                return User(
                    row['id'], row['email'], row['username'], 
                    row['password_hash'], row['created_at'], row['profile_data']
                )
            return None
    
    def update_user_profile(self, user_id: str, profile_data: str) -> bool:
        """Update user profile data"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'UPDATE users SET profile_data = ? WHERE id = ?',
                    (profile_data, user_id)
                )
                conn.commit()
                return True
        except Exception:
            return False
    
    # Course Management Methods
    def create_course(self, user_id: str, title: str, description: str, course_outline: Dict[str, Any]) -> str:
        """Create a new course"""
        course_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO courses (id, user_id, title, description, course_outline, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (course_id, user_id, title, description, json.dumps(course_outline), created_at))
            conn.commit()
            
        return course_id
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM courses WHERE id = ?', (course_id,)
            ).fetchone()
            
            if row:
                return Course(
                    row['id'], row['user_id'], row['title'], row['description'],
                    row['course_outline'], row['created_at'], row['metadata']
                )
            return None
    
    def get_user_courses(self, user_id: str) -> List[Course]:
        """Get all courses for a user"""
        with self.get_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM courses WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            ).fetchall()
            
            return [Course(
                row['id'], row['user_id'], row['title'], row['description'],
                row['course_outline'], row['created_at'], row['metadata']
            ) for row in rows]
    
    def add_course_material(self, course_id: str, user_id: str, title: str, content_type: str,
                           content_text: str = None, file_path: str = None, week_number: int = None,
                           topics: List[str] = None) -> str:
        """Add course material to a course"""
        material_id = str(uuid.uuid4())
        uploaded_at = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO course_materials 
                (id, course_id, user_id, title, content_type, file_path, content_text, 
                 uploaded_at, week_number, topics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (material_id, course_id, user_id, title, content_type, file_path, 
                  content_text, uploaded_at, week_number, json.dumps(topics or [])))
            conn.commit()
            
        return material_id
    
    def get_course_materials(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all materials for a course"""
        with self.get_connection() as conn:
            rows = conn.execute(
                '''SELECT * FROM course_materials WHERE course_id = ? 
                   ORDER BY week_number ASC, uploaded_at ASC''',
                (course_id,)
            ).fetchall()
            
            return [{
                'id': row['id'],
                'course_id': row['course_id'],
                'user_id': row['user_id'],
                'title': row['title'],
                'content_type': row['content_type'],
                'file_path': row['file_path'],
                'content_text': row['content_text'],
                'uploaded_at': row['uploaded_at'],
                'week_number': row['week_number'],
                'topics': json.loads(row['topics']),
                'metadata': json.loads(row['metadata'])
            } for row in rows]
    
    # Study Plan Management Methods
    def create_study_plan(self, course_id: str, user_id: str, plan_data: Dict[str, Any]) -> str:
        """Create a study plan for a course"""
        plan_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO study_plans (id, course_id, user_id, plan_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (plan_id, course_id, user_id, json.dumps(plan_data), created_at, created_at))
            conn.commit()
            
        return plan_id
    
    def get_study_plan(self, plan_id: str) -> Optional[StudyPlan]:
        """Get study plan by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM study_plans WHERE id = ?', (plan_id,)
            ).fetchone()
            
            if row:
                return StudyPlan(
                    row['id'], row['course_id'], row['user_id'], row['plan_data'],
                    row['created_at'], row['updated_at'], row['status']
                )
            return None
    
    def get_course_study_plan(self, course_id: str) -> Optional[StudyPlan]:
        """Get active study plan for a course"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM study_plans WHERE course_id = ? AND status = "active" ORDER BY created_at DESC LIMIT 1',
                (course_id,)
            ).fetchone()
            
            if row:
                return StudyPlan(
                    row['id'], row['course_id'], row['user_id'], row['plan_data'],
                    row['created_at'], row['updated_at'], row['status']
                )
            return None
    
    def create_study_session(self, study_plan_id: str, course_id: str, user_id: str,
                           session_number: int, title: str, topics: List[str],
                           scheduled_date: str, estimated_duration: int,
                           content_requirements: Dict[str, Any], study_guide: str) -> str:
        """Create a study session"""
        session_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO study_sessions 
                (id, study_plan_id, course_id, user_id, session_number, title, topics,
                 scheduled_date, estimated_duration, content_requirements, study_guide)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, study_plan_id, course_id, user_id, session_number, title,
                  json.dumps(topics), scheduled_date, estimated_duration,
                  json.dumps(content_requirements), study_guide))
            conn.commit()
            
        return session_id
    
    def get_study_sessions(self, study_plan_id: str) -> List[StudySession]:
        """Get all study sessions for a study plan"""
        with self.get_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM study_sessions WHERE study_plan_id = ? ORDER BY session_number ASC',
                (study_plan_id,)
            ).fetchall()
            
            return [StudySession(
                row['id'], row['study_plan_id'], row['course_id'], row['user_id'],
                row['session_number'], row['title'], row['topics'], row['scheduled_date'],
                row['estimated_duration'], row['content_requirements'], row['study_guide'],
                row['status'], row['completed_at'], row['validation_score'], row['notes']
            ) for row in rows]
    
    def complete_study_session(self, session_id: str, validation_score: float = None, notes: str = None) -> bool:
        """Mark a study session as completed"""
        completed_at = datetime.utcnow().isoformat()
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE study_sessions 
                    SET status = 'completed', completed_at = ?, validation_score = ?, notes = ?
                    WHERE id = ?
                ''', (completed_at, validation_score, notes, session_id))
                conn.commit()
                return True
        except Exception:
            return False
    
    
    def add_study_session(self, user_id: str, session_type: str, 
                         duration_minutes: int = None, score: float = None,
                         metadata: str = "{}") -> str:
        """Add a legacy study session record"""
        session_id = str(uuid.uuid4())
        completed_at = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO legacy_study_sessions 
                (id, user_id, session_type, duration_minutes, score, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, session_type, duration_minutes, score, completed_at, metadata))
            conn.commit()
            
        return session_id
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user's study progress statistics"""
        with self.get_connection() as conn:
            # Get total courses
            total_courses = conn.execute(
                'SELECT COUNT(*) as count FROM courses WHERE user_id = ?',
                (user_id,)
            ).fetchone()['count']
            
            # Get active study plans
            active_plans = conn.execute(
                'SELECT COUNT(*) as count FROM study_plans WHERE user_id = ? AND status = "active"',
                (user_id,)
            ).fetchone()['count']
            
            # Get completed study sessions
            completed_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ? AND status = "completed"',
                (user_id,)
            ).fetchone()['count']
            
            # Get total study sessions
            total_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ?',
                (user_id,)
            ).fetchone()['count']
            
            # Get this week's completed sessions
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            weekly_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ? AND status = "completed" AND completed_at >= ?',
                (user_id, week_ago)
            ).fetchone()['count']
            
            # Get total study time from completed sessions
            total_time = conn.execute(
                'SELECT SUM(estimated_duration) as total FROM study_sessions WHERE user_id = ? AND status = "completed"',
                (user_id,)
            ).fetchone()['total'] or 0
            
            # Get average validation score
            avg_score = conn.execute(
                'SELECT AVG(validation_score) as avg FROM study_sessions WHERE user_id = ? AND validation_score IS NOT NULL',
                (user_id,)
            ).fetchone()['avg'] or 0
            
            # Calculate progress percentage
            progress = (completed_sessions / max(total_sessions, 1)) * 100 if total_sessions > 0 else 0
            
            return {
                'totalCourses': total_courses,
                'activePlans': active_plans,
                'completedSessions': completed_sessions,
                'totalSessions': total_sessions,
                'weeklyProgress': min(weekly_sessions * 10, 100),  # 10% per session, max 100%
                'overallProgress': min(progress, 100),
                'studyStreak': weekly_sessions,
                'totalStudyTime': round(total_time / 60, 1) if total_time else 0,  # Convert to hours
                'averageScore': round(avg_score, 1) if avg_score else 0,
                'progressPercentage': round(progress, 1)
            }
    
    def get_course_progress(self, course_id: str) -> Dict[str, Any]:
        """Get progress for a specific course"""
        with self.get_connection() as conn:
            # Get study plan for course
            study_plan = self.get_course_study_plan(course_id)
            if not study_plan:
                return {'error': 'No study plan found for course'}
            
            # Get all sessions for the study plan
            total_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE study_plan_id = ?',
                (study_plan.id,)
            ).fetchone()['count']
            
            completed_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE study_plan_id = ? AND status = "completed"',
                (study_plan.id,)
            ).fetchone()['count']
            
            # Get next upcoming session
            next_session = conn.execute(
                '''SELECT * FROM study_sessions WHERE study_plan_id = ? AND status = "scheduled" 
                   ORDER BY scheduled_date ASC LIMIT 1''',
                (study_plan.id,)
            ).fetchone()
            
            progress_percentage = (completed_sessions / max(total_sessions, 1)) * 100
            
            return {
                'course_id': course_id,
                'study_plan_id': study_plan.id,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'progress_percentage': round(progress_percentage, 1),
                'next_session': {
                    'id': next_session['id'],
                    'title': next_session['title'],
                    'scheduled_date': next_session['scheduled_date'],
                    'topics': json.loads(next_session['topics'])
                } if next_session else None
            }

    def create_course(self, user_id: str, title: str, description: str, course_outline: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a new course and return the course ID"""
        course_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata or {})
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO courses (id, user_id, title, description, course_outline, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (course_id, user_id, title, description, course_outline, created_at, metadata_json))
                conn.commit()
                return course_id
        except Exception as e:
            print(f"Error creating course: {e}")
            return None

    def get_course(self, course_id: str) -> Optional[Course]:
        """Get a course by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM courses WHERE id = ?', (course_id,)
            ).fetchone()
            
            if row:
                return Course(
                    row['id'], row['user_id'], row['title'], 
                    row['description'], row['course_outline'], 
                    row['created_at'], row['metadata']
                )
            return None

    def get_user_courses(self, user_id: str) -> List[Course]:
        """Get all courses for a user"""
        courses = []
        with self.get_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM courses WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            ).fetchall()
            
            for row in rows:
                courses.append(Course(
                    row['id'], row['user_id'], row['title'],
                    row['description'], row['course_outline'],
                    row['created_at'], row['metadata']
                ))
        return courses

    def add_course_material(self, course_id: str, user_id: str, title: str, content_type: str,
                           content_text: str, file_path: Optional[str] = None, 
                           week_number: Optional[int] = None, topics: List[str] = None) -> Optional[str]:
        """Add course material and return material ID"""
        material_id = str(uuid.uuid4())
        uploaded_at = datetime.utcnow().isoformat()
        topics_json = json.dumps(topics or [])
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO course_materials 
                    (id, course_id, user_id, title, content_type, file_path, content_text, 
                     uploaded_at, week_number, topics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (material_id, course_id, user_id, title, content_type, file_path,
                      content_text, uploaded_at, week_number, topics_json))
                conn.commit()
                return material_id
        except Exception as e:
            print(f"Error adding course material: {e}")
            return None

    def get_course_materials(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all materials for a course"""
        materials = []
        with self.get_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM course_materials WHERE course_id = ? ORDER BY uploaded_at DESC',
                (course_id,)
            ).fetchall()
            
            for row in rows:
                materials.append({
                    'id': row['id'],
                    'course_id': row['course_id'],
                    'user_id': row['user_id'],
                    'title': row['title'],
                    'content_type': row['content_type'],
                    'file_path': row['file_path'],
                    'content_text': row['content_text'],
                    'uploaded_at': row['uploaded_at'],
                    'week_number': row['week_number'],
                    'topics': json.loads(row['topics']),
                    'metadata': json.loads(row['metadata'] or '{}')
                })
        return materials

    def create_study_plan(self, course_id: str, user_id: str, plan_data: Dict[str, Any]) -> Optional[str]:
        """Create a study plan and return plan ID"""
        plan_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        plan_data_json = json.dumps(plan_data)
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO study_plans (id, course_id, user_id, plan_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (plan_id, course_id, user_id, plan_data_json, created_at, created_at))
                conn.commit()
                return plan_id
        except Exception as e:
            print(f"Error creating study plan: {e}")
            return None

    def get_course_study_plan(self, course_id: str) -> Optional[StudyPlan]:
        """Get study plan for a course"""
        with self.get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM study_plans WHERE course_id = ? ORDER BY created_at DESC LIMIT 1',
                (course_id,)
            ).fetchone()
            
            if row:
                return StudyPlan(
                    row['id'], row['course_id'], row['user_id'],
                    row['plan_data'], row['created_at'], 
                    row['updated_at'], row['status']
                )
            return None

    def add_study_session(self, study_plan_id: str, course_id: str, user_id: str,
                         session_number: int, title: str, topics: List[str],
                         scheduled_date: str, estimated_duration: int,
                         content_requirements: List[str], study_guide: str) -> Optional[str]:
        """Add a study session and return session ID"""
        session_id = str(uuid.uuid4())
        topics_json = json.dumps(topics)
        requirements_json = json.dumps(content_requirements)
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO study_sessions 
                    (id, study_plan_id, course_id, user_id, session_number, title, topics,
                     scheduled_date, estimated_duration, content_requirements, study_guide)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, study_plan_id, course_id, user_id, session_number, title,
                      topics_json, scheduled_date, estimated_duration, requirements_json, study_guide))
                conn.commit()
                return session_id
        except Exception as e:
            print(f"Error adding study session: {e}")
            return None

    def get_study_sessions(self, study_plan_id: str) -> List[StudySession]:
        """Get all study sessions for a study plan"""
        sessions = []
        with self.get_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM study_sessions WHERE study_plan_id = ? ORDER BY session_number ASC',
                (study_plan_id,)
            ).fetchall()
            
            for row in rows:
                sessions.append(StudySession(
                    row['id'], row['study_plan_id'], row['course_id'], row['user_id'],
                    row['session_number'], row['title'], row['topics'], row['scheduled_date'],
                    row['estimated_duration'], row['content_requirements'], row['study_guide'],
                    row['status'], row['completed_at'], row['validation_score'], row['notes']
                ))
        return sessions

    def complete_study_session(self, session_id: str, validation_score: float, notes: str = "") -> bool:
        """Mark a study session as completed"""
        completed_at = datetime.utcnow().isoformat()
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE study_sessions 
                    SET status = "completed", completed_at = ?, validation_score = ?, notes = ?
                    WHERE id = ?
                ''', (completed_at, validation_score, notes, session_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error completing study session: {e}")
            return False

# Global database instance
db = Database()
