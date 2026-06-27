from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

class Category(str, Enum):
    INTERVIEW = "interview"
    CV_SKILL = "cv_skill"

@dataclass
class QuestionRecord:
    id: Optional[int]
    session_id: int
    question_date: str
    section: str
    number: int
    category: Union[Category, str]
    sub_type: str
    difficulty: str
    topics: str
    question_text: str
    user_performance: Optional[int] = None
    last_reviewed: Optional[str] = None
    question_type: Optional[str] = None

def get_db_path() -> str:
    """Resolve the path to interview_ninja.sqlite3.
    
    If the package is placed inside backend/, the database is at backend/interview_ninja.sqlite3.
    This resolves the path dynamically to work both when run from workspace root or inside backend/.
    """
    path_rel = Path(__file__).resolve().parent.parent / "interview_ninja.sqlite3"
    if path_rel.exists() or Path(__file__).resolve().parent.parent.exists():
        return str(path_rel)
    return "interview_ninja.sqlite3"

def init_db() -> None:
    """Initialize the SQLite database schema if tables do not exist and handle migrations."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                difficulty_hint TEXT,
                cv_present INTEGER NOT NULL DEFAULT 0,
                jd_present INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Create questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_date TEXT NOT NULL,
                section TEXT NOT NULL,
                number INTEGER NOT NULL,
                category TEXT NOT NULL,
                sub_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                topics TEXT NOT NULL,
                question_text TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        
        # Migrations: Add user_performance, last_reviewed, and question_type to questions table if they do not exist
        cursor.execute("PRAGMA table_info(questions);")
        columns = [row[1] for row in cursor.fetchall()]
        if "user_performance" not in columns:
            cursor.execute("ALTER TABLE questions ADD COLUMN user_performance INTEGER DEFAULT NULL;")
        if "last_reviewed" not in columns:
            cursor.execute("ALTER TABLE questions ADD COLUMN last_reviewed TEXT DEFAULT NULL;")
        if "question_type" not in columns:
            cursor.execute("ALTER TABLE questions ADD COLUMN question_type TEXT DEFAULT NULL;")
            
        # Create session_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                question_id INTEGER NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_type TEXT NOT NULL,
                is_completed INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Create user_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                question_model TEXT NOT NULL,
                answer_model TEXT NOT NULL,
                openai_key TEXT DEFAULT '',
                gemini_key TEXT DEFAULT '',
                anthropic_key TEXT DEFAULT ''
            )
        """)
        
        # Create system_design_topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_design_topics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brief TEXT NOT NULL,
                category TEXT NOT NULL,
                scale TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                is_lld INTEGER NOT NULL DEFAULT 0,
                subtopics_json TEXT NOT NULL DEFAULT '[]',
                is_custom INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Create lab_sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lab_name TEXT NOT NULL,
                name TEXT NOT NULL,
                is_custom INTEGER NOT NULL DEFAULT 0,
                UNIQUE(lab_name, name)
            )
        """)

        # Create cv_topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cv_topics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brief TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                prerequisites_json TEXT NOT NULL DEFAULT '[]',
                subtopics_json TEXT NOT NULL DEFAULT '[]',
                is_custom INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Create dsa_topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dsa_topics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brief TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                prerequisites_json TEXT NOT NULL DEFAULT '[]',
                subtopics_json TEXT NOT NULL DEFAULT '[]',
                is_custom INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        seed_system_design_topics(cursor)
        seed_cv_topics(cursor)
        seed_dsa_topics(cursor)

        # Seed lab_sections from topics
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'system_design', category, 0 FROM system_design_topics WHERE is_custom = 0
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'system_design', category, 1 FROM system_design_topics WHERE is_custom = 1
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'cv', category, 0 FROM cv_topics WHERE is_custom = 0
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'cv', category, 1 FROM cv_topics WHERE is_custom = 1
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'dsa', category, 0 FROM dsa_topics WHERE is_custom = 0
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            SELECT DISTINCT 'dsa', category, 1 FROM dsa_topics WHERE is_custom = 1
        """)
        
        conn.commit()
    finally:
        conn.close()

def create_session(
    session_date: str,
    difficulty_hint: Optional[str] = None,
    cv_present: bool = False,
    jd_present: bool = False,
) -> int:
    """Create a new session record and return the session ID."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (session_date, difficulty_hint, cv_present, jd_present)
            VALUES (?, ?, ?, ?)
            """,
            (session_date, difficulty_hint, 1 if cv_present else 0, 1 if jd_present else 0),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def insert_questions(session_id: int, questions: List[dict]) -> List[int]:
    """Insert a batch of questions under a specific session ID and return their database IDs."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT session_date FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        session_date = row[0] if row else date.today().isoformat()
        
        inserted_ids = []
        for q in questions:
            topics_val = q.get("topics", [])
            if isinstance(topics_val, list):
                topics_str = ",".join(topics_val)
            else:
                topics_str = str(topics_val)
                
            category_val = q["category"]
            category_str = category_val.value if hasattr(category_val, "value") else str(category_val)
            
            cursor.execute(
                """
                INSERT INTO questions (
                    session_id, question_date, section, number,
                    category, sub_type, difficulty, topics, question_text,
                    question_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    session_date,
                    q["section"],
                    q["number"],
                    category_str,
                    q["sub_type"],
                    q["difficulty"],
                    topics_str,
                    q["question_text"],
                    q.get("question_type", q["sub_type"]),
                ),
            )
            inserted_ids.append(cursor.lastrowid)
        conn.commit()
        return inserted_ids
    finally:
        conn.close()

def fetch_questions(
    category: Optional[Category] = None,
    session_date: Optional[str] = None,
    topic: Optional[str] = None,
) -> List[QuestionRecord]:
    """Query the questions table with optional filters."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        query = """
            SELECT id, session_id, question_date, section, number,
                   category, sub_type, difficulty, topics, question_text,
                   user_performance, last_reviewed, question_type
            FROM questions
            WHERE 1=1
        """
        params = []
        if category is not None:
            category_str = category.value if hasattr(category, "value") else str(category)
            query += " AND category = ?"
            params.append(category_str)
        if session_date is not None:
            query += " AND question_date = ?"
            params.append(session_date)
        if topic is not None:
            query += " AND (topics = ? OR topics LIKE ? OR topics LIKE ? OR topics LIKE ?)"
            params.extend([topic, f"{topic},%", f"%,{topic}", f"%,{topic},%"])
            
        query += " ORDER BY session_id DESC, section ASC, number ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            cat_str = row[5]
            try:
                cat_val = Category(cat_str)
            except ValueError:
                cat_val = cat_str
                
            records.append(
                QuestionRecord(
                    id=row[0],
                    session_id=row[1],
                    question_date=row[2],
                    section=row[3],
                    number=row[4],
                    category=cat_val,
                    sub_type=row[6],
                    difficulty=row[7],
                    topics=row[8],
                    question_text=row[9],
                    user_performance=row[10],
                    last_reviewed=row[11],
                    question_type=row[12],
                )
            )
        return records
    finally:
        conn.close()

def update_question_performance(question_id: int, user_performance: int, last_reviewed: str) -> None:
    """Update user performance and last reviewed date for a specific question."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE questions
            SET user_performance = ?, last_reviewed = ?
            WHERE id = ?
            """,
            (user_performance, last_reviewed, question_id),
        )
        conn.commit()
    finally:
        conn.close()

def save_session_progress(answers: List[dict]) -> None:
    """Save or update session answers in the progress table."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        for answer in answers:
            # Upsert-like behavior using session_date and question_text or question_id
            q_id = answer.get("questionId")
            q_id_val = int(q_id) if q_id is not None and str(q_id).isdigit() else None
            
            # Check if record already exists
            if q_id_val is not None:
                cursor.execute(
                    "SELECT id FROM session_progress WHERE session_date = ? AND question_id = ?",
                    (answer["sessionDate"], q_id_val),
                )
            else:
                cursor.execute(
                    "SELECT id FROM session_progress WHERE session_date = ? AND question_text = ?",
                    (answer["sessionDate"], answer["questionText"]),
                )
                
            row = cursor.fetchone()
            is_completed_val = 1 if answer.get("isCompleted", False) else 0
            
            if row:
                cursor.execute(
                    """
                    UPDATE session_progress
                    SET answer_text = ?, is_completed = ?, category = ?, difficulty = ?, question_type = ?
                    WHERE id = ?
                    """,
                    (
                        answer["answerText"],
                        is_completed_val,
                        answer["category"],
                        answer["difficulty"],
                        answer["questionType"],
                        row[0],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO session_progress (
                        session_date, question_id, question_text, answer_text,
                        category, difficulty, question_type, is_completed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        answer["sessionDate"],
                        q_id_val,
                        answer["questionText"],
                        answer["answerText"],
                        answer["category"],
                        answer["difficulty"],
                        answer["questionType"],
                        is_completed_val,
                    ),
                )
        conn.commit()
    finally:
        conn.close()

def fetch_session_progress(session_date: str) -> List[dict]:
    """Retrieve all session progress records for a given date."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, session_date, question_id, question_text, answer_text,
                   category, difficulty, question_type, is_completed
            FROM session_progress
            WHERE session_date = ?
            """,
            (session_date,),
        )
        rows = cursor.fetchall()
        out = []
        for r in rows:
            out.append({
                "id": str(r[0]),
                "sessionDate": r[1],
                "questionId": str(r[2]) if r[2] is not None else None,
                "questionText": r[3],
                "answerText": r[4],
                "category": r[5],
                "difficulty": r[6],
                "questionType": r[7],
                "isCompleted": bool(r[8]),
            })
        return out
    finally:
        conn.close()

def fetch_progress_stats() -> dict:
    """Retrieve statistics about session progress."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT session_date, is_completed FROM session_progress")
        rows = cursor.fetchall()
        
        unique_dates = list(set(r[0] for r in rows))
        completed = sum(1 for r in rows if r[1] == 1)
        
        # Sort dates descending and take top 7
        unique_dates.sort(reverse=True)
        recent_dates = unique_dates[:7]
        
        return {
            "totalSessions": len(unique_dates),
            "totalAnswered": len(rows),
            "completedAnswers": completed,
            "recentDates": recent_dates,
        }
    finally:
        conn.close()

def fetch_settings() -> dict:
    """Retrieve user configurations, or return defaults if unset."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question_model, answer_model, openai_key, gemini_key, anthropic_key FROM user_settings LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            return {
                "questionModel": row[0],
                "answerModel": row[1],
                "openaiKey": row[2] or "",
                "geminiKey": row[3] or "",
                "anthropicKey": row[4] or "",
            }
        else:
            return {
                "questionModel": "gemini-2.5-flash",
                "answerModel": "gemini-2.5-flash",
                "openaiKey": "",
                "geminiKey": "",
                "anthropicKey": "",
            }
    finally:
        conn.close()

def save_settings(settings: dict) -> None:
    """Save or update user configurations."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        # Clean current settings
        cursor.execute("DELETE FROM user_settings")
        cursor.execute(
            """
            INSERT INTO user_settings (question_model, answer_model, openai_key, gemini_key, anthropic_key)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                settings["questionModel"],
                settings["answerModel"],
                settings.get("openaiKey", ""),
                settings.get("geminiKey", ""),
                settings.get("anthropicKey", ""),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_system_design_topics() -> List[dict]:
    """Retrieve all system design topics, including both seeded and custom user topics."""
    import json
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, brief, category, scale, difficulty, is_lld, subtopics_json, is_custom
            FROM system_design_topics
            ORDER BY is_custom ASC, rowid ASC
            """
        )
        rows = cursor.fetchall()
        out = []
        for r in rows:
            try:
                subtopics = json.loads(r[7])
            except Exception:
                subtopics = []
            out.append({
                "id": r[0],
                "name": r[1],
                "brief": r[2],
                "category": r[3],
                "scale": r[4],
                "difficulty": r[5],
                "isLLD": bool(r[6]),
                "subtopics": subtopics,
                "isCustom": bool(r[8]),
            })
        return out
    finally:
        conn.close()


def save_system_design_topic(topic: dict) -> None:
    """Save a user-added custom system design topic."""
    import json
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO system_design_topics (
                id, name, brief, category, scale, difficulty, is_lld, subtopics_json, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT is_custom FROM system_design_topics WHERE id = ?), 1))
            """,
            (
                topic["id"],
                topic["name"],
                topic["brief"],
                topic["category"],
                topic["scale"],
                topic["difficulty"],
                1 if topic.get("isLLD", False) else 0,
                json.dumps(topic.get("subtopics", [])),
                topic["id"]
            )
        )
        conn.commit()
    finally:
        conn.close()


