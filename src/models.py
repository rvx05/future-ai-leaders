"""
Database models for the AI Study Buddy application
"""
import sqlite3
import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from flask_login import UserMixin

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

class Database:
    """Simple SQLite database manager"""
    
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
            
            # Study sessions table for tracking progress
            conn.execute('''
                CREATE TABLE IF NOT EXISTS study_sessions (
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
            
            # Course materials table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS course_materials (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    file_path TEXT,
                    content_text TEXT,
                    uploaded_at TEXT NOT NULL,
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
    
    def add_study_session(self, user_id: str, session_type: str, 
                         duration_minutes: int = None, score: float = None,
                         metadata: str = "{}") -> str:
        """Add a study session record"""
        session_id = str(uuid.uuid4())
        completed_at = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO study_sessions 
                (id, user_id, session_type, duration_minutes, score, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, session_type, duration_minutes, score, completed_at, metadata))
            conn.commit()
            
        return session_id
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's study progress statistics"""
        with self.get_connection() as conn:
            # Get total sessions
            total_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ?',
                (user_id,)
            ).fetchone()['count']
            
            # Get this week's sessions
            week_ago = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat())
            weekly_sessions = conn.execute(
                'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ? AND completed_at >= ?',
                (user_id, week_ago)
            ).fetchone()['count']
            
            # Get total study time
            total_time = conn.execute(
                'SELECT SUM(duration_minutes) as total FROM study_sessions WHERE user_id = ? AND duration_minutes IS NOT NULL',
                (user_id,)
            ).fetchone()['total'] or 0
            
            # Get average score
            avg_score = conn.execute(
                'SELECT AVG(score) as avg FROM study_sessions WHERE user_id = ? AND score IS NOT NULL',
                (user_id,)
            ).fetchone()['avg'] or 0
            
            return {
                'weeklyProgress': min(weekly_sessions * 10, 100),  # 10% per session, max 100%
                'overallProgress': min(total_sessions * 5, 100),   # 5% per session, max 100%
                'studyStreak': weekly_sessions,  # Simplified streak calculation
                'totalStudyTime': round(total_time / 60, 1) if total_time else 0,  # Convert to hours
                'averageScore': round(avg_score, 1) if avg_score else 0,
                'totalSessions': total_sessions
            }

# Global database instance
db = Database()
