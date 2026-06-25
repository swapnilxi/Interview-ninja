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
        
        seed_system_design_topics(cursor)
        seed_cv_topics(cursor)
        
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
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