def seed_system_design_topics(cursor: sqlite3.Cursor) -> None:
    """Seed the 50 predefined topics into the database if empty."""
    import json
    cursor.execute("SELECT COUNT(*) FROM system_design_topics WHERE is_custom = 0")
    if cursor.fetchone()[0] > 0:
        return

    seed_data = [
        {
            "id": "scaling-fundamentals",
            "name": "Scaling Fundamentals",
            "brief": "Learn when and how to scale system tiers vertically or horizontally.",
            "category": "Fundamentals",
            "scale": "N/A",
            "difficulty": "Easy",
            "subtopics": [
                {"id": "vertical-horizontal", "name": "Vertical vs Horizontal Scaling", "brief": "Scale up vs scale out tradeoffs."},
                {"id": "stateless-stateful", "name": "Stateless vs Stateful Services", "brief": "Managing session state across instances."},
                {"id": "when-to-scale", "name": "When to Scale What", "brief": "Metric-driven scaling criteria."}
            ]
        },
        {
            "id": "load-balancing",
            "name": "Load Balancing",
            "brief": "Distribute network or application traffic across servers.",
            "category": "Fundamentals",
            "scale": "100k+ RPS",
            "difficulty": "Easy",
            "subtopics": [
                {"id": "l4-l7", "name": "L4 vs L7 Load Balancers", "brief": "Transport vs application layer routing."},
                {"id": "lb-algorithms", "name": "Algorithms (Round Robin, Least Connections, Consistent Hashing)", "brief": "Traffic distribution policies."},
                {"id": "health-failover", "name": "Health Checks & Failover", "brief": "Detecting and routing around unhealthy instances."}
            ]
        },
        {
            "id": "caching-strategies",
            "name": "Caching Strategies",
            "brief": "Speed up reads and reduce database load using caching.",
            "category": "Fundamentals",
            "scale": "N/A",
            "difficulty": "Easy-Medium",
            "subtopics": [
                {"id": "cache-patterns", "name": "Cache-Aside, Write-Through, Write-Behind", "brief": "Data synchronization patterns."},
                {"id": "eviction-policies", "name": "Eviction Policies (LRU, LFU, TTL)", "brief": "How cache memory is reclaimed."},
                {"id": "invalidation-patterns", "name": "Cache Invalidation Patterns", "brief": "Keeping cache and database in sync."}
            ]
        },
        {
            "id": "cdn",
            "name": "CDN (Content Delivery Network)",
            "brief": "Deliver content quickly from locations close to users.",
            "category": "Fundamentals",
            "scale": "100M+ Req/day",
            "difficulty": "Easy",
            "subtopics": [
                {"id": "cdn-how-works", "name": "How CDNs Work (Pull vs Push)", "brief": "Origin offloading and content delivery."},
                {"id": "cache-hierarchy", "name": "Cache Hierarchy & Edge Locations", "brief": "Regional caches and edge PoPs."},
                {"id": "cdn-vs-origin", "name": "When to Use CDN vs Origin", "brief": "Static assets vs dynamic endpoints."}
            ]
        },
        {
            "id": "database-fundamentals",
            "name": "Database Fundamentals",
            "brief": "Understand storage engines, indexing, and transactional guarantees.",
            "category": "Fundamentals",
            "scale": "N/A",
            "difficulty": "Easy-Medium",
            "subtopics": [
                {"id": "sql-vs-nosql", "name": "SQL vs NoSQL (when to pick what)", "brief": "Relational vs non-relational storage."},
                {"id": "acid-vs-base", "name": "ACID vs BASE", "brief": "Transactional safety vs availability."},
                {"id": "indexing-query-opt", "name": "Indexing Strategies & Query Optimization", "brief": "B-Trees, Hash indexes, and execution plans."}
            ]
        },
        {
            "id": "database-sharding",
            "name": "Database Sharding",
            "brief": "Partition data across multiple database instances.",
            "category": "Fundamentals",
            "scale": "10TB+ Data",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "sharding-strategies", "name": "Sharding Strategies (hash, range, geo)", "brief": "Horizontal partitioning methods."},
                {"id": "rebalancing-hotspots", "name": "Rebalancing & Hotspot Handling", "brief": "Dealing with skewed traffic/storage."},
                {"id": "cross-shard-queries", "name": "Cross-Shard Queries & Joins", "brief": "Handling distributed transaction complexities."}
            ]
        },
        {
            "id": "database-replication",
            "name": "Database Replication",
            "brief": "Copy data across multiple machines for durability and scale.",
            "category": "Fundamentals",
            "scale": "10k writes/sec",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "replication-topologies", "name": "Leader-Follower, Leader-Leader", "brief": "Topology design and write management."},
                {"id": "sync-vs-async-repl", "name": "Synchronous vs Asynchronous Replication", "brief": "Tradeoffs in durability vs latency."},
                {"id": "repl-lag-consistency", "name": "Replication Lag & Read-After-Write Consistency", "brief": "Handling stale replica reads."}
            ]
        },
        {
            "id": "cap-theorem",
            "name": "CAP Theorem & Consistency Models",
            "brief": "Learn CAP and PACELC trade-offs in distributed data systems.",
            "category": "Fundamentals",
            "scale": "N/A",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "cap-pacelc", "name": "CAP & PACELC", "brief": "Understanding consistency, availability, partitions, latency."},
                {"id": "consistency-models", "name": "Strong, Eventual, Causal Consistency", "brief": "Hierarchy of consistency models."},
                {"id": "real-world-tradeoffs", "name": "Real-World Tradeoffs (Dynamo, Cassandra, Spanner)", "brief": "How modern databases handle CAP."}
            ]
        },
        {
            "id": "consistent-hashing",
            "name": "Consistent Hashing",
            "brief": "Minimize hash ring remapping when nodes join or leave.",
            "category": "Fundamentals",
            "scale": "1M+ Nodes",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "virtual-nodes", "name": "Virtual Nodes & Ring-Based Distribution", "brief": "Even load distribution technique."},
                {"id": "node-membership", "name": "Adding/Removing Nodes", "brief": "Data migration path during cluster scaling."},
                {"id": "hashing-use-cases", "name": "Use Cases (distributed caches, partitioning)", "brief": "Redis, Memcached, Dynamo sharding."}
            ]
        },
        {
            "id": "message-queues",
            "name": "Message Queues & Async Processing",
            "brief": "Deconstruct request flows using asynchronous event brokers.",
            "category": "Fundamentals",
            "scale": "1M Events/sec",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "queue-pubsub-streaming", "name": "Queue vs Pub/Sub vs Streaming", "brief": "RabbitMQ vs Kafka vs SQS."},
                {"id": "delivery-guarantees", "name": "At-Least-Once, At-Most-Once, Exactly-Once Delivery", "brief": "Message delivery mechanics."},
                {"id": "backpressure-dlq", "name": "Backpressure & Dead Letter Queues", "brief": "Handling failures and slow consumers."}
            ]
        },
        {
            "id": "api-design",
            "name": "API Design & Rate Limiting",
            "brief": "Design clean external interfaces and protect them from abuse.",
            "category": "API & Microservices",
            "scale": "N/A",
            "difficulty": "Easy-Medium",
            "subtopics": [
                {"id": "protocols", "name": "REST vs gRPC vs GraphQL vs WebSockets", "brief": "API communication protocols."},
                {"id": "pagination", "name": "Pagination (cursor vs offset)", "brief": "Query paging design."},
                {"id": "rate-limiting-algos", "name": "Rate Limiting Algorithms (Token Bucket, Sliding Window)", "brief": "Traffic throttling methods."}
            ]
        },
        {
            "id": "microservices-architecture",
            "name": "Microservices Architecture",
            "brief": "Design service boundaries, communication networks, and discovery systems.",
            "category": "API & Microservices",
            "scale": "100+ Services",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "migration", "name": "Monolith → Microservices Migration", "brief": "Strangler Fig pattern and modular decoupling."},
                {"id": "discovery-comm", "name": "Service Discovery & Communication", "brief": "DNS, Consul, and HTTP vs RPC protocols."},
                {"id": "saga-pattern", "name": "Saga Pattern & Distributed Transactions", "brief": "Choreographed and orchestrated sagas."}
            ]
        },
        {
            "id": "event-driven-architecture",
            "name": "Event-Driven Architecture",
            "brief": "Build decoupling systems by publishing and reacting to events.",
            "category": "API & Microservices",
            "scale": "100M Events/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "event-sourcing", "name": "Event Sourcing", "brief": "Storing state modifications as event sequences."},
                {"id": "cqrs", "name": "CQRS (Command Query Responsibility Segregation)", "brief": "Splitting read and write paths."},
                {"id": "choreography-orchestration", "name": "Choreography vs Orchestration", "brief": "Decentralized vs centralized flows."}
            ]
        },
        {
            "id": "url-shortener",
            "name": "Design a URL Shortener (TinyURL)",
            "brief": "Design a high-throughput, low-latency URL redirect service.",
            "category": "System Design (HLD)",
            "scale": "100M URLs/day",
            "difficulty": "Easy",
            "subtopics": [
                {"id": "hash-generation", "name": "Hash Generation & Collision Handling", "brief": "MD5 vs Base62 encoding."},
                {"id": "read-heavy-opt", "name": "Read-Heavy Optimization", "brief": "Caching redirection mappings."},
                {"id": "analytics-expiration", "name": "Analytics & Expiration", "brief": "Handling click counts and storage cleanup."}
            ]
        },
        {
            "id": "pastebin",
            "name": "Design a Paste Bin",
            "brief": "Design a web application to share plain text snippet files.",
            "category": "System Design (HLD)",
            "scale": "10M pastes/day",
            "difficulty": "Easy",
            "subtopics": [
                {"id": "paste-storage", "name": "Storage Strategy for Text Blobs", "brief": "Object storage vs relational database."},
                {"id": "paste-expiration", "name": "Expiration & Cleanup", "brief": "S3 lifecycle policies and cron jobs."},
                {"id": "paste-rate-limiting", "name": "Rate Limiting Abuse", "brief": "IP-based restriction of paste uploads."}
            ]
        },
        {
            "id": "rate-limiter",
            "name": "Design a Rate Limiter",
            "brief": "Design a high-scale API gateway utility to limit incoming traffic.",
            "category": "System Design (HLD)",
            "scale": "1M RPS",
            "difficulty": "Easy-Medium",
            "subtopics": [
                {"id": "rl-token-bucket", "name": "Token Bucket & Sliding Window Counter", "brief": "Comparing core algorithms."},
                {"id": "distributed-rl", "name": "Distributed Rate Limiting (Redis-based)", "brief": "Using Redis cluster and Lua scripts."},
                {"id": "rl-scopes", "name": "Per-User vs Per-IP vs Per-API", "brief": "Configuring rate limiter granularity."}
            ]
        },
        {
            "id": "key-value-store",
            "name": "Design a Key-Value Store",
            "brief": "Design a distributed KV store with high-performance writes.",
            "category": "System Design (HLD)",
            "scale": "Petabyte scale",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "kv-persistence", "name": "In-Memory + Persistence (LSM Tree, SSTable)", "brief": "Write Path, Memtable, Commit Log."},
                {"id": "kv-replication", "name": "Replication & Consistency", "brief": "Quorum writes, sloppy quorum."},
                {"id": "conflict-resolution", "name": "Conflict Resolution (Vector Clocks, Last-Write-Wins)", "brief": "Handling concurrent edits."}
            ]
        },
        {
            "id": "twitter",
            "name": "Design Twitter / X",
            "brief": "Design a social media network with news feed generation.",
            "category": "System Design (HLD)",
            "scale": "500M Tweets/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "tweet-fanout", "name": "Value-based Fan-Out on Write vs Fan-Out on Read", "brief": "Push vs pull feed architecture."},
                {"id": "tweet-timeline", "name": "Timeline Generation & Ranking", "brief": "Caching user home timelines."},
                {"id": "celebrity-problem", "name": "Celebrity Problem & Hybrid Approach", "brief": "Handling users with millions of followers."}
            ]
        },
        {
            "id": "instagram",
            "name": "Design Instagram",
            "brief": "Design a photo and video sharing social network.",
            "category": "System Design (HLD)",
            "scale": "100M Uploads/day",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "insta-upload", "name": "Photo Upload & Storage Pipeline", "brief": "S3 storage, media transcoding, metadata."},
                {"id": "insta-feed", "name": "News Feed Generation", "brief": "Caching posts of followed users."},
                {"id": "insta-explore", "name": "Explore/Recommendation Feed", "brief": "Machine learning model ranking."}
            ]
        },
        {
            "id": "whatsapp",
            "name": "Design WhatsApp / Messenger",
            "brief": "Design a secure, low-latency, real-time messaging application.",
            "category": "System Design (HLD)",
            "scale": "100B Messages/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "wa-realtime", "name": "Real-Time Messaging (WebSockets, Long Polling)", "brief": "Connection manager and gateway design."},
                {"id": "wa-guarantees", "name": "Message Delivery Guarantees", "brief": "Sent, delivered, and read indicators."},
                {"id": "wa-group-encryption", "name": "Group Chat & End-to-End Encryption", "brief": "Signal Protocol, group sessions."},
                {"id": "wa-offline", "name": "Offline Messaging & Sync", "brief": "Storing and delivering pending messages."}
            ]
        },
        {
            "id": "youtube-netflix",
            "name": "Design YouTube / Netflix",
            "brief": "Design a high-scale video hosting and streaming service.",
            "category": "System Design (HLD)",
            "scale": "200M concurrent users",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "yt-upload", "name": "Video Upload & Transcoding Pipeline", "brief": "Chunking, formats (MP4, WebM), resolutions."},
                {"id": "yt-streaming", "name": "Adaptive Bitrate Streaming (HLS, DASH)", "brief": "Adjusting stream quality dynamically."},
                {"id": "yt-recommendation", "name": "Recommendation Engine & CDN Strategy", "brief": "Optimizing edge cache hit rate."},
                {"id": "yt-live", "name": "Live Streaming Architecture", "brief": "Low-latency ingestion and delivery."}
            ]
        },
        {
            "id": "google-drive",
            "name": "Design Google Drive / Dropbox",
            "brief": "Design a file synchronization and storage cloud service.",
            "category": "System Design (HLD)",
            "scale": "50M active users",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "gd-chunking", "name": "File Chunking & Deduplication", "brief": "Block-level sync and content-based hashing."},
                {"id": "gd-conflict", "name": "Sync Conflict Resolution", "brief": "Client vs server side merge strategies."},
                {"id": "gd-versioning", "name": "Versioning & Delta Sync", "brief": "Only uploading modified file blocks."},
                {"id": "gd-notification", "name": "Notification Service for Changes", "brief": "WebSocket/SSE update pushes."}
            ]
        },
        {
            "id": "uber",
            "name": "Design Uber / Ola",
            "brief": "Design a real-time ride-sharing dispatch system.",
            "category": "System Design (HLD)",
            "scale": "1M active drivers",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "uber-tracking", "name": "Real-Time Location Tracking (Geohashing, Quadtrees)", "brief": "Storing driver GPS coordinates."},
                {"id": "uber-matching", "name": "Ride Matching Algorithm", "brief": "Finding nearby drivers efficiently."},
                {"id": "uber-eta", "name": "ETA Calculation & Surge Pricing", "brief": "Routing algorithms and supply-demand adjustments."},
                {"id": "uber-statemachine", "name": "Driver/Rider State Machine", "brief": "Managing dispatch state transitions."}
            ]
        },
        {
            "id": "zomato",
            "name": "Design Zomato / DoorDash",
            "brief": "Design a real-time food delivery discovery and order system.",
            "category": "System Design (HLD)",
            "scale": "5M orders/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "zomato-search", "name": "Restaurant Search & Ranking", "brief": "Geospatial indexing and search query routing."},
                {"id": "zomato-statemachine", "name": "Order State Machine & Delivery Assignment", "brief": "Matching orders with delivery partners."},
                {"id": "zomato-tracking", "name": "Real-Time Tracking & ETA Updates", "brief": "Driver coordinate updates to customer."},
                {"id": "zomato-payment", "name": "Payment & Refund Flows", "brief": "Handling transactions and failures."}
            ]
        },
        {
            "id": "notification-system",
            "name": "Design a Notification System",
            "brief": "Design a distributed system to send push, SMS, and email alerts.",
            "category": "System Design (HLD)",
            "scale": "1B notifications/day",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "notif-channels", "name": "Push, Email, SMS, In-App Channels", "brief": "Integrating third-party APIs (APNS, Twilio, SendGrid)."},
                {"id": "notif-throttling", "name": "Priority & Throttling", "brief": "Managing user preferences and message backlogs."},
                {"id": "notif-templates", "name": "Template Engine & Preference Management", "brief": "Resolving dynamic content and user opt-outs."},
                {"id": "notif-retry", "name": "Retry & Deduplication", "brief": "Idempotency keys and fallback paths."}
            ]
        },
        {
            "id": "payment-system",
            "name": "Design a Payment System (Stripe/Razorpay)",
            "brief": "Design a payment processing system with double-spend prevention.",
            "category": "System Design (HLD)",
            "scale": "10k tx/sec",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "pay-idempotency", "name": "Idempotency & Double-Spend Prevention", "brief": "Using unique transaction keys and distributed locks."},
                {"id": "pay-statemachine", "name": "Payment State Machine", "brief": "Tracking pending, authorized, and captured states."},
                {"id": "pay-ledger", "name": "Ledger Design & Reconciliation", "brief": "Double-entry bookkeeping and nightly audits."},
                {"id": "pay-pci", "name": "PCI Compliance & Tokenization", "brief": "Handling credit card data securely."}
            ]
        },
        {
            "id": "distributed-message-queue",
            "name": "Design a Distributed Message Queue (Kafka)",
            "brief": "Design a high-throughput, partitioned log broker.",
            "category": "System Design (HLD)",
            "scale": "10B events/day",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "mq-partitioning", "name": "Partitioning & Consumer Groups", "brief": "Scale-out and message order preservation."},
                {"id": "mq-offsets", "name": "Offset Management & Replayability", "brief": "Tracking consumer progress in partition logs."},
                {"id": "mq-eos", "name": "Exactly-Once Semantics", "brief": "Transactional writes and read isolation."},
                {"id": "mq-compaction", "name": "Retention & Compaction", "brief": "Log cleaning and key-based compaction."}
            ]
        },
        {
            "id": "search-autocomplete",
            "name": "Design a Search Autocomplete / Typeahead",
            "brief": "Design a real-time prefix-matching query suggestion service.",
            "category": "System Design (HLD)",
            "scale": "100k searches/sec",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "auto-trie", "name": "Trie-Based vs Prefix Search", "brief": "Structuring in-memory search structures."},
                {"id": "auto-ranking", "name": "Ranking by Popularity & Personalization", "brief": "Determining autocomplete order."},
                {"id": "auto-updates", "name": "Real-Time Updates & Caching", "brief": "Rebuilding indices with MapReduce/Spark."}
            ]
        },
        {
            "id": "web-crawler",
            "name": "Design a Web Crawler",
            "brief": "Design a scalable crawler to index the World Wide Web.",
            "category": "System Design (HLD)",
            "scale": "10B pages crawled",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "crawl-politeness", "name": "Politeness & robots.txt", "brief": "Avoiding DOS attacks on host servers."},
                {"id": "crawl-frontier", "name": "URL Frontier & Priority Scheduling", "brief": "Managing queue priority and crawl frequency."},
                {"id": "crawl-dedup", "name": "Deduplication (URL + Content)", "brief": "Minimizing redundant crawls using Bloom filters."},
                {"id": "crawl-dist", "name": "Distributed Crawling Architecture", "brief": "Partitioning domains across crawl workers."}
            ]
        },
        {
            "id": "google-maps",
            "name": "Design Google Maps",
            "brief": "Design a routing and geospatial tile serving system.",
            "category": "System Design (HLD)",
            "scale": "1B DAU",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "maps-tiles", "name": "Map Tile Serving & Caching", "brief": "Mercator projection and server caches."},
                {"id": "maps-routing", "name": "Shortest Path (Dijkstra, A*, Contraction Hierarchies)", "brief": "Low-latency route computation."},
                {"id": "maps-eta", "name": "ETA Prediction & Traffic Data Pipeline", "brief": "Fusing historical and live GPS data."},
                {"id": "maps-geospatial", "name": "Places Search & Geospatial Indexing", "brief": "Indexing points of interest using S2/H3."}
            ]
        },
        {
            "id": "recommendation-engine",
            "name": "Design a Recommendation Engine",
            "brief": "Design a real-time recommender model pipeline.",
            "category": "System Design (HLD)",
            "scale": "100M active users",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "rec-filtering", "name": "Collaborative Filtering vs Content-Based", "brief": "Comparing recommendation heuristics."},
                {"id": "rec-timing", "name": "Real-Time vs Batch Recommendations", "brief": "Offline training vs online inference."},
                {"id": "rec-features", "name": "Feature Store & Model Serving", "brief": "Feature retrieval at millisecond scale."},
                {"id": "rec-coldstart", "name": "Cold Start Problem", "brief": "Handling new users or items."}
            ]
        },
        {
            "id": "ad-click-aggregation",
            "name": "Design an Ad Click Aggregation System",
            "brief": "Design a stream processor to count global ad clicks.",
            "category": "System Design (HLD)",
            "scale": "10B clicks/day",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "ad-counting", "name": "Real-Time Counting at Scale", "brief": "Aggregating events inside streaming windows."},
                {"id": "ad-lambda", "name": "Lambda Architecture (batch + stream)", "brief": "Fast layer vs accurate batch layer."},
                {"id": "ad-fraud", "name": "Deduplication & Fraud Detection", "brief": "Filtering bot traffic and double clicks."},
                {"id": "ad-windowing", "name": "Windowed Aggregation", "brief": "Tumbling, sliding, and session windows."}
            ]
        },
        {
            "id": "metrics-monitoring",
            "name": "Design a Metrics & Monitoring System (Datadog)",
            "brief": "Design a high-scale time-series data storage and alert engine.",
            "category": "System Design (HLD)",
            "scale": "100M metrics/sec",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "metrics-ingest", "name": "Time-Series Data Ingestion at Scale", "brief": "Handling write-heavy numeric telemetry."},
                {"id": "metrics-retention", "name": "Downsampling & Retention Policies", "brief": "Reducing data density for older logs."},
                {"id": "metrics-alerting", "name": "Alerting Engine & Anomaly Detection", "brief": "Running periodic checks against metrics."},
                {"id": "metrics-query", "name": "Dashboard Query Optimization", "brief": "Caching queries and index partitions."}
            ]
        },
        {
            "id": "distributed-task-scheduler",
            "name": "Design a Distributed Task Scheduler (Airflow)",
            "brief": "Design a task runner with dependency execution rules.",
            "category": "System Design (HLD)",
            "scale": "10M tasks/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "sched-dag", "name": "DAG Execution & Dependency Resolution", "brief": "Topological sorting of workflow graphs."},
                {"id": "sched-workers", "name": "Worker Pool & Task Assignment", "brief": "Distributing jobs to distributed agents."},
                {"id": "sched-failures", "name": "Retry, Timeout, Dead Letter Handling", "brief": "Managing task runtime failures."},
                {"id": "sched-idempotency", "name": "Idempotent Task Execution", "brief": "Ensuring tasks can run multiple times safely."}
            ]
        },
        {
            "id": "gaming-leaderboard",
            "name": "Design a Real-Time Gaming Leaderboard",
            "brief": "Design a scoreboard showing ranking among millions of active users.",
            "category": "System Design (HLD)",
            "scale": "10M DAU",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "game-zset", "name": "Sorted Sets (Redis ZSET)", "brief": "Score sorting via skip-lists."},
                {"id": "game-queries", "name": "Top-K & Rank Queries", "brief": "Getting user ranks in O(log N) time."},
                {"id": "game-sharding", "name": "Sharding Strategies for Global Scale", "brief": "Partitioning score ranges across clusters."},
                {"id": "game-realtime", "name": "Near-Real-Time vs Exact Ranking", "brief": "Caching rankings to reduce database load."}
            ]
        },
        {
            "id": "distributed-cache",
            "name": "Design a Distributed Cache (Memcached Cluster)",
            "brief": "Design a custom caching cluster with consistent key routing.",
            "category": "System Design (HLD)",
            "scale": "10M RPS",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "cache-part", "name": "Consistent Hashing for Partitioning", "brief": "Node routing without a central leader."},
                {"id": "cache-stampede", "name": "Cache Stampede & Thundering Herd", "brief": "Mitigating simultaneous cache expires."},
                {"id": "cache-hotkey", "name": "Hot Key Handling", "brief": "Local replication and caching of popular items."},
                {"id": "cache-warming", "name": "Cache Warming Strategies", "brief": "Pre-populating cache keys before launch."}
            ]
        },
        {
            "id": "fraud-detection",
            "name": "Design a Fraud Detection System",
            "brief": "Design a low-latency transaction scoring application.",
            "category": "System Design (HLD)",
            "scale": "10k tx/sec",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "fraud-features", "name": "Real-Time Feature Computation", "brief": "Windowed aggregations for profile context."},
                {"id": "fraud-rules", "name": "Rule Engine + ML Hybrid", "brief": "Applying heuristics and models simultaneously."},
                {"id": "fraud-scoring", "name": "Low-Latency Scoring Pipeline", "brief": "Making decisions in under 50 milliseconds."},
                {"id": "fraud-feedback", "name": "Feedback Loop & Model Retraining", "brief": "Updating models based on manual audits."}
            ]
        },
        {
            "id": "content-moderation",
            "name": "Design a Content Moderation Pipeline",
            "brief": "Design an automated review queue for uploaded media files.",
            "category": "System Design (HLD)",
            "scale": "10M uploads/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "mod-detection", "name": "Multi-Modal Detection (text, image, video)", "brief": "Routing media to ML classifiers."},
                {"id": "mod-review", "name": "Human-in-the-Loop Review Queue", "brief": "Escalating edge cases to humans."},
                {"id": "mod-appeal", "name": "Appeal & Escalation System", "brief": "Allowing users to challenge blocks."},
                {"id": "mod-tradeoffs", "name": "Latency vs Accuracy Tradeoffs", "brief": "Synchronous vs asynchronous mod loops."}
            ]
        },
        {
            "id": "splitwise",
            "name": "Design Splitwise (Expense Sharing)",
            "brief": "Model group balances and optimize debt settlements.",
            "category": "Low-Level Design (LLD)",
            "scale": "N/A",
            "difficulty": "Easy-Medium",
            "isLLD": True,
            "subtopics": [
                {"id": "split-debt", "name": "Debt Simplification Algorithm", "brief": "Minimizing transactions using graphs."},
                {"id": "split-balances", "name": "Group & Friend Balances", "brief": "Class structures for users and transactions."},
                {"id": "split-concurrent", "name": "Concurrent Settlement Handling", "brief": "Optimistic locking on group balances."}
            ]
        },
        {
            "id": "parking-lot",
            "name": "Design a Parking Lot System",
            "brief": "Model vehicle parking allocation and billing systems.",
            "category": "Low-Level Design (LLD)",
            "scale": "N/A",
            "difficulty": "Easy",
            "isLLD": True,
            "subtopics": [
                {"id": "park-modeling", "name": "Object Modeling (Vehicle, Spot, Floor, Ticket)", "brief": "Defining class relationships."},
                {"id": "park-strategy", "name": "Strategy Pattern for Spot Assignment", "brief": "Decoupling spot allocation logic."},
                {"id": "park-billing", "name": "Payment & Exit Flow", "brief": "Ticket verification and pricing algorithms."}
            ]
        },
        {
            "id": "bookmyshow",
            "name": "Design BookMyShow (Seat Booking)",
            "brief": "Model theater seat reservation under high concurrency.",
            "category": "Low-Level Design (LLD)",
            "scale": "10k seats/sec",
            "difficulty": "Medium",
            "isLLD": True,
            "subtopics": [
                {"id": "book-locking", "name": "Seat Locking & Reservation Timeout", "brief": "Temporary locks in Redis/DB."},
                {"id": "book-concurrency", "name": "Concurrency Handling (Optimistic Locking)", "brief": "Preventing double booking."},
                {"id": "book-recovery", "name": "Payment Integration & Failure Recovery", "brief": "Reclaiming seats on payment fail."}
            ]
        },
        {
            "id": "elevator-system",
            "name": "Design an Elevator System",
            "brief": "Model lift movement and floor passenger dispatch.",
            "category": "Low-Level Design (LLD)",
            "scale": "N/A",
            "difficulty": "Easy-Medium",
            "isLLD": True,
            "subtopics": [
                {"id": "elv-state", "name": "State Machine (Idle, Moving, Stopped)", "brief": "Defining elevator state transitions."},
                {"id": "elv-scan", "name": "Scheduling Algorithms (SCAN, LOOK)", "brief": "Optimizing pick-up path."},
                {"id": "elv-coordinate", "name": "Multi-Elevator Coordination", "brief": "Dispatching elevators dynamically."}
            ]
        },
        {
            "id": "lru-cache",
            "name": "Design an LRU Cache",
            "brief": "Implement a thread-safe least recently used cache.",
            "category": "Low-Level Design (LLD)",
            "scale": "N/A",
            "difficulty": "Easy",
            "isLLD": True,
            "subtopics": [
                {"id": "lru-ds", "name": "HashMap + Doubly Linked List", "brief": "Getting O(1) reads and writes."},
                {"id": "lru-threads", "name": "Thread-Safe Implementation", "brief": "Using locks or concurrent structures."},
                {"id": "lru-ttl", "name": "Eviction & TTL Extension", "brief": "Combining LRU with time-based expiry."}
            ]
        },
        {
            "id": "pub-sub-system",
            "name": "Design a Pub-Sub System",
            "brief": "Model dynamic topic subscriptions and memory buffer queues.",
            "category": "Low-Level Design (LLD)",
            "scale": "N/A",
            "difficulty": "Medium",
            "isLLD": True,
            "subtopics": [
                {"id": "pub-registry", "name": "Topic Management & Subscriber Registry", "brief": "Observer pattern representation."},
                {"id": "pub-delivery", "name": "Message Delivery Guarantees", "brief": "Push vs pull message delivery."},
                {"id": "pub-pressure", "name": "Backpressure & Slow Consumer Handling", "brief": "Buffering and overflow policies."}
            ]
        },
        {
            "id": "chess-tictactoe",
            "name": "Design Chess / Tic-Tac-Toe",
            "brief": "Model turn-based board games with move verification.",
            "category": "Low-Level Design (LLD)",
            "scale": "N/A",
            "difficulty": "Easy",
            "isLLD": True,
            "subtopics": [
                {"id": "chess-board", "name": "Board Representation & Move Validation", "brief": "Array mapping and rule engines."},
                {"id": "chess-state", "name": "Game State Machine", "brief": "Tracking player turns and game status."},
                {"id": "chess-undo", "name": "Undo/Redo & Replay", "brief": "Command pattern implementation."}
            ]
        },
        {
            "id": "observability-sre",
            "name": "Observability & SRE Fundamentals",
            "brief": "Understand monitoring frameworks and service level targets.",
            "category": "Infrastructure & Ops",
            "scale": "N/A",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "obs-pillars", "name": "Logs, Metrics, Traces (Three Pillars)", "brief": "Fusing telemetry formats together."},
                {"id": "obs-sli", "name": "SLIs, SLOs, SLAs & Error Budgets", "brief": "Quantifying and budgeting service targets."},
                {"id": "obs-incident", "name": "Incident Response & Postmortems", "brief": "Standard operations for outages."}
            ]
        },
        {
            "id": "distributed-consensus",
            "name": "Distributed Consensus",
            "brief": "Understand consensus protocols for distributed state agreement.",
            "category": "Infrastructure & Ops",
            "scale": "N/A",
            "difficulty": "Hard",
            "subtopics": [
                {"id": "cons-raft", "name": "Paxos & Raft", "brief": "Underpinnings of state machine replication."},
                {"id": "cons-leader", "name": "Leader Election", "brief": "Heartbeats, randomized timeouts, term numbers."},
                {"id": "cons-split", "name": "Split Brain & Network Partitions", "brief": "Handling network partition recovery."}
            ]
        },
        {
            "id": "data-pipelines",
            "name": "Data Pipelines & Stream Processing",
            "brief": "Understand batch and stream processing systems at scale.",
            "category": "Infrastructure & Ops",
            "scale": "100TB/day",
            "difficulty": "Medium-Hard",
            "subtopics": [
                {"id": "pipe-batch", "name": "Batch vs Stream (MapReduce vs Flink/Spark Streaming)", "brief": "Bounded vs unbounded data streams."},
                {"id": "pipe-window", "name": "Windowing (Tumbling, Sliding, Session)", "brief": "Aggregation boundaries over time."},
                {"id": "pipe-schema", "name": "Backfill & Schema Evolution", "brief": "Re-running pipelines and mapping schema changes."}
            ]
        },
        {
            "id": "security-auth",
            "name": "Security & Auth at Scale",
            "brief": "Protect systems using token authorization and key vaults.",
            "category": "Infrastructure & Ops",
            "scale": "10k auths/sec",
            "difficulty": "Medium",
            "subtopics": [
                {"id": "sec-oauth", "name": "OAuth 2.0 & JWT Architecture", "brief": "Token format and centralized vs distributed validation."},
                {"id": "sec-gateway", "name": "API Gateway & Zero Trust", "brief": "Ingress enforcement and service mTLS."},
                {"id": "sec-secret", "name": "Secret Management & Key Rotation", "brief": "Safeguarding API tokens and database keys."},
                {"id": "sec-ddos", "name": "DDoS Mitigation", "brief": "Rate limits, CDN filtering, Web Application Firewalls."}
            ]
        },
        {
            "id": "cicd-pipeline",
            "name": "Design a CI/CD Pipeline",
            "brief": "Model automated compilation, testing, and deployment jobs.",
            "category": "Infrastructure & Ops",
            "scale": "10k builds/day",
            "difficulty": "Medium",
            "isLLD": True,
            "subtopics": [
                {"id": "ci-dag", "name": "Pipeline DAG & Stage Execution", "brief": "Resolving job dependencies in order."},
                {"id": "ci-cache", "name": "Artifact Storage & Caching", "brief": "Caching node_modules and compiler output."},
                {"id": "ci-deploy", "name": "Rollback Strategies (Blue-Green, Canary)", "brief": "Mitigating risk during server releases."},
                {"id": "ci-isolation", "name": "Concurrent Build Isolation", "brief": "Running jobs inside ephemeral containers."}
            ]
        }
    ]

    for topic in seed_data:
        cursor.execute(
            """
            INSERT OR IGNORE INTO system_design_topics (
                id, name, brief, category, scale, difficulty, is_lld, subtopics_json, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                topic["id"],
                topic["name"],
                topic["brief"],
                topic["category"],
                topic["scale"],
                topic["difficulty"],
                1 if topic.get("isLLD", False) else 0,
                json.dumps(topic.get("subtopics", [])),
            )
        )

def fetch_lab_sections(lab_name: str) -> List[dict]:
    """Retrieve all sections for a specific lab."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, lab_name, name, is_custom
            FROM lab_sections
            WHERE lab_name = ?
            ORDER BY is_custom ASC, id ASC
            """,
            (lab_name,)
        )
        rows = cursor.fetchall()
        return [{"id": r[0], "labName": r[1], "name": r[2], "isCustom": bool(r[3])} for r in rows]
    finally:
        conn.close()

def save_lab_section(lab_name: str, name: str, is_custom: int = 1) -> None:
    """Save a new lab section."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO lab_sections (lab_name, name, is_custom)
            VALUES (?, ?, ?)
            """,
            (lab_name, name, is_custom)
        )
        conn.commit()
    finally:
        conn.close()

def fetch_cv_topics() -> List[dict]:
    """Retrieve all CV topics from the database, sorted with seeded first."""
    import json
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, brief, category, difficulty, prerequisites_json, subtopics_json, is_custom
            FROM cv_topics
            ORDER BY is_custom ASC, rowid ASC
            """
        )
        rows = cursor.fetchall()
        out = []
        for r in rows:
            try:
                prereqs = json.loads(r[5])
            except Exception:
                prereqs = []
            try:
                subtopics = json.loads(r[6])
            except Exception:
                subtopics = []
            out.append({
                "id": r[0],
                "name": r[1],
                "brief": r[2],
                "category": r[3],
                "difficulty": r[4],
                "prerequisites": prereqs,
                "subtopics": subtopics,
                "isCustom": bool(r[7]),
            })
        return out
    finally:
        conn.close()


def save_cv_topic(topic: dict) -> None:
    """Save a user-added custom CV topic to the database."""
    import json
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO cv_topics (
                id, name, brief, category, difficulty, prerequisites_json, subtopics_json, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT is_custom FROM cv_topics WHERE id = ?), 1))
            """,
            (
                topic["id"],
                topic["name"],
                topic["brief"],
                topic["category"],
                topic["difficulty"],
                json.dumps(topic.get("prerequisites", [])),
                json.dumps(topic.get("subtopics", [])),
                topic["id"]
            )
        )
        conn.commit()
    finally:
        conn.close()


def seed_cv_topics(cursor: sqlite3.Cursor) -> None:
    """Seed the 35 predefined CV topics into the database if empty."""
    import json
    cursor.execute("SELECT COUNT(*) FROM cv_topics WHERE is_custom = 0")
    if cursor.fetchone()[0] > 0:
        return

    seed_data = [
        {
            "id": "image-basics",
            "name": "Image Basics & Representation",
            "brief": "Learn pixels, channels, and basic operations with OpenCV.",
            "category": "Fundamentals",
            "difficulty": "Easy",
            "prerequisites": ["Basic Python", "NumPy"],
            "subtopics": [
                {"id": "cv-pixels", "name": "Pixels, Channels, Color Spaces (RGB, HSV, LAB)", "brief": "Understanding how images are represented in memory."},
                {"id": "cv-io", "name": "Image Reading, Writing, Display with OpenCV", "brief": "Loading, displaying, and saving images using cv2."},
                {"id": "cv-transforms", "name": "Image Resizing, Cropping, Rotation", "brief": "Primary geometric manipulation operations."}
            ]
        },
        {
            "id": "filtering-convolution",
            "name": "Image Filtering & Convolution",
            "brief": "Understand spatial filtering and kernel-based image convolution.",
            "category": "Classical CV",
            "difficulty": "Easy",
            "prerequisites": ["Image Basics", "2D Convolution Math"],
            "subtopics": [
                {"id": "cv-kernels", "name": "Kernels & Convolution Operation", "brief": "Mathematical concept of moving a kernel over an image."},
                {"id": "cv-blurs", "name": "Gaussian Blur & Box Blur", "brief": "Image smoothing techniques and low-pass filtering."},
                {"id": "cv-sharpen", "name": "Sharpening Filters", "brief": "Enhancing image high-frequency details."}
            ]
        },
        {
            "id": "thresholding-binarization",
            "name": "Thresholding & Binarization",
            "brief": "Convert grayscale images to binary using global or local thresholding.",
            "category": "Classical CV",
            "difficulty": "Easy",
            "prerequisites": ["Image Basics"],
            "subtopics": [
                {"id": "cv-otsu", "name": "Global Thresholding (Otsu's Method)", "brief": "Automatic thresholding based on bimodal histograms."},
                {"id": "cv-adaptive-thresh", "name": "Adaptive Thresholding", "brief": "Local binarization under uneven lighting conditions."},
                {"id": "cv-color-mask", "name": "Color-based Segmentation (HSV masking)", "brief": "Isolating colored objects in HSV color space."}
            ]
        },
        {
            "id": "edge-detection",
            "name": "Edge Detection",
            "brief": "Detect spatial boundaries and high-contrast lines in images.",
            "category": "Classical CV",
            "difficulty": "Easy-Medium",
            "prerequisites": ["Filtering & Convolution"],
            "subtopics": [
                {"id": "cv-gradients", "name": "Sobel & Laplacian Operators", "brief": "Calculating first and second order spatial derivatives."},
                {"id": "cv-canny", "name": "Canny Edge Detection", "brief": "Multi-stage edge detector with hysteresis thresholding."},
                {"id": "cv-edge-realworld", "name": "Edge Detection for Real-World Images", "brief": "Handling noise and scaling parameter adjustments."}
            ]
        },
        {
            "id": "morphological",
            "name": "Morphological Operations",
            "brief": "Perform mathematical morphology on binary shapes.",
            "category": "Classical CV",
            "difficulty": "Easy",
            "prerequisites": ["Thresholding & Binarization"],
            "subtopics": [
                {"id": "cv-erosion-dilation", "name": "Erosion, Dilation", "brief": "Shrinking or expanding binary shapes."},
                {"id": "cv-open-close", "name": "Opening, Closing", "brief": "Opening and closing operations."},
                {"id": "cv-morph-noise", "name": "Morphological Noise Removal", "brief": "Combining operators to isolate structures."}
            ]
        },
        {
            "id": "contour-detection",
            "name": "Contour Detection & Shape Analysis",
            "brief": "Find, analyze, and classify geometric boundaries in binary images.",
            "category": "Classical CV",
            "difficulty": "Medium",
            "prerequisites": ["Thresholding & Binarization", "Edge Detection"],
            "subtopics": [
                {"id": "cv-find-contours", "name": "Finding & Drawing Contours", "brief": "Extracting curves representing boundaries."},
                {"id": "cv-contour-props", "name": "Contour Properties (area, perimeter, bounding box)", "brief": "Computing geometric indicators of a contour."},
                {"id": "cv-shape-class", "name": "Shape Classification using Contours", "brief": "Sorting contours by circularity or aspect ratio."}
            ]
        },
        {
            "id": "feature-detection",
            "name": "Feature Detection & Matching",
            "brief": "Detect robust keypoints and associate them across multiple viewpoints.",
            "category": "Classical CV",
            "difficulty": "Medium",
            "prerequisites": ["Filtering & Convolution", "Linear Algebra"],
            "subtopics": [
                {"id": "cv-harris", "name": "Harris Corner Detection", "brief": "Detecting corners based on local intensity changes."},
                {"id": "cv-orb", "name": "ORB Feature Detector", "brief": "Fast, scale-invariant binary feature keypoint descriptor."},
                {"id": "cv-matcher", "name": "Feature Matching between Images (BFMatcher)", "brief": "Associating keypoint descriptions using Hamming distance."}
            ]
        },
        {
            "id": "histogram-analysis",
            "name": "Histogram Analysis",
            "brief": "Analyze global color distribution and improve contrast.",
            "category": "Classical CV",
            "difficulty": "Easy-Medium",
            "prerequisites": ["Image Basics"],
            "subtopics": [
                {"id": "cv-hist-compute", "name": "Histogram Computation & Visualization", "brief": "Counting pixel frequency per intensity value."},
                {"id": "cv-clahe", "name": "Histogram Equalization (CLAHE)", "brief": "Contrast adjustment and adaptive equalization."},
                {"id": "cv-backprojection", "name": "Histogram Backprojection", "brief": "Finding regions matching a model color template."}
            ]
        },
        {
            "id": "geometric-homography",
            "name": "Geometric Transformations & Homography",
            "brief": "Project image viewpoints onto planes using linear maps.",
            "category": "Classical CV",
            "difficulty": "Medium",
            "prerequisites": ["Linear Algebra"],
            "subtopics": [
                {"id": "cv-affine", "name": "Affine Transformations", "brief": "Scale, translation, rotation using 2x3 matrices."},
                {"id": "cv-perspective", "name": "Perspective Transform (Bird's Eye View)", "brief": "Warping perspective using 3x3 matrices."},
                {"id": "cv-ransac", "name": "Homography Estimation with RANSAC", "brief": "Calculating projection matrices under outlier noise."}
            ]
        },
        {
            "id": "template-matching",
            "name": "Template Matching & Object Localization",
            "brief": "Search for matches to a smaller reference image within a scene.",
            "category": "Classical CV",
            "difficulty": "Medium",
            "prerequisites": ["Filtering & Convolution"],
            "subtopics": [
                {"id": "cv-tm-methods", "name": "Template Matching Methods", "brief": "Comparing normalized cross-correlation and squared diffs."},
                {"id": "cv-tm-multiscale", "name": "Multi-scale Template Matching", "brief": "Matching template over a range of resolution scales."},
                {"id": "cv-tm-limits", "name": "Limitations & When to Use", "brief": "Sensitivity to scale, rotation, and illumination."}
            ]
        },
        {
            "id": "optical-flow",
            "name": "Optical Flow & Motion Estimation",
            "brief": "Track pixel displacements across video frames.",
            "category": "Classical CV",
            "difficulty": "Medium-Hard",
            "prerequisites": ["Filtering & Convolution", "Calculus"],
            "subtopics": [
                {"id": "cv-lucas-kanade", "name": "Lucas-Kanade Optical Flow", "brief": "Sparse feature tracking over consecutive frames."},
                {"id": "cv-farneback", "name": "Dense Optical Flow (Farneback)", "brief": "Calculating displacement vectors for all pixels."},
                {"id": "cv-motion-tracking", "name": "Motion Detection & Tracking Applications", "brief": "Background subtraction and trajectory tracking."}
            ]
        },
        {
            "id": "image-segmentation-classical",
            "name": "Image Segmentation (Classical)",
            "brief": "Divide an image into semantic regions using classical algorithms.",
            "category": "Classical CV",
            "difficulty": "Medium",
            "prerequisites": ["Contour Detection"],
            "subtopics": [
                {"id": "cv-watershed", "name": "Watershed Algorithm", "brief": "Marker-based image segmentation using topographies."},
                {"id": "cv-grabcut", "name": "GrabCut", "brief": "Interactive foreground extraction using graph cuts."},
                {"id": "cv-meanshift", "name": "Mean Shift Segmentation", "brief": "Clustering pixel colors to partition regions."}
            ]
        },
        {
            "id": "camera-calibration-stereo",
            "name": "Camera Calibration & Stereo Vision",
            "brief": "Extract depth maps and spatial coordinates using multi-camera layouts.",
            "category": "Geometry & Stereo",
            "difficulty": "Hard",
            "prerequisites": ["Linear Algebra", "Geometric Transformations & Homography"],
            "subtopics": [
                {"id": "cv-params", "name": "Intrinsic & Extrinsic Parameters", "brief": "Camera focal length, principal point, pose matrices."},
                {"id": "cv-chessboard", "name": "Chessboard Calibration", "brief": "Estimating distortion coefficients via targets."},
                {"id": "cv-depth-maps", "name": "Stereo Matching & Depth Maps", "brief": "Triangulating disparity values between stereo cameras."}
            ]
        },
        {
            "id": "intro-cnn",
            "name": "Introduction to CNNs",
            "brief": "Understand the layers, math, and operations of convolutional nets.",
            "category": "Deep Learning",
            "difficulty": "Medium",
            "prerequisites": ["Python & PyTorch", "Linear Algebra", "Calculus"],
            "subtopics": [
                {"id": "cv-layers", "name": "Convolution, Pooling, Stride, Padding", "brief": "Core components of convolutional neural layers."},
                {"id": "cv-cnn-scratch", "name": "Building a CNN from Scratch (PyTorch)", "brief": "Assembling layers into a network model in PyTorch."},
                {"id": "cv-cifar", "name": "Training on CIFAR-10", "brief": "Running a complete image classification training cycle."}
            ]
        },
        {
            "id": "transfer-learning",
            "name": "Transfer Learning & Fine-Tuning",
            "brief": "Adapt large pretrained networks to target datasets.",
            "category": "Deep Learning",
            "difficulty": "Medium",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-pretrained", "name": "Using Pretrained Models (ResNet, EfficientNet)", "brief": "Loading model weights pre-trained on ImageNet."},
                {"id": "cv-fe-vs-ft", "name": "Feature Extraction vs Fine-Tuning", "brief": "Freezing backbone weights vs full tuning."},
                {"id": "cv-custom-pipeline", "name": "Custom Dataset Training Pipeline", "brief": "Custom PyTorch Dataset and DataLoader design."}
            ]
        },
        {
            "id": "classification-architectures",
            "name": "Image Classification Architectures",
            "brief": "Trace SOTA backbone structures and design evolutions.",
            "category": "Deep Learning",
            "difficulty": "Medium-Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-archs-evolution", "name": "LeNet -> AlexNet -> VGG (evolution)", "brief": "Timeline of early CNN architectures."},
                {"id": "cv-resnet", "name": "ResNet & Skip Connections", "brief": "Gradient flow optimization via residual blocks."},
                {"id": "cv-efficientnet", "name": "EfficientNet & Compound Scaling", "brief": "Compound scaling of width, depth and resolution."}
            ]
        },
        {
            "id": "yolo-object-detection",
            "name": "Object Detection with YOLO",
            "brief": "Train and deploy single-stage real-time object detectors.",
            "category": "Deep Learning",
            "difficulty": "Medium-Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-yolo-how", "name": "YOLO Architecture & How It Works", "brief": "Grid-based object detection strategy."},
                {"id": "cv-yolo-train", "name": "YOLOv8 Training on Custom Dataset", "brief": "Preparing bounding box labels and running ultralytics."},
                {"id": "cv-yolo-deploy", "name": "Real-Time Detection Deployment", "brief": "Exporting YOLO models to running scripts."}
            ]
        },
        {
            "id": "two-stage-object-detection",
            "name": "Object Detection (Two-Stage)",
            "brief": "Understand region-proposal and anchor-based detector networks.",
            "category": "Deep Learning",
            "difficulty": "Hard",
            "prerequisites": ["Introduction to CNNs", "Object Detection with YOLO"],
            "subtopics": [
                {"id": "cv-rcnn-evolution", "name": "R-CNN -> Fast R-CNN -> Faster R-CNN", "brief": "History of region proposal architectures."},
                {"id": "cv-rpn", "name": "Region Proposal Networks", "brief": "Directing CNN model attention to candidates."},
                {"id": "cv-det-metrics", "name": "Anchor Boxes, IoU, NMS, mAP Metrics", "brief": "Object detection evaluation criteria."}
            ]
        },
        {
            "id": "semantic-segmentation",
            "name": "Semantic Segmentation",
            "brief": "Classify every pixel in an image to a semantic class.",
            "category": "Deep Learning",
            "difficulty": "Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-fcn", "name": "Fully Convolutional Networks (FCN)", "brief": "Replacing linear classifier layers with conv layers."},
                {"id": "cv-unet", "name": "U-Net Architecture & Medical Imaging", "brief": "Symmetrical contracting and expanding paths."},
                {"id": "cv-deeplab", "name": "DeepLabV3+ & Atrous Convolution", "brief": "Capturing context using dilated kernels."}
            ]
        },
        {
            "id": "instance-segmentation",
            "name": "Instance Segmentation",
            "brief": "Identify, segment, and separate individual objects in scenes.",
            "category": "Deep Learning",
            "difficulty": "Hard",
            "prerequisites": ["Object Detection (Two-Stage)", "Semantic Segmentation"],
            "subtopics": [
                {"id": "cv-mask-rcnn", "name": "Mask R-CNN Architecture", "brief": "Adding a mask projection head to Faster R-CNN."},
                {"id": "cv-panoptic", "name": "Panoptic Segmentation", "brief": "Fusing background stuff and foreground things."},
                {"id": "cv-sam", "name": "Segment Anything Model (SAM)", "brief": "Promptable visual foundation segmentation models."}
            ]
        },
        {
            "id": "gans",
            "name": "GANs (Generative Adversarial Networks)",
            "brief": "Train adversarial generator and discriminator models.",
            "category": "Generative AI",
            "difficulty": "Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-gan-loop", "name": "GAN Fundamentals & Training Loop", "brief": "Minimax optimization of generator vs discriminator."},
                {"id": "cv-dcgan", "name": "DCGAN Implementation", "brief": "Using transpose convolutions to synthesize images."},
                {"id": "cv-cyclegan", "name": "CycleGAN (Unpaired Image Translation)", "brief": "Mapping styles across unaligned image sets."}
            ]
        },
        {
            "id": "diffusion-models",
            "name": "Diffusion Models",
            "brief": "Generate high-fidelity images using denoising probability paths.",
            "category": "Generative AI",
            "difficulty": "Hard",
            "prerequisites": ["Semantic Segmentation", "Probability & Calculus"],
            "subtopics": [
                {"id": "cv-ddpm", "name": "DDPM (Denoising Diffusion Probabilistic Models)", "brief": "Forward noise addition and backward denoising loops."},
                {"id": "cv-stable-diff", "name": "Stable Diffusion Architecture", "brief": "Latent diffusion inside encoded vector spaces."},
                {"id": "cv-controlnet", "name": "Controlnet & Guided Generation", "brief": "Injecting spatial conditions into U-Net paths."}
            ]
        },
        {
            "id": "vit",
            "name": "Vision Transformers (ViT)",
            "brief": "Apply self-attention mechanisms directly to image patch sequences.",
            "category": "Transformers & Attention",
            "difficulty": "Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-vit-attn", "name": "Self-Attention for Images", "brief": "Computing query-key similarity matrices over patches."},
                {"id": "cv-vit-patches", "name": "ViT Architecture & Patch Embeddings", "brief": "Flattening 16x16 pixels into token vectors."},
                {"id": "cv-swin", "name": "Swin Transformer & Hierarchical Features", "brief": "Shifted window attention to reduce complexity."}
            ]
        },
        {
            "id": "clip-multimodal",
            "name": "CLIP & Multimodal Vision",
            "brief": "Align text and image embeddings in shared contrastive spaces.",
            "category": "Transformers & Attention",
            "difficulty": "Hard",
            "prerequisites": ["Vision Transformers (ViT)"],
            "subtopics": [
                {"id": "cv-clip-contrastive", "name": "Contrastive Learning for Vision-Language", "brief": "Aligning matched image-text pairs in a batch."},
                {"id": "cv-clip-zeroshot", "name": "Zero-Shot Classification with CLIP", "brief": "Predicting image labels via dynamic text prompts."},
                {"id": "cv-clip-search", "name": "Building a CLIP-based Image Search", "brief": "Searching visual databases using natural language."}
            ]
        },
        {
            "id": "video-understanding",
            "name": "Video Understanding",
            "brief": "Analyze temporal transitions and track objects across frames.",
            "category": "Deep Learning",
            "difficulty": "Medium-Hard",
            "prerequisites": ["Introduction to CNNs", "Optical Flow & Motion Estimation"],
            "subtopics": [
                {"id": "cv-video-io", "name": "Frame Extraction & Video Processing", "brief": "Handling video stream ingestion and encoding."},
                {"id": "cv-tracking", "name": "Object Tracking (DeepSORT, ByteTrack)", "brief": "Kalman filters and embedding associations."},
                {"id": "cv-action-rec", "name": "Action Recognition (SlowFast, I3D)", "brief": "Extracting features across spatial and temporal dimensions."}
            ]
        },
        {
            "id": "face-detection-recognition",
            "name": "Face Detection & Recognition",
            "brief": "Detect human faces and associate them with identities.",
            "category": "Deep Learning",
            "difficulty": "Medium",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-classical-face", "name": "Haar Cascades & HOG Detectors", "brief": "Early face boundary detection heuristics."},
                {"id": "cv-mtcnn", "name": "MTCNN & RetinaFace", "brief": "Cascade deep networks for boundary localization."},
                {"id": "cv-facenet", "name": "FaceNet Embeddings & Face Matching", "brief": "Learning facial feature vectors using triplet loss."}
            ]
        },
        {
            "id": "ocr-document-analysis",
            "name": "OCR & Document Analysis",
            "brief": "Segment layout boundaries and read character symbols in documents.",
            "category": "Deep Learning",
            "difficulty": "Medium",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-tesseract", "name": "Tesseract OCR Pipeline", "brief": "Text detection and character recognition pipeline."},
                {"id": "cv-scene-text", "name": "Scene Text Detection (EAST, CRAFT)", "brief": "Finding dynamic text rotated in natural scenes."},
                {"id": "cv-layout-analysis", "name": "Document Layout Analysis", "brief": "Parsing sections, tables, and paragraphs."}
            ]
        },
        {
            "id": "pose-estimation",
            "name": "Pose Estimation",
            "brief": "Track human joint coordinates and body postures.",
            "category": "Deep Learning",
            "difficulty": "Medium-Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-mediapipe", "name": "OpenPose & MediaPipe", "brief": "Real-time keypoint extraction pipelines."},
                {"id": "cv-hrnet", "name": "HRNet Architecture", "brief": "Preserving high-resolution features across network pipelines."},
                {"id": "cv-pose-apps", "name": "Applications: Fitness, AR, Sign Language", "brief": "Interpreting joint coordinates for motion logic."}
            ]
        },
        {
            "id": "3d-vision-depth",
            "name": "3D Vision & Depth Estimation",
            "brief": "Generate point clouds and estimate scene depth from 2D views.",
            "category": "Geometry & Stereo",
            "difficulty": "Hard",
            "prerequisites": ["Camera Calibration & Stereo Vision"],
            "subtopics": [
                {"id": "cv-mono-depth", "name": "Monocular Depth Estimation (MiDaS)", "brief": "Predicting relative depth from a single camera frame."},
                {"id": "cv-point-clouds", "name": "Point Clouds & PointNet", "brief": "Processing unordered collections of 3D spatial points."},
                {"id": "cv-nerf", "name": "NeRF (Neural Radiance Fields)", "brief": "Synthesizing views using neural implicit representations."}
            ]
        },
        {
            "id": "model-deployment-vision",
            "name": "Model Deployment for Vision",
            "brief": "Optimize and compile neural backbones for target runtimes.",
            "category": "MLOps",
            "difficulty": "Medium",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-onnx", "name": "ONNX Export & Optimization", "brief": "Translating PyTorch models to dynamic computation graphs."},
                {"id": "cv-tensorrt", "name": "TensorRT & OpenVINO", "brief": "Compiling models for Nvidia or Intel silicon layers."},
                {"id": "cv-edge-deploy", "name": "Edge Deployment (Jetson Nano, Mobile)", "brief": "Deploying models inside resource-constrained environments."}
            ]
        },
        {
            "id": "data-augmentation-tricks",
            "name": "Data Augmentation & Training Tricks",
            "brief": "Increase dataset variety and optimize model robustness.",
            "category": "Deep Learning",
            "difficulty": "Easy-Medium",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-albumentations", "name": "Albumentations Library", "brief": "Creating fast, pixel-level bounding box augmentations."},
                {"id": "cv-aug-mix", "name": "Mixup, Cutout, CutMix", "brief": "Creating synthetic linear combination images."},
                {"id": "cv-class-imbalance", "name": "Handling Class Imbalance", "brief": "Focal Loss and weighted sample strategies."}
            ]
        },
        {
            "id": "adversarial-robustness",
            "name": "Adversarial Attacks & Robustness",
            "brief": "Deconstruct models using adversarial perturbations and defend them.",
            "category": "Deep Learning",
            "difficulty": "Hard",
            "prerequisites": ["Introduction to CNNs", "Calculus (gradients)"],
            "subtopics": [
                {"id": "cv-attacks", "name": "FGSM & PGD Attacks", "brief": "Synthesizing input perturbations along loss gradients."},
                {"id": "cv-adv-training", "name": "Adversarial Training", "brief": "Injecting perturbed inputs into training loops."},
                {"id": "cv-robustness-eval", "name": "Model Robustness Evaluation", "brief": "Testing robustness against corruption and noise."}
            ]
        },
        {
            "id": "self-supervised-vision",
            "name": "Self-Supervised Learning for Vision",
            "brief": "Learn visual features without human annotation labels.",
            "category": "Deep Learning",
            "difficulty": "Hard",
            "prerequisites": ["Introduction to CNNs", "Data Augmentation & Training Tricks"],
            "subtopics": [
                {"id": "cv-ssl-contrastive", "name": "Contrastive Learning (SimCLR, MoCo)", "brief": "Aligning positive views and pushing negative views."},
                {"id": "cv-mae", "name": "Masked Autoencoders (MAE)", "brief": "Reconstructing hidden patches of images."},
                {"id": "cv-dino-ssl", "name": "DINO & Self-Distillation", "brief": "Training ViT architectures without labels."}
            ]
        },
        {
            "id": "explainability-interpretability",
            "name": "Explainability & Interpretability",
            "brief": "Understand model decisions using attribution maps.",
            "category": "Deep Learning",
            "difficulty": "Medium-Hard",
            "prerequisites": ["Introduction to CNNs"],
            "subtopics": [
                {"id": "cv-gradcam", "name": "Grad-CAM & Saliency Maps", "brief": "Using final conv layer gradients to map focus areas."},
                {"id": "cv-shap", "name": "SHAP for Image Models", "brief": "Calculating game-theoretic pixel contributions."},
                {"id": "cv-feature-vis", "name": "What Does the Network Actually See?", "brief": "Synthesizing inputs that maximize activations."}
            ]
        },
        {
            "id": "end-to-end-projects",
            "name": "End-to-End Projects",
            "brief": "Build functional production computer vision projects.",
            "category": "Projects",
            "difficulty": "Mixed",
            "prerequisites": ["Deep Learning & Classical CV basics"],
            "subtopics": [
                {"id": "cv-proj-alpr", "name": "Build a Real-Time License Plate Reader [Medium]", "brief": "YOLO detection + OCR recognition pipeline."},
                {"id": "cv-proj-search", "name": "Build a Visual Search Engine [Hard]", "brief": "Feature database retrieval using vector embeddings."},
                {"id": "cv-proj-defect", "name": "Build a Defect Detection System (Manufacturing) [Hard]", "brief": "Anomaly segmentation under strict timing limits."},
                {"id": "cv-proj-filter", "name": "Build an AR Filter (Face Mesh + Overlay) [Medium]", "brief": "MediaPipe keypoint tracking + image mapping."},
                {"id": "cv-proj-scanner", "name": "Build a Document Scanner App [Easy-Medium]", "brief": "Contour perspective transformation + binarization."}
            ]
        }
    ]

    for topic in seed_data:
        cursor.execute(
            """
            INSERT OR IGNORE INTO cv_topics (
                id, name, brief, category, difficulty, prerequisites_json, subtopics_json, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                topic["id"],
                topic["name"],
                topic["brief"],
                topic["category"],
                topic["difficulty"],
                json.dumps(topic.get("prerequisites", [])),
                json.dumps(topic.get("subtopics", [])),
            )
        )


def seed_dsa_topics(cursor: sqlite3.Cursor) -> None:
    import json
    seed_data = [
        # ── PATTERN 1: PREFIX SUM & CUMULATIVE LOGIC ──────────────────────────
        {
            "id": "ps-subarray-sum-k",
            "name": "Subarray Sum Equals K",
            "brief": "LC #560 [Medium] — prefix sum + hashmap",
            "category": "Prefix Sum & Cumulative Logic",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ps-560-python", "name": "Python", "brief": "collections.defaultdict(int) for frequency map"},
                {"id": "ps-560-real", "name": "Real-World", "brief": "Financial transaction anomaly detection (sum of transactions in a window)"},
                {"id": "ps-560-remember", "name": "Remember", "brief": "prefix_sum - k lookup, not sliding window (negative numbers exist)"},
                {"id": "ps-560-edge", "name": "Edge", "brief": "prefix_sum map starts with {0: 1}, not empty"},
            ],
        },
        {
            "id": "ps-product-except-self",
            "name": "Product of Array Except Self",
            "brief": "LC #238 [Medium] — left × right pass",
            "category": "Prefix Sum & Cumulative Logic",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ps-238-python", "name": "Python", "brief": "list comprehension with running product, no division"},
                {"id": "ps-238-real", "name": "Real-World", "brief": "Recommendation scoring (multiply all feature weights except current)"},
                {"id": "ps-238-remember", "name": "Remember", "brief": "Left pass × Right pass trick, O(1) extra space using output array"},
                {"id": "ps-238-edge", "name": "Edge", "brief": "Zeros in array break division approach, prefix product handles it"},
            ],
        },
        {
            "id": "ps-range-sum-query",
            "name": "Range Sum Query - Immutable",
            "brief": "LC #303 [Easy] — itertools.accumulate",
            "category": "Prefix Sum & Cumulative Logic",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "ps-303-python", "name": "Python", "brief": "itertools.accumulate for one-liner prefix sum"},
                {"id": "ps-303-real", "name": "Real-World", "brief": "Dashboard analytics (sum of metrics over any date range)"},
                {"id": "ps-303-remember", "name": "Remember", "brief": "prefix[right+1] - prefix[left], off-by-one kills you"},
                {"id": "ps-303-edge", "name": "Edge", "brief": "Single element range, full array range"},
            ],
        },
        {
            "id": "ps-contiguous-array",
            "name": "Contiguous Array",
            "brief": "LC #525 [Medium] — 0→-1 transform + prefix sum",
            "category": "Prefix Sum & Cumulative Logic",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ps-525-python", "name": "Python", "brief": "dict for first-seen index of running sum"},
                {"id": "ps-525-real", "name": "Real-World", "brief": "Network packet analysis (equal 0s and 1s = balanced traffic)"},
                {"id": "ps-525-remember", "name": "Remember", "brief": "Treat 0 as -1, reduce to 'subarray sum = 0' problem"},
                {"id": "ps-525-edge", "name": "Edge", "brief": "Entire array is the answer, store index -1 for sum 0"},
            ],
        },
        # ── PATTERN 2: TWO POINTERS ───────────────────────────────────────────
        {
            "id": "tp-3sum",
            "name": "3Sum",
            "brief": "LC #15 [Medium] — sort + two pointers",
            "category": "Two Pointers",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "tp-15-python", "name": "Python", "brief": "sort + two pointers, skip duplicates with while loops"},
                {"id": "tp-15-real", "name": "Real-World", "brief": "Chemistry (finding 3 reagents that balance to neutral pH)"},
                {"id": "tp-15-remember", "name": "Remember", "brief": "Sort first, fix one element, two-pointer on rest. Dedup at BOTH levels"},
                {"id": "tp-15-edge", "name": "Edge", "brief": "All zeros [0,0,0,0], all negatives, array with duplicates"},
            ],
        },
        {
            "id": "tp-container-most-water",
            "name": "Container With Most Water",
            "brief": "LC #11 [Medium] — move shorter pointer",
            "category": "Two Pointers",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "tp-11-python", "name": "Python", "brief": "max() with two pointers from both ends"},
                {"id": "tp-11-real", "name": "Real-World", "brief": "Warehouse shelf placement (maximize storage between two walls)"},
                {"id": "tp-11-remember", "name": "Remember", "brief": "Move the SHORTER pointer (greedy). Width decreases, so only height increase helps"},
                {"id": "tp-11-edge", "name": "Edge", "brief": "Monotonically increasing/decreasing heights"},
            ],
        },
        {
            "id": "tp-trapping-rain-water",
            "name": "Trapping Rain Water",
            "brief": "LC #42 [Hard] — two pointer with left/right max",
            "category": "Two Pointers",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "tp-42-python", "name": "Python", "brief": "Two-pointer with left_max, right_max tracking"},
                {"id": "tp-42-real", "name": "Real-World", "brief": "Terrain flooding simulation, reservoir capacity estimation"},
                {"id": "tp-42-remember", "name": "Remember", "brief": "Water at i = min(left_max, right_max) - height[i]. Two-pointer avoids O(n) space"},
                {"id": "tp-42-edge", "name": "Edge", "brief": "Flat surface (no trap), single peak, valley at edges"},
            ],
        },
        {
            "id": "tp-valid-palindrome-ii",
            "name": "Valid Palindrome II",
            "brief": "LC #680 [Easy] — try skip left OR right",
            "category": "Two Pointers",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "tp-680-python", "name": "Python", "brief": "string slicing s[i+1:j+1] or s[i:j] for skip check"},
                {"id": "tp-680-real", "name": "Real-World", "brief": "Spell-checker (allow one typo tolerance)"},
                {"id": "tp-680-remember", "name": "Remember", "brief": "On mismatch, try skipping left OR right, check both"},
                {"id": "tp-680-edge", "name": "Edge", "brief": "Already palindrome, single char, skip first or last char"},
            ],
        },
        # ── PATTERN 3: SLIDING WINDOW ─────────────────────────────────────────
        {
            "id": "sw-min-window-substring",
            "name": "Minimum Window Substring",
            "brief": "LC #76 [Hard] — expand right, shrink left",
            "category": "Sliding Window",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "sw-76-python", "name": "Python", "brief": "collections.Counter for need/have maps, expandable window"},
                {"id": "sw-76-real", "name": "Real-World", "brief": "Log search (smallest time window containing all error types)"},
                {"id": "sw-76-remember", "name": "Remember", "brief": "Expand right until valid, shrink left to minimize. Track 'formed' count"},
                {"id": "sw-76-edge", "name": "Edge", "brief": "t has duplicate chars, t longer than s, single char match"},
            ],
        },
        {
            "id": "sw-longest-no-repeat",
            "name": "Longest Substring Without Repeating Characters",
            "brief": "LC #3 [Medium] — char last-index dict",
            "category": "Sliding Window",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "sw-3-python", "name": "Python", "brief": "dict storing last index of each char, update left = max(left, last_seen+1)"},
                {"id": "sw-3-real", "name": "Real-World", "brief": "Unique session tracking (longest streak of unique page visits)"},
                {"id": "sw-3-remember", "name": "Remember", "brief": "Don't reset left backward. Use max() to only move forward"},
                {"id": "sw-3-edge", "name": "Edge", "brief": "All same chars 'aaaa', all unique 'abcdef', empty string"},
            ],
        },
        {
            "id": "sw-sliding-window-max",
            "name": "Sliding Window Maximum",
            "brief": "LC #239 [Hard] — monotonic deque of indices",
            "category": "Sliding Window",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "sw-239-python", "name": "Python", "brief": "collections.deque as monotonic decreasing deque"},
                {"id": "sw-239-real", "name": "Real-World", "brief": "Stock market (max price in rolling k-day window), sensor peak detection"},
                {"id": "sw-239-remember", "name": "Remember", "brief": "Deque stores INDICES not values. Pop from back if smaller, pop from front if out of window"},
                {"id": "sw-239-edge", "name": "Edge", "brief": "k=1 (return array itself), k=len(nums), all equal elements"},
            ],
        },
        {
            "id": "sw-longest-repeating-replacement",
            "name": "Longest Repeating Character Replacement",
            "brief": "LC #424 [Medium] — window size - max_freq <= k",
            "category": "Sliding Window",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "sw-424-python", "name": "Python", "brief": "Counter + window where len - max_freq <= k"},
                {"id": "sw-424-real", "name": "Real-World", "brief": "DNA mutation analysis (longest strand achievable with k mutations)"},
                {"id": "sw-424-remember", "name": "Remember", "brief": "Window is valid if (window_size - count_of_most_frequent) <= k. Never shrink max_freq"},
                {"id": "sw-424-edge", "name": "Edge", "brief": "k >= len(s) means whole string, all same chars already"},
            ],
        },
        # ── PATTERN 4: FAST & SLOW POINTERS ──────────────────────────────────
        {
            "id": "fs-linked-list-cycle-ii",
            "name": "Linked List Cycle II",
            "brief": "LC #142 [Medium] — Floyd's + reset to head",
            "category": "Fast & Slow Pointers",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "fs-142-python", "name": "Python", "brief": "Floyd's algorithm, after meet reset one pointer to head"},
                {"id": "fs-142-real", "name": "Real-World", "brief": "Deadlock detection in OS (resource allocation graph cycle)"},
                {"id": "fs-142-remember", "name": "Remember", "brief": "After meeting, distance from head to cycle start = distance from meet to cycle start"},
                {"id": "fs-142-edge", "name": "Edge", "brief": "No cycle, cycle at head, single node self-loop"},
            ],
        },
        {
            "id": "fs-find-duplicate",
            "name": "Find the Duplicate Number",
            "brief": "LC #287 [Medium] — array as implicit linked list",
            "category": "Fast & Slow Pointers",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "fs-287-python", "name": "Python", "brief": "Treat array as linked list, index → value as next pointer"},
                {"id": "fs-287-real", "name": "Real-World", "brief": "Database integrity check (finding duplicate primary keys)"},
                {"id": "fs-287-remember", "name": "Remember", "brief": "Floyd's on array without modifying it. nums[0] is entry point (0 is never in range)"},
                {"id": "fs-287-edge", "name": "Edge", "brief": "Duplicate appears many times, duplicate is at boundary"},
            ],
        },
        {
            "id": "fs-happy-number",
            "name": "Happy Number",
            "brief": "LC #202 [Easy] — cycle detection via fast/slow",
            "category": "Fast & Slow Pointers",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "fs-202-python", "name": "Python", "brief": "Digit sum with divmod() in a loop, or set for cycle detection"},
                {"id": "fs-202-real", "name": "Real-World", "brief": "Hashing collision detection (cycle in hash chains)"},
                {"id": "fs-202-remember", "name": "Remember", "brief": "Sum of squares either reaches 1 or enters a cycle. Fast/slow or HashSet both work"},
                {"id": "fs-202-edge", "name": "Edge", "brief": "Single digit numbers, very large numbers converge quickly"},
            ],
        },
        {
            "id": "fs-middle-linked-list",
            "name": "Middle of the Linked List",
            "brief": "LC #876 [Easy] — slow/fast pointer split",
            "category": "Fast & Slow Pointers",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "fs-876-python", "name": "Python", "brief": "slow = slow.next, fast = fast.next.next"},
                {"id": "fs-876-real", "name": "Real-World", "brief": "Load balancer (split request queue in half for two workers)"},
                {"id": "fs-876-remember", "name": "Remember", "brief": "For even length, this gives second middle. Check fast AND fast.next"},
                {"id": "fs-876-edge", "name": "Edge", "brief": "Single node, two nodes, odd vs even length"},
            ],
        },
        # ── PATTERN 5: HASHMAP & FREQUENCY COUNTING ───────────────────────────
        {
            "id": "hm-top-k-frequent",
            "name": "Top K Frequent Elements",
            "brief": "LC #347 [Medium] — bucket sort O(n)",
            "category": "Hashmap & Frequency Counting",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "hm-347-python", "name": "Python", "brief": "Counter.most_common(k) one-liner, or bucket sort O(n)"},
                {"id": "hm-347-real", "name": "Real-World", "brief": "Trending topics, top search queries, most active users"},
                {"id": "hm-347-remember", "name": "Remember", "brief": "Bucket sort beats heap: index = frequency, value = list of elements. O(n) vs O(n log k)"},
                {"id": "hm-347-edge", "name": "Edge", "brief": "All same frequency, k equals unique elements, single element"},
            ],
        },
        {
            "id": "hm-group-anagrams",
            "name": "Group Anagrams",
            "brief": "LC #49 [Medium] — sorted-tuple key",
            "category": "Hashmap & Frequency Counting",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "hm-49-python", "name": "Python", "brief": "defaultdict(list) with tuple(sorted(word)) as key, or letter count tuple"},
                {"id": "hm-49-real", "name": "Real-World", "brief": "Plagiarism detection, search engine query clustering"},
                {"id": "hm-49-remember", "name": "Remember", "brief": "sorted() key is O(k log k). Count-based tuple key is O(k) but 26-length fixed"},
                {"id": "hm-49-edge", "name": "Edge", "brief": "Empty strings group together, single char words, all same word"},
            ],
        },
        {
            "id": "hm-longest-consecutive",
            "name": "Longest Consecutive Sequence",
            "brief": "LC #128 [Medium] — set + start-of-sequence trick",
            "category": "Hashmap & Frequency Counting",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "hm-128-python", "name": "Python", "brief": "set() for O(1) lookup, only start counting from sequence START"},
                {"id": "hm-128-real", "name": "Real-World", "brief": "Gap analysis in time-series data, finding continuous uptime stretches"},
                {"id": "hm-128-remember", "name": "Remember", "brief": "Only process if (num - 1) NOT in set. This makes it O(n) not O(n²)"},
                {"id": "hm-128-edge", "name": "Edge", "brief": "Duplicates (set handles), empty array, all same number"},
            ],
        },
        {
            "id": "hm-two-sum",
            "name": "Two Sum",
            "brief": "LC #1 [Easy] — complement dict single pass",
            "category": "Hashmap & Frequency Counting",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "hm-1-python", "name": "Python", "brief": "dict for complement lookup in single pass"},
                {"id": "hm-1-real", "name": "Real-World", "brief": "Payment matching (find two transactions that sum to a target refund)"},
                {"id": "hm-1-remember", "name": "Remember", "brief": "Store {value: index}. Check complement BEFORE inserting (avoids using same element twice)"},
                {"id": "hm-1-edge", "name": "Edge", "brief": "Same element can't be used twice, negative numbers, exactly two solutions"},
            ],
        },
        # ── PATTERN 6: MONOTONIC STACK ────────────────────────────────────────
        {
            "id": "ms-daily-temperatures",
            "name": "Daily Temperatures",
            "brief": "LC #739 [Medium] — monotonic decreasing stack of indices",
            "category": "Monotonic Stack",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ms-739-python", "name": "Python", "brief": "stack stores indices, pop when current > stack top"},
                {"id": "ms-739-real", "name": "Real-World", "brief": "Weather forecasting (days until warmer), stock price alerts"},
                {"id": "ms-739-remember", "name": "Remember", "brief": "Stack holds INDICES of decreasing temps. answer[popped] = i - popped"},
                {"id": "ms-739-edge", "name": "Edge", "brief": "Monotonically increasing (empty result), monotonically decreasing (all zeros)"},
            ],
        },
        {
            "id": "ms-largest-rectangle-histogram",
            "name": "Largest Rectangle in Histogram",
            "brief": "LC #84 [Hard] — stack with sentinel -1",
            "category": "Monotonic Stack",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "ms-84-python", "name": "Python", "brief": "Stack of indices, calculate width on pop: i - stack[-1] - 1"},
                {"id": "ms-84-real", "name": "Real-World", "brief": "Maximum rectangular plot in uneven terrain, UI layout calculation"},
                {"id": "ms-84-remember", "name": "Remember", "brief": "Push -1 as sentinel. Width = i - stack[-1] - 1 (not i - popped)"},
                {"id": "ms-84-edge", "name": "Edge", "brief": "All same height, single bar, ascending order, descending order"},
            ],
        },
        {
            "id": "ms-next-greater-element",
            "name": "Next Greater Element I",
            "brief": "LC #496 [Easy] — stack + hashmap",
            "category": "Monotonic Stack",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "ms-496-python", "name": "Python", "brief": "Stack + HashMap to store next-greater mapping"},
                {"id": "ms-496-real", "name": "Real-World", "brief": "Stock next peak prediction, DNS resolution chain"},
                {"id": "ms-496-remember", "name": "Remember", "brief": "Process nums2 with stack, build map. Then look up each nums1 element"},
                {"id": "ms-496-edge", "name": "Edge", "brief": "No greater element exists (return -1), last element always -1"},
            ],
        },
        {
            "id": "ms-online-stock-span",
            "name": "Online Stock Span",
            "brief": "LC #901 [Medium] — (price, span) tuple stack",
            "category": "Monotonic Stack",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ms-901-python", "name": "Python", "brief": "Stack of (price, span) tuples, accumulate span on pop"},
                {"id": "ms-901-real", "name": "Real-World", "brief": "Literal stock span calculation, consecutive performance metrics"},
                {"id": "ms-901-remember", "name": "Remember", "brief": "Pop all smaller/equal prices, ADD their spans to current. Stack stores cumulative info"},
                {"id": "ms-901-edge", "name": "Edge", "brief": "Monotonically increasing prices (span always 1), all same price"},
            ],
        },
        # ── PATTERN 7: BINARY SEARCH (ON ANSWER) ─────────────────────────────
        {
            "id": "bs-koko-bananas",
            "name": "Koko Eating Bananas",
            "brief": "LC #875 [Medium] — binary search on answer space",
            "category": "Binary Search (On Answer)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "bs-875-python", "name": "Python", "brief": "bisect-style on answer space, math.ceil(pile/speed) for hours calc"},
                {"id": "bs-875-real", "name": "Real-World", "brief": "Resource allocation (minimum server capacity to process jobs in time)"},
                {"id": "bs-875-remember", "name": "Remember", "brief": "Search space is [1, max(piles)]. Binary search on the ANSWER, not the array"},
                {"id": "bs-875-edge", "name": "Edge", "brief": "h == len(piles) means answer is max(piles), single pile"},
            ],
        },
        {
            "id": "bs-search-rotated-array",
            "name": "Search in Rotated Sorted Array",
            "brief": "LC #33 [Medium] — identify sorted half first",
            "category": "Binary Search (On Answer)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "bs-33-python", "name": "Python", "brief": "Identify which half is sorted, then decide direction"},
                {"id": "bs-33-real", "name": "Real-World", "brief": "Searching in circular buffers, log rotation search"},
                {"id": "bs-33-remember", "name": "Remember", "brief": "One half is ALWAYS sorted. Check if target is in sorted half, else go other way"},
                {"id": "bs-33-edge", "name": "Edge", "brief": "No rotation, single element, target not present, rotation at start/end"},
            ],
        },
        {
            "id": "bs-find-min-rotated",
            "name": "Find Minimum in Rotated Sorted Array",
            "brief": "LC #153 [Medium] — compare mid with right",
            "category": "Binary Search (On Answer)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "bs-153-python", "name": "Python", "brief": "Compare mid with right (not left!) to decide direction"},
                {"id": "bs-153-real", "name": "Real-World", "brief": "Finding reset point in circular time-series data"},
                {"id": "bs-153-remember", "name": "Remember", "brief": "If nums[mid] > nums[right], min is in right half. Compare with RIGHT always"},
                {"id": "bs-153-edge", "name": "Edge", "brief": "Not rotated (first element), single element, two elements"},
            ],
        },
        {
            "id": "bs-median-two-arrays",
            "name": "Median of Two Sorted Arrays",
            "brief": "LC #4 [Hard] — binary search on shorter array partition",
            "category": "Binary Search (On Answer)",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "bs-4-python", "name": "Python", "brief": "Binary search on shorter array, partition both arrays"},
                {"id": "bs-4-real", "name": "Real-World", "brief": "Database merge-sort optimization, distributed percentile computation"},
                {"id": "bs-4-remember", "name": "Remember", "brief": "Binary search on SHORTER array. Partition so left_total = (m+n+1)//2. Check cross-boundaries"},
                {"id": "bs-4-edge", "name": "Edge", "brief": "One empty array, arrays of very different sizes, all elements same"},
            ],
        },
        # ── PATTERN 8: BACKTRACKING ───────────────────────────────────────────
        {
            "id": "bt-combination-sum",
            "name": "Combination Sum",
            "brief": "LC #39 [Medium] — recursive with reuse allowed",
            "category": "Backtracking",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "bt-39-python", "name": "Python", "brief": "Recursive with start index, append/pop pattern, allow reuse (i not i+1)"},
                {"id": "bt-39-real", "name": "Real-World", "brief": "Budget allocation (find all ways to spend exact budget on items)"},
                {"id": "bt-39-remember", "name": "Remember", "brief": "Pass same index i (reuse allowed). Sort to enable early termination when sum > target"},
                {"id": "bt-39-edge", "name": "Edge", "brief": "Single element equals target, no valid combination, very deep recursion"},
            ],
        },
        {
            "id": "bt-word-search",
            "name": "Word Search",
            "brief": "LC #79 [Medium] — DFS with in-place mark/restore",
            "category": "Backtracking",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "bt-79-python", "name": "Python", "brief": "DFS with in-place marking (board[r][c] = '#'), restore after"},
                {"id": "bt-79-real", "name": "Real-World", "brief": "Pattern matching in grids (crossword solvers, OCR character path detection)"},
                {"id": "bt-79-remember", "name": "Remember", "brief": "Mark visited IN-PLACE to save space. Restore on backtrack. Check bounds first"},
                {"id": "bt-79-edge", "name": "Edge", "brief": "Single char word, word longer than board cells, all same chars in board"},
            ],
        },
        {
            "id": "bt-n-queens",
            "name": "N-Queens",
            "brief": "LC #51 [Hard] — sets for cols, diagonals, anti-diagonals",
            "category": "Backtracking",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "bt-51-python", "name": "Python", "brief": "Sets for columns, diagonals (row-col), anti-diagonals (row+col)"},
                {"id": "bt-51-real", "name": "Real-World", "brief": "Constraint satisfaction (scheduling, resource allocation without conflicts)"},
                {"id": "bt-51-remember", "name": "Remember", "brief": "Diagonal identity: row-col is constant. Anti-diagonal: row+col is constant. Sets for O(1) check"},
                {"id": "bt-51-edge", "name": "Edge", "brief": "n=1 (trivial), n=2,3 (no solution), n=4 (two solutions)"},
            ],
        },
        {
            "id": "bt-palindrome-partitioning",
            "name": "Palindrome Partitioning",
            "brief": "LC #131 [Medium] — backtrack + DP palindrome check",
            "category": "Backtracking",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "bt-131-python", "name": "Python", "brief": "Backtrack with s[start:i+1] slicing, isPalindrome check"},
                {"id": "bt-131-real", "name": "Real-World", "brief": "Text segmentation (NLP word boundary detection with constraints)"},
                {"id": "bt-131-remember", "name": "Remember", "brief": "For each position, try all possible palindrome prefixes. Memoize palindrome checks with DP table"},
                {"id": "bt-131-edge", "name": "Edge", "brief": "All same chars (many partitions), no palindrome substring longer than 1"},
            ],
        },
        # ── PATTERN 9: BFS / DFS ON GRAPHS ───────────────────────────────────
        {
            "id": "gr-number-of-islands",
            "name": "Number of Islands",
            "brief": "LC #200 [Medium] — DFS sinking / BFS deque",
            "category": "BFS / DFS on Graphs",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr-200-python", "name": "Python", "brief": "DFS with in-place sinking (grid[r][c] = '0'), or BFS with deque"},
                {"id": "gr-200-real", "name": "Real-World", "brief": "Image blob detection, connected component analysis in maps"},
                {"id": "gr-200-remember", "name": "Remember", "brief": "Sink visited land to avoid visited set. Iterate full grid, count DFS triggers"},
                {"id": "gr-200-edge", "name": "Edge", "brief": "All water, all land (one island), diagonal doesn't count"},
            ],
        },
        {
            "id": "gr-course-schedule",
            "name": "Course Schedule",
            "brief": "LC #207 [Medium] — 3-state DFS cycle detection",
            "category": "BFS / DFS on Graphs",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr-207-python", "name": "Python", "brief": "defaultdict(list) for adjacency, DFS with 3-state coloring (unvisited, in-progress, done)"},
                {"id": "gr-207-real", "name": "Real-World", "brief": "Build system dependency resolution (make, gradle), package managers"},
                {"id": "gr-207-remember", "name": "Remember", "brief": "Cycle detection = impossible. Three states prevent revisiting done nodes. Kahn's BFS also works"},
                {"id": "gr-207-edge", "name": "Edge", "brief": "No prerequisites (always possible), self-loop, disconnected graph"},
            ],
        },
        {
            "id": "gr-word-ladder",
            "name": "Word Ladder",
            "brief": "LC #127 [Hard] — BFS shortest path with wildcard neighbors",
            "category": "BFS / DFS on Graphs",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr-127-python", "name": "Python", "brief": "BFS with deque, generate neighbors by replacing each char with a-z"},
                {"id": "gr-127-real", "name": "Real-World", "brief": "Spell-checker suggestion chains, gene mutation paths"},
                {"id": "gr-127-remember", "name": "Remember", "brief": "BFS guarantees shortest path. Use wildcard pattern dict for O(26*L) neighbor gen"},
                {"id": "gr-127-edge", "name": "Edge", "brief": "No transformation possible (return 0), endWord not in list, very long words"},
            ],
        },
        {
            "id": "gr-clone-graph",
            "name": "Clone Graph",
            "brief": "LC #133 [Medium] — DFS with old→new hashmap",
            "category": "BFS / DFS on Graphs",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr-133-python", "name": "Python", "brief": "dict {original: clone} as visited map, DFS/BFS cloning"},
                {"id": "gr-133-real", "name": "Real-World", "brief": "Deep copy of object graphs, database record duplication with references"},
                {"id": "gr-133-remember", "name": "Remember", "brief": "HashMap maps old→new node. Clone node FIRST, then recurse neighbors. Handles cycles naturally"},
                {"id": "gr-133-edge", "name": "Edge", "brief": "Empty graph, single node with self-loop, fully connected graph"},
            ],
        },
        # ── PATTERN 10: TREE TRAVERSAL & DFS ─────────────────────────────────
        {
            "id": "tr-level-order-traversal",
            "name": "Binary Tree Level Order Traversal",
            "brief": "LC #102 [Medium] — BFS with level snapshot",
            "category": "Tree Traversal & DFS",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "tr-102-python", "name": "Python", "brief": "deque BFS, process level_size = len(queue) nodes per iteration"},
                {"id": "tr-102-real", "name": "Real-World", "brief": "Org chart level display, DOM rendering layer by layer, BFS in social networks"},
                {"id": "tr-102-remember", "name": "Remember", "brief": "Key trick is snapshot len(queue) at start of each level. Append children during iteration"},
                {"id": "tr-102-edge", "name": "Edge", "brief": "Empty tree, single node, skewed tree (one node per level)"},
            ],
        },
        {
            "id": "tr-validate-bst",
            "name": "Validate Binary Search Tree",
            "brief": "LC #98 [Medium] — recursive bounds (low, high)",
            "category": "Tree Traversal & DFS",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "tr-98-python", "name": "Python", "brief": "Recursive with (low, high) bounds, or inorder should be strictly increasing"},
                {"id": "tr-98-real", "name": "Real-World", "brief": "Database index validation, ensuring B-tree property holds after mutations"},
                {"id": "tr-98-remember", "name": "Remember", "brief": "Pass bounds down: left child gets (low, node.val), right gets (node.val, high). Use float('-inf'), float('inf')"},
                {"id": "tr-98-edge", "name": "Edge", "brief": "Equal values (strictly less, not <=), single node, Integer.MIN/MAX as values"},
            ],
        },
        {
            "id": "tr-serialize-deserialize",
            "name": "Serialize and Deserialize Binary Tree",
            "brief": "LC #297 [Hard] — preorder with null markers",
            "category": "Tree Traversal & DFS",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "tr-297-python", "name": "Python", "brief": "Preorder with 'null' markers, deque for deserialization (popleft)"},
                {"id": "tr-297-real", "name": "Real-World", "brief": "Saving tree state to disk/network (JSON tree structure, AST serialization)"},
                {"id": "tr-297-remember", "name": "Remember", "brief": "Preorder + null markers = unique tree. Use deque.popleft() for O(1) consumption during deserialize"},
                {"id": "tr-297-edge", "name": "Edge", "brief": "Empty tree, all left children (skewed), complete binary tree"},
            ],
        },
        {
            "id": "tr-lowest-common-ancestor",
            "name": "Lowest Common Ancestor",
            "brief": "LC #236 [Medium] — bubble up from both sides",
            "category": "Tree Traversal & DFS",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "tr-236-python", "name": "Python", "brief": "Recursive, return node if found, bubble up from both sides"},
                {"id": "tr-236-real", "name": "Real-World", "brief": "Version control merge-base (git merge-base), taxonomy classification"},
                {"id": "tr-236-remember", "name": "Remember", "brief": "If left and right both return non-null, current node is LCA. If one is null, return the other"},
                {"id": "tr-236-edge", "name": "Edge", "brief": "One node is ancestor of other, both nodes same, root is one of the nodes"},
            ],
        },
        # ── PATTERN 11: HEAP / PRIORITY QUEUE ────────────────────────────────
        {
            "id": "hp-merge-k-sorted-lists",
            "name": "Merge K Sorted Lists",
            "brief": "LC #23 [Hard] — heapq with tie-breaker index",
            "category": "Heap / Priority Queue",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "hp-23-python", "name": "Python", "brief": "heapq with (val, index, node) tuples (index breaks ties since ListNode isn't comparable)"},
                {"id": "hp-23-real", "name": "Real-World", "brief": "Database merge-sort join, merging sorted log files from multiple servers"},
                {"id": "hp-23-remember", "name": "Remember", "brief": "Push first element of each list. Pop min, push next from same list. Tie-breaker index needed"},
                {"id": "hp-23-edge", "name": "Edge", "brief": "Empty lists in input, single list, all lists have one element"},
            ],
        },
        {
            "id": "hp-median-data-stream",
            "name": "Find Median from Data Stream",
            "brief": "LC #295 [Hard] — two heaps (max-left + min-right)",
            "category": "Heap / Priority Queue",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "hp-295-python", "name": "Python", "brief": "Two heaps: max-heap (negate for Python) for left, min-heap for right"},
                {"id": "hp-295-real", "name": "Real-World", "brief": "Real-time percentile monitoring, streaming analytics dashboards"},
                {"id": "hp-295-remember", "name": "Remember", "brief": "Balance: len(left) == len(right) or len(left) == len(right)+1. Always push to left first"},
                {"id": "hp-295-edge", "name": "Edge", "brief": "Single element, two elements, all same values, alternating large/small"},
            ],
        },
        {
            "id": "hp-task-scheduler",
            "name": "Task Scheduler",
            "brief": "LC #621 [Medium] — max-heap + cooldown queue",
            "category": "Heap / Priority Queue",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "hp-621-python", "name": "Python", "brief": "Counter + max-heap (negate), track cooldown with queue of (time_available, count)"},
                {"id": "hp-621-real", "name": "Real-World", "brief": "CPU task scheduling, rate-limited API call batching"},
                {"id": "hp-621-remember", "name": "Remember", "brief": "Most frequent task determines idle slots. Formula: (max_freq-1) * (n+1) + count_of_max_freq tasks"},
                {"id": "hp-621-edge", "name": "Edge", "brief": "n=0 (no cooldown), all same task, many tasks with same frequency"},
            ],
        },
        {
            "id": "hp-kth-largest",
            "name": "Kth Largest Element in an Array",
            "brief": "LC #215 [Medium] — min-heap of size k / quickselect",
            "category": "Heap / Priority Queue",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "hp-215-python", "name": "Python", "brief": "heapq.nlargest(k, nums)[-1], or min-heap of size k, or quickselect"},
                {"id": "hp-215-real", "name": "Real-World", "brief": "Top-K leaderboard, finding percentile cutoffs in real-time"},
                {"id": "hp-215-remember", "name": "Remember", "brief": "Min-heap of size k: push all, pop when size > k. Top of heap = kth largest. O(n log k)"},
                {"id": "hp-215-edge", "name": "Edge", "brief": "k=1 (max), k=n (min), duplicates in array, all same elements"},
            ],
        },
        # ── PATTERN 12: DYNAMIC PROGRAMMING (1D) ─────────────────────────────
        {
            "id": "dp1-house-robber",
            "name": "House Robber",
            "brief": "LC #198 [Medium] — dp[i] = max(dp[i-1], dp[i-2]+nums[i])",
            "category": "Dynamic Programming (1D)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp1-198-python", "name": "Python", "brief": "dp[i] = max(dp[i-1], dp[i-2] + nums[i]), space-optimize to two vars"},
                {"id": "dp1-198-real", "name": "Real-World", "brief": "Resource selection with exclusion constraints, ad placement with spacing rules"},
                {"id": "dp1-198-remember", "name": "Remember", "brief": "Choice at each step: skip or take+skip_previous. Two variables (prev1, prev2) replace array"},
                {"id": "dp1-198-edge", "name": "Edge", "brief": "Single house, two houses, all same values, alternating high/low"},
            ],
        },
        {
            "id": "dp1-lis",
            "name": "Longest Increasing Subsequence",
            "brief": "LC #300 [Medium] — bisect_left on tails array O(n log n)",
            "category": "Dynamic Programming (1D)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp1-300-python", "name": "Python", "brief": "bisect.bisect_left on tails array for O(n log n), or dp[i] = LIS ending at i"},
                {"id": "dp1-300-real", "name": "Real-World", "brief": "Stock trend analysis (longest uptrend), version dependency resolution"},
                {"id": "dp1-300-remember", "name": "Remember", "brief": "Patience sorting: maintain smallest tail for each length. bisect_left finds insertion point"},
                {"id": "dp1-300-edge", "name": "Edge", "brief": "Strictly increasing (LIS = n), strictly decreasing (LIS = 1), all equal"},
            ],
        },
        {
            "id": "dp1-coin-change",
            "name": "Coin Change",
            "brief": "LC #322 [Medium] — bottom-up dp[i] = min coins",
            "category": "Dynamic Programming (1D)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp1-322-python", "name": "Python", "brief": "dp = [float('inf')] * (amount+1), dp[0] = 0, iterate coins for each amount"},
                {"id": "dp1-322-real", "name": "Real-World", "brief": "Making change (literally), minimum resource allocation, minimum API calls"},
                {"id": "dp1-322-remember", "name": "Remember", "brief": "Bottom-up: dp[i] = min(dp[i], dp[i-coin]+1) for all coins. Check dp[amount] != inf"},
                {"id": "dp1-322-edge", "name": "Edge", "brief": "Amount 0 (return 0), impossible (return -1), single coin, amount < smallest coin"},
            ],
        },
        {
            "id": "dp1-decode-ways",
            "name": "Decode Ways",
            "brief": "LC #91 [Medium] — dp depends on 1-digit & 2-digit",
            "category": "Dynamic Programming (1D)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp1-91-python", "name": "Python", "brief": "dp[i] depends on single digit (1-9) and double digit (10-26)"},
                {"id": "dp1-91-real", "name": "Real-World", "brief": "Text encoding/decoding ambiguity, parser state machines"},
                {"id": "dp1-91-remember", "name": "Remember", "brief": "'0' alone is invalid. Leading zeros kill paths. Check both s[i] and s[i-1:i+1]"},
                {"id": "dp1-91-edge", "name": "Edge", "brief": "Leading zero '0...', '10' vs '01', consecutive zeros, '00'"},
            ],
        },
        # ── PATTERN 13: DYNAMIC PROGRAMMING (2D) ─────────────────────────────
        {
            "id": "dp2-lcs",
            "name": "Longest Common Subsequence",
            "brief": "LC #1143 [Medium] — 2D dp, space-optimized to two rows",
            "category": "Dynamic Programming (2D)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp2-1143-python", "name": "Python", "brief": "2D dp, space-optimize to two rows. dp[i][j] = dp[i-1][j-1]+1 if match"},
                {"id": "dp2-1143-real", "name": "Real-World", "brief": "Diff tools (git diff), DNA sequence alignment, spell-check suggestions"},
                {"id": "dp2-1143-remember", "name": "Remember", "brief": "Match → diagonal+1. No match → max(left, top). Space optimization: only need previous row"},
                {"id": "dp2-1143-edge", "name": "Edge", "brief": "No common chars (LCS=0), one is substring of other, identical strings"},
            ],
        },
        {
            "id": "dp2-edit-distance",
            "name": "Edit Distance",
            "brief": "LC #72 [Hard] — insert / delete / replace DP",
            "category": "Dynamic Programming (2D)",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp2-72-python", "name": "Python", "brief": "dp[i][j] = operations to convert word1[:i] to word2[:j]. Three choices: insert, delete, replace"},
                {"id": "dp2-72-real", "name": "Real-World", "brief": "Spell checker ranking, DNA mutation distance, fuzzy string matching"},
                {"id": "dp2-72-remember", "name": "Remember", "brief": "Match = dp[i-1][j-1]. Else: 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]). Base cases = indices"},
                {"id": "dp2-72-edge", "name": "Edge", "brief": "One empty string (answer = len of other), identical strings (0), completely different"},
            ],
        },
        {
            "id": "dp2-unique-paths",
            "name": "Unique Paths",
            "brief": "LC #62 [Medium] — dp or math.comb one-liner",
            "category": "Dynamic Programming (2D)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp2-62-python", "name": "Python", "brief": "dp[i][j] = dp[i-1][j] + dp[i][j-1], or math.comb(m+n-2, m-1) one-liner"},
                {"id": "dp2-62-real", "name": "Real-World", "brief": "Robot navigation, grid-based routing, network packet path counting"},
                {"id": "dp2-62-remember", "name": "Remember", "brief": "Combinatorics shortcut: C(m+n-2, m-1). DP if obstacles exist (LC #63)"},
                {"id": "dp2-62-edge", "name": "Edge", "brief": "1xn or mx1 grid (only one path), large grids (overflow in some languages, not Python)"},
            ],
        },
        {
            "id": "dp2-burst-balloons",
            "name": "Burst Balloons",
            "brief": "LC #312 [Hard] — interval DP, think LAST balloon to burst",
            "category": "Dynamic Programming (2D)",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "dp2-312-python", "name": "Python", "brief": "Interval DP. dp[l][r] = max coins from bursting all balloons between l and r"},
                {"id": "dp2-312-real", "name": "Real-World", "brief": "Optimal job sequencing with neighbor-dependent rewards, game theory"},
                {"id": "dp2-312-remember", "name": "Remember", "brief": "Think of LAST balloon to burst in range (not first). Multiply with boundaries nums[l-1]*nums[k]*nums[r+1]"},
                {"id": "dp2-312-edge", "name": "Edge", "brief": "Single balloon, two balloons, padding with 1s at boundaries"},
            ],
        },
        # ── PATTERN 14: GREEDY ────────────────────────────────────────────────
        {
            "id": "gr2-jump-game",
            "name": "Jump Game",
            "brief": "LC #55 [Medium] — track farthest reachable index",
            "category": "Greedy",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr2-55-python", "name": "Python", "brief": "Track farthest reachable index, iterate and update"},
                {"id": "gr2-55-real", "name": "Real-World", "brief": "Network hop analysis (can packet reach destination?), game level feasibility"},
                {"id": "gr2-55-remember", "name": "Remember", "brief": "At each index, farthest = max(farthest, i + nums[i]). If i > farthest, unreachable"},
                {"id": "gr2-55-edge", "name": "Edge", "brief": "Single element (always true), first element is 0 (false unless n=1), all 1s"},
            ],
        },
        {
            "id": "gr2-partition-labels",
            "name": "Partition Labels",
            "brief": "LC #763 [Medium] — last-occurrence greedy expansion",
            "category": "Greedy",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr2-763-python", "name": "Python", "brief": "dict for last occurrence of each char, expand partition end greedily"},
                {"id": "gr2-763-real", "name": "Real-World", "brief": "Log file splitting (ensure each log type stays in one partition), data sharding"},
                {"id": "gr2-763-remember", "name": "Remember", "brief": "Track last occurrence of every char. Expand current partition end to max(end, last[char])"},
                {"id": "gr2-763-edge", "name": "Edge", "brief": "All unique chars (each is own partition), single char repeated (one partition)"},
            ],
        },
        {
            "id": "gr2-gas-station",
            "name": "Gas Station",
            "brief": "LC #134 [Medium] — reset start on deficit, total >= 0 = solvable",
            "category": "Greedy",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr2-134-python", "name": "Python", "brief": "If total gas >= total cost, solution exists. Track running surplus, reset start on deficit"},
                {"id": "gr2-134-real", "name": "Real-World", "brief": "Vehicle routing with refueling, circular delivery optimization"},
                {"id": "gr2-134-remember", "name": "Remember", "brief": "If total >= 0, answer exists and is UNIQUE. Reset start when tank goes negative"},
                {"id": "gr2-134-edge", "name": "Edge", "brief": "All stations same gas/cost, only one valid start, impossible (total < 0)"},
            ],
        },
        {
            "id": "gr2-meeting-rooms-ii",
            "name": "Meeting Rooms II",
            "brief": "LC #253 [Medium] — sorted start/end two-pointer or heap",
            "category": "Greedy",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "gr2-253-python", "name": "Python", "brief": "Sort starts and ends separately, two-pointer to count overlaps. Or heapq for end times"},
                {"id": "gr2-253-real", "name": "Real-World", "brief": "Conference room scheduling, server connection pool sizing, parallel job slots"},
                {"id": "gr2-253-remember", "name": "Remember", "brief": "Sort start[] and end[] separately. If start[i] < end[j], need new room. Else reuse (j++)"},
                {"id": "gr2-253-edge", "name": "Edge", "brief": "No overlaps (1 room), all overlap (n rooms), meetings with zero duration"},
            ],
        },
        # ── PATTERN 15: INTERVALS ─────────────────────────────────────────────
        {
            "id": "iv-merge-intervals",
            "name": "Merge Intervals",
            "brief": "LC #56 [Medium] — sort by start, merge on overlap",
            "category": "Intervals",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "iv-56-python", "name": "Python", "brief": "Sort by start, compare current.start with last_merged.end"},
                {"id": "iv-56-real", "name": "Real-World", "brief": "Calendar merge (free/busy), IP range consolidation, time-series compression"},
                {"id": "iv-56-remember", "name": "Remember", "brief": "Sort by start. If overlap: merged[-1][1] = max(merged[-1][1], current[1]). Else append"},
                {"id": "iv-56-edge", "name": "Edge", "brief": "Single interval, all overlapping (merge to one), already sorted, touching boundaries [1,2][2,3]"},
            ],
        },
        {
            "id": "iv-non-overlapping-intervals",
            "name": "Non-Overlapping Intervals",
            "brief": "LC #435 [Medium] — sort by END time, count removals",
            "category": "Intervals",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "iv-435-python", "name": "Python", "brief": "Sort by END time (greedy), count conflicts"},
                {"id": "iv-435-real", "name": "Real-World", "brief": "Job scheduling (maximize non-conflicting jobs), TV show recording conflicts"},
                {"id": "iv-435-remember", "name": "Remember", "brief": "Sort by END (not start!). Greedy: keep interval that ends earliest. Count removals"},
                {"id": "iv-435-edge", "name": "Edge", "brief": "No overlaps (remove 0), all same interval (remove n-1), nested intervals"},
            ],
        },
        {
            "id": "iv-insert-interval",
            "name": "Insert Interval",
            "brief": "LC #57 [Medium] — three-phase: before / merge / after",
            "category": "Intervals",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "iv-57-python", "name": "Python", "brief": "Three phases: before (end < new_start), merge (overlap), after (start > new_end)"},
                {"id": "iv-57-real", "name": "Real-World", "brief": "Calendar event insertion, range-based access control updates"},
                {"id": "iv-57-remember", "name": "Remember", "brief": "Collect all non-overlapping before, merge all overlapping, collect all after. Clean 3-pass logic"},
                {"id": "iv-57-edge", "name": "Edge", "brief": "Insert at beginning, insert at end, new interval covers all existing"},
            ],
        },
        {
            "id": "iv-car-pooling",
            "name": "Car Pooling",
            "brief": "LC #1094 [Medium] — difference array / sweep line",
            "category": "Intervals",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "iv-1094-python", "name": "Python", "brief": "Difference array / sweep line. Mark +passengers at start, -passengers at end"},
                {"id": "iv-1094-real", "name": "Real-World", "brief": "Literal carpooling, elevator capacity, bandwidth allocation over time"},
                {"id": "iv-1094-remember", "name": "Remember", "brief": "Sweep line: at each point sum active passengers. array[start] += p, array[end] -= p"},
                {"id": "iv-1094-edge", "name": "Edge", "brief": "All same pickup/drop, capacity exactly met, trips are sorted vs unsorted"},
            ],
        },
        # ── PATTERN 16: TRIE (PREFIX TREE) ───────────────────────────────────
        {
            "id": "ti-implement-trie",
            "name": "Implement Trie",
            "brief": "LC #208 [Medium] — TrieNode with children dict + is_end",
            "category": "Trie (Prefix Tree)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ti-208-python", "name": "Python", "brief": "Nested defaultdict or class TrieNode with children dict + is_end flag"},
                {"id": "ti-208-real", "name": "Real-World", "brief": "Autocomplete engines, spell checkers, IP routing tables (longest prefix match)"},
                {"id": "ti-208-remember", "name": "Remember", "brief": "Each node has children dict (char → TrieNode) and is_end boolean. Insert/search/startsWith"},
                {"id": "ti-208-edge", "name": "Edge", "brief": "Empty string insertion, prefix is also a word, single character words"},
            ],
        },
        {
            "id": "ti-word-search-ii",
            "name": "Word Search II",
            "brief": "LC #212 [Hard] — Trie + backtracking with pruning",
            "category": "Trie (Prefix Tree)",
            "difficulty": "Hard",
            "prerequisites": [],
            "subtopics": [
                {"id": "ti-212-python", "name": "Python", "brief": "Build Trie from words, DFS on board with Trie pruning. Remove word from Trie after found"},
                {"id": "ti-212-real", "name": "Real-World", "brief": "Multi-keyword search in documents, content moderation (banned word detection)"},
                {"id": "ti-212-remember", "name": "Remember", "brief": "Trie + backtracking on grid. Prune: delete leaf nodes after finding word. Mark visited in-place"},
                {"id": "ti-212-edge", "name": "Edge", "brief": "Same word found multiple paths (only add once), overlapping words, board smaller than word"},
            ],
        },
        {
            "id": "ti-add-search-words",
            "name": "Design Add and Search Words",
            "brief": "LC #211 [Medium] — Trie with DFS for '.' wildcard",
            "category": "Trie (Prefix Tree)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ti-211-python", "name": "Python", "brief": "Trie with DFS for '.' wildcard (try all children at that level)"},
                {"id": "ti-211-real", "name": "Real-World", "brief": "Regex-lite matching, wildcard DNS resolution, pattern-based log search"},
                {"id": "ti-211-remember", "name": "Remember", "brief": "'.' means branch to ALL children at current level. Recursive DFS for each wildcard position"},
                {"id": "ti-211-edge", "name": "Edge", "brief": "All dots '...' (match any word of that length), dot at end, no matching word"},
            ],
        },
        {
            "id": "ti-replace-words",
            "name": "Replace Words",
            "brief": "LC #648 [Medium] — Trie shortest-prefix replacement",
            "category": "Trie (Prefix Tree)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ti-648-python", "name": "Python", "brief": "Build Trie from roots, for each word find shortest prefix in Trie"},
                {"id": "ti-648-real", "name": "Real-World", "brief": "Text summarization (replace long words with abbreviations), stemming in NLP"},
                {"id": "ti-648-remember", "name": "Remember", "brief": "Walk each word char by char through Trie. First is_end found = shortest root. Replace and stop"},
                {"id": "ti-648-edge", "name": "Edge", "brief": "Word has no root (keep original), multiple roots match (shortest wins), root equals full word"},
            ],
        },
        # ── PATTERN 17: UNION-FIND ────────────────────────────────────────────
        {
            "id": "uf-accounts-merge",
            "name": "Accounts Merge",
            "brief": "LC #721 [Medium] — Union-Find on emails",
            "category": "Union-Find (Disjoint Set)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "uf-721-python", "name": "Python", "brief": "Union-Find with email → owner mapping, group by root at end"},
                {"id": "uf-721-real", "name": "Real-World", "brief": "User identity resolution (merge accounts across platforms), entity deduplication"},
                {"id": "uf-721-remember", "name": "Remember", "brief": "Union emails that share an account. Group all emails by find(root). Sort each group"},
                {"id": "uf-721-edge", "name": "Edge", "brief": "Same email in multiple accounts, single email accounts, no merging needed"},
            ],
        },
        {
            "id": "uf-redundant-connection",
            "name": "Redundant Connection",
            "brief": "LC #684 [Medium] — first edge where find(u)==find(v)",
            "category": "Union-Find (Disjoint Set)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "uf-684-python", "name": "Python", "brief": "Union-Find, first edge where find(u) == find(v) before union is the answer"},
                {"id": "uf-684-real", "name": "Real-World", "brief": "Network loop detection, removing redundant connections to form spanning tree"},
                {"id": "uf-684-remember", "name": "Remember", "brief": "Process edges in order. If u and v already connected (same root), this edge creates cycle"},
                {"id": "uf-684-edge", "name": "Edge", "brief": "Tree with exactly one extra edge (guaranteed), edge at the beginning vs end"},
            ],
        },
        {
            "id": "uf-connected-components",
            "name": "Number of Connected Components",
            "brief": "LC #323 [Medium] — n - successful_unions",
            "category": "Union-Find (Disjoint Set)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "uf-323-python", "name": "Python", "brief": "Union-Find with rank, count components = n - successful_unions"},
                {"id": "uf-323-real", "name": "Real-World", "brief": "Social network clustering, network segmentation analysis"},
                {"id": "uf-323-remember", "name": "Remember", "brief": "Start with n components. Each successful union reduces by 1. Or: count unique roots at end"},
                {"id": "uf-323-edge", "name": "Edge", "brief": "Fully connected (1 component), no edges (n components), self-loops"},
            ],
        },
        {
            "id": "uf-graph-valid-tree",
            "name": "Graph Valid Tree",
            "brief": "LC #261 [Medium] — n-1 edges + fully connected",
            "category": "Union-Find (Disjoint Set)",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "uf-261-python", "name": "Python", "brief": "Valid tree = connected + no cycles = (n-1 edges + all connected via Union-Find)"},
                {"id": "uf-261-real", "name": "Real-World", "brief": "Validating hierarchy structures, checking acyclic dependency graphs"},
                {"id": "uf-261-remember", "name": "Remember", "brief": "Tree conditions: exactly n-1 edges AND fully connected. Union-Find detects cycles during edge processing"},
                {"id": "uf-261-edge", "name": "Edge", "brief": "Empty graph (n=1 is valid), disconnected components, extra edges"},
            ],
        },
        # ── PATTERN 18: BIT MANIPULATION ─────────────────────────────────────
        {
            "id": "bm-single-number",
            "name": "Single Number",
            "brief": "LC #136 [Easy] — XOR all elements",
            "category": "Bit Manipulation",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "bm-136-python", "name": "Python", "brief": "functools.reduce(operator.xor, nums) one-liner"},
                {"id": "bm-136-real", "name": "Real-World", "brief": "Error detection (parity bits), finding corrupted packet in duplicate stream"},
                {"id": "bm-136-remember", "name": "Remember", "brief": "XOR properties: a^a=0, a^0=a, commutative+associative. All pairs cancel out"},
                {"id": "bm-136-edge", "name": "Edge", "brief": "Single element array, large numbers, negative numbers (XOR still works in Python)"},
            ],
        },
        {
            "id": "bm-counting-bits",
            "name": "Counting Bits",
            "brief": "LC #338 [Easy] — dp[i] = dp[i>>1] + (i&1)",
            "category": "Bit Manipulation",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "bm-338-python", "name": "Python", "brief": "dp[i] = dp[i >> 1] + (i & 1), or dp[i] = dp[i & (i-1)] + 1"},
                {"id": "bm-338-real", "name": "Real-World", "brief": "Hamming weight tables in networking, population count for SIMD operations"},
                {"id": "bm-338-remember", "name": "Remember", "brief": "Relationship: i's bit count = (i//2)'s count + last bit. Build table bottom-up O(n)"},
                {"id": "bm-338-edge", "name": "Edge", "brief": "n=0 (just [0]), powers of 2 (exactly 1 bit), n=1"},
            ],
        },
        {
            "id": "bm-reverse-bits",
            "name": "Reverse Bits",
            "brief": "LC #190 [Easy] — 32-iteration LSB extract & shift",
            "category": "Bit Manipulation",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "bm-190-python", "name": "Python", "brief": "Bit-by-bit: result = (result << 1) | (n & 1); n >>= 1 for 32 iterations"},
                {"id": "bm-190-real", "name": "Real-World", "brief": "Network byte order conversion (endianness), cryptographic bit permutations"},
                {"id": "bm-190-remember", "name": "Remember", "brief": "Extract LSB with n&1, shift result left, OR it in. Do exactly 32 times (fixed width)"},
                {"id": "bm-190-edge", "name": "Edge", "brief": "All zeros, all ones, alternating bits"},
            ],
        },
        {
            "id": "bm-missing-number",
            "name": "Missing Number",
            "brief": "LC #268 [Easy] — XOR or math: n*(n+1)//2 - sum",
            "category": "Bit Manipulation",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "bm-268-python", "name": "Python", "brief": "XOR all indices AND all values, or math: n*(n+1)//2 - sum(nums)"},
                {"id": "bm-268-real", "name": "Real-World", "brief": "Data integrity check (detect missing packet in sequence), census gap detection"},
                {"id": "bm-268-remember", "name": "Remember", "brief": "XOR approach: xor(0..n) ^ xor(nums) = missing. Math approach: expected_sum - actual_sum"},
                {"id": "bm-268-edge", "name": "Edge", "brief": "Missing 0, missing n (last), single element [0] or [1]"},
            ],
        },
        # ── PATTERN 19: LINKED LIST MANIPULATION ─────────────────────────────
        {
            "id": "ll-reverse-linked-list",
            "name": "Reverse Linked List",
            "brief": "LC #206 [Easy] — iterative prev/curr/next trio",
            "category": "Linked List Manipulation",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "ll-206-python", "name": "Python", "brief": "Iterative with prev/curr/next trio, or recursive (head.next.next = head)"},
                {"id": "ll-206-real", "name": "Real-World", "brief": "Undo stack implementation, reversing transaction chain"},
                {"id": "ll-206-remember", "name": "Remember", "brief": "Save next, point curr to prev, advance. Three pointers always. Don't lose reference to next"},
                {"id": "ll-206-edge", "name": "Edge", "brief": "Empty list, single node, two nodes"},
            ],
        },
        {
            "id": "ll-lru-cache",
            "name": "LRU Cache",
            "brief": "LC #146 [Medium] — OrderedDict or HashMap + doubly linked list",
            "category": "Linked List Manipulation",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ll-146-python", "name": "Python", "brief": "collections.OrderedDict with move_to_end(), or HashMap + doubly linked list"},
                {"id": "ll-146-real", "name": "Real-World", "brief": "Browser cache, database query cache, CPU cache eviction"},
                {"id": "ll-146-remember", "name": "Remember", "brief": "OrderedDict.move_to_end(key) on get, popitem(last=False) on evict. O(1) everything"},
                {"id": "ll-146-edge", "name": "Edge", "brief": "Capacity 1, get non-existent key, put existing key (update, don't evict)"},
            ],
        },
        {
            "id": "ll-merge-two-sorted-lists",
            "name": "Merge Two Sorted Lists",
            "brief": "LC #21 [Easy] — dummy head, link smaller, attach remainder",
            "category": "Linked List Manipulation",
            "difficulty": "Easy",
            "prerequisites": [],
            "subtopics": [
                {"id": "ll-21-python", "name": "Python", "brief": "Dummy head node, compare and link smaller, attach remainder"},
                {"id": "ll-21-real", "name": "Real-World", "brief": "Merge sort merge step, combining sorted search results from multiple shards"},
                {"id": "ll-21-remember", "name": "Remember", "brief": "dummy = ListNode(0), tail pointer advances. At end, attach whichever list remains"},
                {"id": "ll-21-edge", "name": "Edge", "brief": "One empty list, both empty, all elements from one list come first"},
            ],
        },
        {
            "id": "ll-reorder-list",
            "name": "Reorder List",
            "brief": "LC #143 [Medium] — split + reverse second half + interleave",
            "category": "Linked List Manipulation",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "ll-143-python", "name": "Python", "brief": "Find middle (fast/slow) → reverse second half → merge alternating"},
                {"id": "ll-143-real", "name": "Real-World", "brief": "Memory-efficient interleaving, playlist shuffle (alternating new/old)"},
                {"id": "ll-143-remember", "name": "Remember", "brief": "Three steps: (1) split at middle, (2) reverse second half, (3) interleave merge. Modify in-place"},
                {"id": "ll-143-edge", "name": "Edge", "brief": "Single node, two nodes, odd vs even length"},
            ],
        },
        # ── PATTERN 20: MATRIX / 2D TRAVERSAL ────────────────────────────────
        {
            "id": "mx-rotate-image",
            "name": "Rotate Image",
            "brief": "LC #48 [Medium] — transpose then reverse rows",
            "category": "Matrix / 2D Traversal",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "mx-48-python", "name": "Python", "brief": "Transpose (swap matrix[i][j] with matrix[j][i]) then reverse each row"},
                {"id": "mx-48-real", "name": "Real-World", "brief": "Image rotation in CV, game board rotation, screen orientation change"},
                {"id": "mx-48-remember", "name": "Remember", "brief": "90 clockwise = transpose + reverse rows. 90 counter-clockwise = transpose + reverse columns"},
                {"id": "mx-48-edge", "name": "Edge", "brief": "1x1 matrix, 2x2 matrix, non-square (can't rotate in-place)"},
            ],
        },
        {
            "id": "mx-spiral-matrix",
            "name": "Spiral Matrix",
            "brief": "LC #54 [Medium] — four shrinking boundaries",
            "category": "Matrix / 2D Traversal",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "mx-54-python", "name": "Python", "brief": "Four boundaries (top, bottom, left, right), shrink after each direction"},
                {"id": "mx-54-real", "name": "Real-World", "brief": "Printer rasterization, CNC machine path, snake game board traversal"},
                {"id": "mx-54-remember", "name": "Remember", "brief": "Go right→down→left→up, shrink boundary after each. Check boundary still valid after each shrink"},
                {"id": "mx-54-edge", "name": "Edge", "brief": "Single row, single column, 1x1, non-square matrix"},
            ],
        },
        {
            "id": "mx-set-matrix-zeroes",
            "name": "Set Matrix Zeroes",
            "brief": "LC #73 [Medium] — use first row/col as markers",
            "category": "Matrix / 2D Traversal",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "mx-73-python", "name": "Python", "brief": "Use first row/col as markers, separate flag for row0/col0"},
                {"id": "mx-73-real", "name": "Real-World", "brief": "Spreadsheet formula propagation (zeroing dependent cells), game of life neighbor marking"},
                {"id": "mx-73-remember", "name": "Remember", "brief": "O(1) space: first row/col store which rows/cols to zero. Process non-first row/col first on cleanup"},
                {"id": "mx-73-edge", "name": "Edge", "brief": "No zeros, entire matrix zeros, zeros only in first row/col"},
            ],
        },
        {
            "id": "mx-search-2d-matrix",
            "name": "Search a 2D Matrix",
            "brief": "LC #74 [Medium] — treat as 1D sorted array",
            "category": "Matrix / 2D Traversal",
            "difficulty": "Medium",
            "prerequisites": [],
            "subtopics": [
                {"id": "mx-74-python", "name": "Python", "brief": "Treat as 1D sorted array. index → row = mid//cols, col = mid%cols"},
                {"id": "mx-74-real", "name": "Real-World", "brief": "Searching in paginated sorted data, matrix-stored sorted databases"},
                {"id": "mx-74-remember", "name": "Remember", "brief": "Virtual 1D index mapping: row = mid // n, col = mid % n. Standard binary search"},
                {"id": "mx-74-edge", "name": "Edge", "brief": "Single row, single column, target smaller/larger than all elements"},
            ],
        },
    ]

    for topic in seed_data:
        cursor.execute(
            """
            INSERT OR IGNORE INTO dsa_topics (
                id, name, brief, category, difficulty, prerequisites_json, subtopics_json, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                topic["id"],
                topic["name"],
                topic["brief"],
                topic["category"],
                topic["difficulty"],
                json.dumps(topic.get("prerequisites", [])),
                json.dumps(topic.get("subtopics", [])),
            )
        )

def fetch_dsa_topics() -> list:
    import json
    from interview_ninja.db import get_db_path # avoid cyclic or global issues if any, but get_db_path is defined
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, brief, category, difficulty, prerequisites_json, subtopics_json, is_custom
            FROM dsa_topics
            ORDER BY is_custom ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        topics = []
        for r in rows:
            topics.append({
                "id": r[0],
                "name": r[1],
                "brief": r[2],
                "category": r[3],
                "difficulty": r[4],
                "prerequisites": json.loads(r[5]),
                "subtopics": json.loads(r[6]),
                "isCustom": bool(r[7]),
            })
        return topics
    finally:
        conn.close()

def save_dsa_topic(payload: dict) -> None:
    import json
    from interview_ninja.db import get_db_path
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        
        prereqs_str = json.dumps(payload.get("prerequisites", []))
        subtopics_str = json.dumps(payload.get("subtopics", []))
        
        cursor.execute(
            """
            INSERT INTO dsa_topics (
                id, name, brief, category, difficulty, prerequisites_json, subtopics_json, is_custom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                brief=excluded.brief,
                category=excluded.category,
                difficulty=excluded.difficulty,
                prerequisites_json=excluded.prerequisites_json,
                subtopics_json=excluded.subtopics_json,
                is_custom=COALESCE((SELECT is_custom FROM dsa_topics WHERE id=excluded.id), 1)
            """,
            (
                payload["id"],
                payload["name"],
                payload["brief"],
                payload["category"],
                payload["difficulty"],
                prereqs_str,
                subtopics_str,
            )
        )
        conn.commit()
    finally:
        conn.close()
