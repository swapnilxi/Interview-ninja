'use client';

import { useState } from 'react';
import Icon from '@/components/ui/AppIcon';
import LabCopilot from '@/components/common/LabCopilot';
import OnDemandSection from '@/components/lab/OnDemandSection';
import QuizCarousel from '@/components/lab/QuizCarousel';

interface SDTopic {
  id: string; name: string; brief: string; category: string;
  scale: string;
  subtopics: { id: string; name: string; brief: string }[];
}
interface SectionState { generated: boolean; generating: boolean; content: string }

const TOPICS: SDTopic[] = [
  {
    id: 'url-shortener', name: 'URL Shortener (TinyURL)', brief: 'Design a scalable URL shortening service like bit.ly.', category: 'Storage & Hashing', scale: '100M URLs/day',
    subtopics: [
      { id: 'url-lld', name: 'LLD: Short URL Generation Strategies', brief: 'Hash vs base62 vs counter-based approaches.' },
      { id: 'url-analytics', name: 'Analytics Extension', brief: 'Click tracking with time-series storage.' },
    ],
  },
  {
    id: 'rate-limiter', name: 'Rate Limiter', brief: 'Design a distributed rate limiter for API protection.', category: 'Distributed Systems', scale: '1M RPS',
    subtopics: [
      { id: 'token-bucket', name: 'Token Bucket Algorithm', brief: 'Burst-friendly rate limiting algorithm.' },
      { id: 'sliding-window-rl', name: 'Sliding Window Counter', brief: 'Precise rate limiting with Redis sorted sets.' },
    ],
  },
  {
    id: 'news-feed', name: 'News Feed (Facebook/Twitter)', brief: 'Design a social media feed for millions of users.', category: 'Social Systems', scale: '1B users, 100k posts/sec',
    subtopics: [
      { id: 'fanout', name: 'Fanout On Write vs On Read', brief: 'Push vs pull model trade-offs.' },
      { id: 'ranking', name: 'Feed Ranking Algorithm', brief: 'Relevance scoring and personalization.' },
    ],
  },
  {
    id: 'key-value-store', name: 'Distributed Key-Value Store', brief: 'Design a distributed KV store like DynamoDB or Redis.', category: 'Storage Systems', scale: 'Petabyte scale',
    subtopics: [
      { id: 'consistent-hashing', name: 'Consistent Hashing', brief: 'Distributing keys with minimal remapping.' },
      { id: 'replication', name: 'Replication & Consensus (Raft)', brief: 'Leader election and log replication.' },
    ],
  },
  {
    id: 'search-engine', name: 'Search Engine (Google)', brief: 'Design a web-scale search engine with ranking.', category: 'Search & Indexing', scale: '8.5B searches/day',
    subtopics: [
      { id: 'inverted-index', name: 'Inverted Index Construction', brief: 'MapReduce-based indexing pipeline.' },
      { id: 'pagerank', name: 'PageRank & Link Analysis', brief: 'Graph-based authority scoring.' },
    ],
  },
  {
    id: 'video-streaming', name: 'Video Streaming (Netflix/YouTube)', brief: 'Design a global video streaming platform.', category: 'Media Systems', scale: '250M concurrent users',
    subtopics: [
      { id: 'adaptive-streaming', name: 'Adaptive Bitrate Streaming', brief: 'HLS/DASH quality adaptation algorithms.' },
      { id: 'cdn-design', name: 'CDN Architecture', brief: 'Edge caching and PoP selection strategy.' },
    ],
  },
];

function getContent(sectionId: string, topic: SDTopic): string {
  const name = topic.name;

  const templates: Record<string, string> = {
    problem: `**Problem Statement: ${name}**\n\n**Why this matters:**\nThis system is at the core of modern digital infrastructure. Getting the design right is the difference between a system that serves millions and one that falls over under load.\n\n**The core challenge:**\n${topic.brief}\n\n**What makes this hard:**\n1. Scale: ${topic.scale}\n2. Reliability: Users expect 99.99%+ uptime\n3. Consistency vs Availability trade-offs under network partitions\n4. Cost: Compute and storage at this scale is expensive\n\n**Interview context:**\nThis is a favourite at FAANG because it tests: system thinking, knowledge of distributed systems, ability to make and justify trade-offs, and practical engineering experience.`,

    requirements: `**Requirements for ${name}**\n\n**Functional Requirements (what the system must DO):**\n1. Core feature: primary use case, end-to-end\n2. CRUD operations: create, read, update, delete as applicable\n3. Search/query capabilities if needed\n4. User authentication and authorisation\n5. Notifications/webhooks for async events\n\n**Non-Functional Requirements (how well it must do it):**\n| Requirement | Target | Notes |\n|---|---|---|\n| Latency | < 100ms p99 | End-to-end for read |\n| Availability | 99.99% | 52min downtime/year |\n| Consistency | Eventual | Tolerate staleness < 1s |\n| Scale | ${topic.scale} | Peak traffic |\n| Durability | 99.999999999% | 11 nines for data |\n\n**What to clarify in interview:**\n- Read-heavy or write-heavy? (affects caching strategy)\n- Global or single-region? (affects replication design)\n- Strong or eventual consistency? (fundamental design driver)\n- What are the SLOs and who are the users?`,

    estimation: `**Back-of-Envelope Estimation**\n\n**Assumptions:**\n- Scale: ${topic.scale}\n- Read:Write ratio = 100:1 (most systems are read-heavy)\n- Average payload size = 1KB\n\n**QPS Calculation:**\n\`\`\`\nTotal requests/day = ${topic.scale.split('/')[0]} × reads\nPeak QPS = daily_requests / 86400 × 3 (3x peak factor)\n         ≈ 100,000 RPS peak\n\`\`\`\n\n**Storage Calculation:**\n\`\`\`\nNew data/day   = 10M new records × 1KB = 10GB/day\nFor 5 years    = 10GB × 365 × 5 = ~18TB\nWith replication (3x): 54TB total\n\`\`\`\n\n**Bandwidth:**\n\`\`\`\nIncoming: 10M writes/day × 1KB = ~115MB/s peak\nOutgoing: 100M reads/day × 1KB = ~1.15GB/s peak\n→ Need CDN offloading for read traffic\n\`\`\`\n\n**Memory (caching):**\n\`\`\`\nCache hot 20% of reads: 20M records × 1KB = 20GB Redis cluster\n\`\`\``,

    api: `**API Design for ${name}**\n\n**REST Endpoints:**\n\`\`\`\n# Primary CRUD\nPOST   /api/v1/resource         → Create\nGET    /api/v1/resource/{id}    → Read by ID  \nPUT    /api/v1/resource/{id}    → Update\nDELETE /api/v1/resource/{id}   → Delete\nGET    /api/v1/resources?cursor=xxx&limit=20  → Paginated list\n\`\`\`\n\n**Request/Response Schema:**\n\`\`\`json\n// POST /api/v1/resource\n{\n  "data": "...",\n  "metadata": { "ttl": 86400, "tags": ["tag1"] },\n  "client_id": "uuid"\n}\n\n// Response\n{\n  "id": "abc123",\n  "short_url": "https://example.com/abc123",\n  "created_at": "2024-01-01T00:00:00Z",\n  "expires_at": "2025-01-01T00:00:00Z"\n}\n\`\`\`\n\n**Pagination strategy:**\n- Cursor-based pagination (not offset) — consistent under concurrent inserts\n- Cursor = base64(timestamp + last_id)\n- Default page_size = 20, max = 100\n\n**Rate limiting headers:**\n\`\`\`\nX-RateLimit-Limit: 1000\nX-RateLimit-Remaining: 999\nX-RateLimit-Reset: 1704067200\n\`\`\``,

    datamodel: `**Data Model for ${name}**\n\n**Primary Table (SQL / DynamoDB):**\n\`\`\`sql\nCREATE TABLE records (\n    id          VARCHAR(8)   PRIMARY KEY,    -- Short key\n    data        TEXT         NOT NULL,\n    user_id     BIGINT       NOT NULL,\n    created_at  TIMESTAMP    DEFAULT NOW(),\n    expires_at  TIMESTAMP,\n    is_active   BOOLEAN      DEFAULT TRUE,\n    \n    -- Partitioning key for horizontal scaling\n    shard_key   SMALLINT GENERATED ALWAYS AS (HASH(id) % 256)\n);\n\n-- Indexes\nCREATE INDEX idx_user_id ON records(user_id, created_at DESC);\nCREATE INDEX idx_expires ON records(expires_at) WHERE is_active = TRUE;\n\`\`\`\n\n**Sharding strategy:**\n- Shard by hash(primary_key) → 256 shards → ~400M records/shard before rebalancing\n- Each shard = 1 primary + 2 read replicas\n- Cross-shard queries require scatter-gather (avoid for hot paths)\n\n**Caching layer (Redis):**\n\`\`\`\nKey:   resource:{id}\nValue: JSON blob\nTTL:   3600s (1 hour, or match expiry)\nWrite: write-through on create, lazy on update\nEviction: allkeys-lru\n\`\`\``,

    architecture: `**High-Level Architecture for ${name}**\n\n\`\`\`\nClients\n  ↓  HTTPS\nCDN (CloudFront / Fastly)\n  ↓  Cache miss\nAPI Gateway (Kong / AWS API GW)\n  ├── Auth Service (JWT validation)\n  ├── Rate Limiter (Redis sliding window)\n  └── Load Balancer (Round-robin L7)\n       ↓\nApplication Servers (stateless, auto-scaled)\n  ├── Read path  → Redis Cache → DB Read Replica\n  └── Write path → Message Queue (Kafka) → DB Primary\n                                         → Async workers\nDatabase Layer\n  ├── Primary: PostgreSQL (writes)\n  ├── Read replicas: 3 replicas (reads)\n  └── Cache: Redis Cluster (hot data)\n\nAsync Layer\n  ├── Kafka (event streaming)\n  ├── Workers (analytics, notifications)\n  └── Data Warehouse (S3 + Athena)\n\`\`\`\n\n**Request flow:**\n1. Client → CDN (cache hit? serve directly)\n2. CDN miss → API Gateway (auth, rate limit)\n3. Gateway → App Server (stateless, any instance)\n4. App → Redis (cache hit? return in <5ms)\n5. Cache miss → DB read replica (< 50ms)\n6. Write → DB primary → async replication → replicas`,

    scaling: `**Scaling Strategy for ${name}**\n\n**Horizontal Scaling (stateless app tier):**\n- Auto-scaling groups based on CPU (target 60%)\n- Blue-green deployment for zero-downtime releases\n- Connection pooling (PgBouncer) — each server has 10k conns, DB handles 500\n\n**Database Scaling:**\n- Read replicas: Start with 1, add more at >80% read load on primary\n- Sharding: When primary > 1TB or QPS > 10k writes/sec\n- Consider CockroachDB/Spanner for automatic horizontal sharding\n\n**Caching Strategy (cache hierarchy):**\n1. Browser cache (CDN headers, ETag, max-age)\n2. CDN cache (edge nodes, 200+ PoPs globally)\n3. Application cache (local in-process LRU, 1000 items)\n4. Distributed cache (Redis cluster, sub-millisecond)\n5. Database (last resort)\n\n**Cache eviction policies:**\n- LRU for general purpose\n- LFU for content with stable popularity (CDN)\n- TTL-based for session data and tokens\n\n**Async processing (offload from critical path):**\n- Email sending, push notifications, analytics → Kafka\n- Image processing, PDF generation → SQS + Lambda\n- Never block a user-facing request on background work`,

    reliability: `**Reliability & Resiliency**\n\n**Replication:**\n- Database: synchronous replication to 1 replica (durability), async to 2 more (availability)\n- Multi-AZ deployment: primary in us-east-1a, replica in us-east-1b and us-east-1c\n- RPO: < 1 second, RTO: < 30 seconds for AZ failure\n\n**Circuit Breaker Pattern:**\n\`\`\`python\nfrom circuitbreaker import circuit\n\n@circuit(failure_threshold=5, recovery_timeout=30)\ndef call_database(query):\n    return db.execute(query)  # Opens circuit after 5 failures\n\`\`\`\n\n**Retry Strategy:**\n- Exponential backoff: retry at 1s, 2s, 4s, 8s (max 3 retries)\n- Jitter: add random 0-1s to prevent thundering herd\n- Idempotency keys for safe retries on write operations\n\n**Graceful Degradation:**\n- If cache is down → serve from DB (slower but functional)\n- If recommendations fail → serve chronological feed\n- If search is down → return "search temporarily unavailable" (not 500)\n\n**Health Checks:**\n- Shallow: /health → returns 200 (process alive)\n- Deep: /health/ready → checks DB, cache, dependencies\n- Load balancer uses shallow, orchestrator uses deep`,

    consistency: `**Consistency vs Availability Trade-offs (CAP Theorem Applied)**\n\n**CAP Theorem Reality for ${name}:**\nNetwork partitions WILL happen. You're choosing between C and A.\n\n**What this system chooses:**\n- Prefer Availability for reads (users can tolerate slightly stale data)\n- Prefer Consistency for critical writes (payments, auth tokens)\n\n**Consistency levels in practice:**\n| Operation | Level | Rationale |\n|---|---|---|\n| Read user profile | Eventual | Staleness < 1s is fine |\n| Read payments | Strong | Must be accurate |\n| Write new post | Eventual | Followers see it ~1s later |\n| Auth token validation | Strong | Security critical |\n\n**Techniques for strong consistency:**\n- Read from primary (not replica) for critical reads\n- Versioned writes with optimistic locking (compare-and-swap)\n- Two-phase commit for cross-service transactions (avoid if possible)\n\n**Techniques for eventual consistency:**\n- Event sourcing: single source of truth in event log\n- CRDT data structures for conflict-free merging\n- Saga pattern for distributed transactions without 2PC`,

    security: `**Security Design for ${name}**\n\n**Authentication & Authorization:**\n\`\`\`\nAuth flow:\n  Client → Login → Auth Service → JWT (15min TTL)\n  Client → API → Gateway validates JWT → Request proceeds\n  Refresh: Refresh token (7 days) → new JWT pair\n\`\`\`\n\n**Rate Limiting (multi-layer):**\n- Layer 1: CDN rate limiting (coarse, DDoS protection)\n- Layer 2: API Gateway (per-IP, 1000 req/min)\n- Layer 3: Application (per-user, 100 req/min for writes)\n\n**Data Security:**\n- Encryption at rest: AES-256 (AWS KMS managed keys)\n- Encryption in transit: TLS 1.3 minimum\n- PII fields: encrypt at application layer with user-specific keys\n- Secrets: AWS Secrets Manager, never in code or env vars\n\n**Input Validation:**\n\`\`\`python\nimport re\nfrom pydantic import BaseModel, validator\n\nclass CreateRequest(BaseModel):\n    url: str\n    \n    @validator('url')\n    def validate_url(cls, v):\n        pattern = r'^https?://[^\\s/$.?#].[^\\s]*$'\n        if not re.match(pattern, v):\n            raise ValueError('Invalid URL format')\n        if len(v) > 2048:\n            raise ValueError('URL too long')\n        return v\n\`\`\`\n\n**SQL Injection prevention:**\n- Always use parameterised queries (never f-strings in SQL)\n- ORM with query builder (SQLAlchemy, Prisma)`,

    monitoring: `**Monitoring & Observability for ${name}**\n\n**The Three Pillars:**\n\n**1. Metrics (Prometheus + Grafana):**\n\`\`\`\nKey SLI Metrics to track:\n- request_duration_seconds (p50, p95, p99)\n- request_error_rate (5xx / total)\n- cache_hit_ratio (target > 95%)\n- db_query_duration_seconds\n- queue_depth (if async workers)\n\`\`\`\n\n**2. Logs (ELK / DataDog):**\n\`\`\`json\n{\n  "timestamp": "2024-01-01T00:00:00Z",\n  "level": "INFO",\n  "service": "api",\n  "trace_id": "abc123",\n  "user_id": "u456",\n  "endpoint": "POST /api/v1/resource",\n  "duration_ms": 45,\n  "status": 200\n}\n\`\`\`\n\n**3. Traces (Jaeger / AWS X-Ray):**\n- Distributed tracing across all services\n- Identify which service is slow (not just "the request was slow")\n\n**SLO/SLA Definition:**\n- SLO: 99.9% of requests succeed in < 200ms\n- Error budget: 0.1% = 43.2min/month\n- Burn rate alert: if using error budget 2x faster than planned → page on-call\n\n**Alerting (PagerDuty):**\n- P1 (immediate): error rate > 1%, latency > 1s\n- P2 (30min): cache hit < 90%, queue depth > 10k\n- P3 (business hours): storage > 80%, slow queries > 100ms`,

    bottlenecks: `**Bottleneck Analysis for ${name}**\n\n**What breaks at different scales:**\n\n| Scale | Bottleneck | Solution |\n|---|---|---|\n| 1k RPS | Single app server CPU | Horizontal scaling |\n| 10k RPS | Database connections | Connection pooling |\n| 100k RPS | DB read I/O | Read replicas + caching |\n| 1M RPS | Network bandwidth | CDN + data locality |\n| 10M RPS | Cache memory | Distributed cache cluster |\n\n**Hot Spots (the N+1 problem):**\n\`\`\`python\n# BAD: N+1 query pattern\nfor user_id in user_ids:          # 1 query\n    profile = db.get(user_id)     # N queries → catastrophic at scale\n\n# GOOD: Batch fetch\nprofiles = db.get_many(user_ids)  # 1 query\n\`\`\`\n\n**Celebrity / Hot Key Problem:**\nWhen a famous user's post goes viral → millions of reads to same cache key\n- Solution 1: Read-through cache with consistent hashing\n- Solution 2: Local in-process cache (first 1000 copies served from memory)\n- Solution 3: Proactive cache warming before anticipated spike\n\n**Capacity Planning:**\n- Run load tests at 2x, 5x, 10x expected peak before launch\n- Monitor p99 latency, not just averages (averages lie)\n- Auto-scaling with headroom (scale at 60% CPU, not 90%)`,

    interview_tips: `**Interview Discussion Tips for ${name}**\n\n**The 45-minute structure:**\n- 0-5min: Clarify requirements, ask smart questions\n- 5-10min: Estimation (QPS, storage, bandwidth)\n- 10-20min: High-level architecture discussion\n- 20-30min: Component deep dives (pick 2-3 the interviewer cares about)\n- 30-40min: Trade-off discussion, failure scenarios\n- 40-45min: Questions to interviewer, wrap up\n\n**Questions to ask the interviewer (signals seniority):**\n1. "What consistency guarantees do we need?"\n2. "Is this read-heavy or write-heavy? What's the ratio?"\n3. "Are we optimising for cost, latency, or simplicity first?"\n4. "Do we need global distribution or single region?"\n5. "What's the DAU and peak concurrency?"\n\n**Common mistakes candidates make:**\n1. Jumping to microservices for a problem that doesn't need it\n2. Not doing estimation (leads to wrong architecture choices)\n3. Being too vague: "use a cache" vs "Redis cluster with LRU eviction"\n4. Ignoring failure modes: "what happens if the DB is slow?"\n5. Not knowing CAP theorem well enough to apply it\n\n**What FAANG interviewers want to see:**\n- Structured thinking (requirements → estimation → design → deep dive)\n- Justify EVERY decision with trade-offs\n- Proactively identify failure modes before being asked\n- Know 2-3 design patterns deeply: consistent hashing, saga, circuit breaker`,

    insights: `**Real-World Production Insights**\n\n**How big tech actually builds ${name}:**\n\n**Lesson 1: Start simple, evolve later**\nNetflix ran on a monolith until they needed to scale. Twitter started with Ruby on Rails and MySQL. Don't over-engineer at launch — you'll optimise the wrong things.\n\n**Lesson 2: The database is usually the bottleneck**\nApp servers are stateless and trivially scalable. Your primary DB can't be. Invest early in: connection pooling, query optimisation, appropriate indexes, and read replicas.\n\n**Lesson 3: Caching is dangerous**\nCache invalidation is one of the two hard problems in CS. Stale cache + write-through + TTL mismatch caused major outages at Twitter, Amazon, and Facebook. Design your cache invalidation strategy before caching anything.\n\n**Lesson 4: Distributed transactions are evil**\nTwo-phase commit is slow (holds locks) and complex (failure handling). If you need cross-service consistency, use the Saga pattern + compensating transactions instead.\n\n**Lesson 5: Observability is not optional**\nYou WILL have a 3am incident. The question is whether you can find the root cause in 10 minutes or 3 hours. Log structured data, trace everything, and alert on burn rates not thresholds.`,

    quiz: '',
    lld: `**Low-Level Design: ${name}**\n\n**Core Classes:**\n\`\`\`python\nfrom abc import ABC, abstractmethod\nfrom dataclasses import dataclass\nfrom datetime import datetime\nfrom typing import Optional\nimport hashlib\nimport base64\n\n@dataclass\nclass Resource:\n    id: str\n    data: str\n    user_id: str\n    created_at: datetime\n    expires_at: Optional[datetime] = None\n    is_active: bool = True\n\nclass StorageBackend(ABC):\n    @abstractmethod\n    def get(self, resource_id: str) -> Optional[Resource]: ...\n    \n    @abstractmethod  \n    def set(self, resource: Resource) -> bool: ...\n    \n    @abstractmethod\n    def delete(self, resource_id: str) -> bool: ...\n\nclass CacheDecorator(StorageBackend):\n    """Cache-aside pattern decorator over any storage backend."""\n    \n    def __init__(self, backend: StorageBackend, cache):\n        self.backend = backend\n        self.cache = cache\n    \n    def get(self, resource_id: str) -> Optional[Resource]:\n        # Try cache first\n        cached = self.cache.get(f"resource:{resource_id}")\n        if cached:\n            return cached\n        \n        # Cache miss → fetch from backend\n        resource = self.backend.get(resource_id)\n        if resource:\n            self.cache.set(f"resource:{resource_id}", resource, ttl=3600)\n        return resource\n\`\`\`\n\n**Design Patterns used:**\n- Repository pattern: decouple storage from business logic\n- Decorator pattern: add caching without modifying storage class\n- Strategy pattern: swap storage backends (SQL → NoSQL) without changing callers`,
  };

  return templates[sectionId] ?? `**${name} — ${sectionId}**\n\nProduction-quality system design content for this section.`;
}

const SECTION_DEFS = [
  { id: 'problem', label: 'Problem Statement & Why It Matters', icon: 'DocumentTextIcon', subtitle: 'Context, challenges, interview importance' },
  { id: 'requirements', label: 'Functional & Non-Functional Requirements', icon: 'ClipboardDocumentListIcon', subtitle: 'User stories, SLOs, constraints' },
  { id: 'estimation', label: 'Back-of-Envelope Estimation', icon: 'CalculatorIcon', subtitle: 'QPS, storage, bandwidth, memory' },
  { id: 'api', label: 'API Design', icon: 'CodeBracketSquareIcon', subtitle: 'REST endpoints, schemas, pagination' },
  { id: 'datamodel', label: 'Data Model', icon: 'CircleStackIcon', subtitle: 'SQL schema, indexing, sharding key' },
  { id: 'architecture', label: 'High-Level Architecture', icon: 'ServerStackIcon', subtitle: 'Component diagram + request flow' },
  { id: 'scaling', label: 'Scaling Strategy', icon: 'ArrowTrendingUpIcon', subtitle: 'Horizontal scaling, caching layers, CDN' },
  { id: 'reliability', label: 'Reliability & Resiliency', icon: 'ShieldCheckIcon', subtitle: 'Replication, circuit breakers, retries' },
  { id: 'consistency', label: 'Consistency vs Availability (CAP)', icon: 'ScaleIcon', subtitle: 'CAP applied to this specific system' },
  { id: 'security', label: 'Security Design', icon: 'LockClosedIcon', subtitle: 'Auth, rate limiting, encryption, PII' },
  { id: 'monitoring', label: 'Monitoring & Observability', icon: 'ChartBarIcon', subtitle: 'SLOs, metrics, traces, alerting' },
  { id: 'bottlenecks', label: 'Bottleneck Analysis', icon: 'BoltSlashIcon', subtitle: 'What breaks at scale + solutions' },
  { id: 'interview_tips', label: 'Interview Discussion Tips', icon: 'AcademicCapIcon', subtitle: '45-min structure, what FAANG expects' },
  { id: 'insights', label: 'Real-World Production Insights', icon: 'BuildingOffice2Icon', subtitle: 'Big tech war stories, lessons learned' },
  { id: 'quiz', label: 'Quiz', icon: 'TrophyIcon', subtitle: '4 questions with explanations' },
  { id: 'lld', label: 'Low-Level Design', icon: 'PuzzlePieceIcon', subtitle: 'Design patterns, class diagrams, Python code' },
];

const QUIZ_BANK = [
  { q: 'What does CAP theorem state?', options: ['A system can have Consistency, Availability, and Partition tolerance', 'A distributed system can only guarantee 2 of: Consistency, Availability, Partition tolerance', 'Consistency and Availability are always achievable', 'Partition tolerance is optional'], answer: 1, explanation: 'CAP theorem: in the presence of a network Partition, you must choose between Consistency (all nodes see same data) and Availability (every request gets a response).' },
  { q: 'Which pagination strategy is better for systems with high write concurrency?', options: ['Offset-based pagination', 'Cursor-based pagination', 'Page number pagination', 'Time-based pagination'], answer: 1, explanation: 'Cursor-based pagination is consistent under concurrent writes. Offset pagination can miss or repeat records when rows are inserted between pages.' },
  { q: 'What is the primary purpose of consistent hashing in distributed systems?', options: ['Ensuring data consistency', 'Minimising key remapping when nodes are added/removed', 'Load balancing HTTP requests', 'Preventing hash collisions'], answer: 1, explanation: 'Consistent hashing maps keys to a ring. Adding/removing a node only remaps keys that were assigned to that specific node, minimising data movement.' },
  { q: 'What does a circuit breaker do when it "opens"?', options: ['Retries the request with exponential backoff', 'Fails fast without calling the downstream service', 'Routes traffic to a backup service', 'Sends an alert to the on-call engineer'], answer: 1, explanation: 'An open circuit breaker fails fast (returns error immediately) without calling the failing downstream service, preventing cascade failures.' },
];

function initSections(): Record<string, SectionState> {
  return Object.fromEntries(SECTION_DEFS.map(s => [s.id, { generated: false, generating: false, content: '' }]));
}

export default function SystemDesignLabInteractive() {
  const [topics] = useState<SDTopic[]>(TOPICS);
  const [selectedTopicId, setSelectedTopicId] = useState('url-shortener');
  const [selectedSubtopicId, setSelectedSubtopicId] = useState<string | null>(null);
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set(['url-shortener']));
  const [sections, setSections] = useState<Record<string, SectionState>>(initSections());
  const [customInput, setCustomInput] = useState('');
  const [addingCustom, setAddingCustom] = useState(false);
  const [customTopics, setCustomTopics] = useState<SDTopic[]>([]);
  const [quizBatch, setQuizBatch] = useState(0);

  const allTopics = [...topics, ...customTopics];
  const currentTopic = allTopics.find(t => t.id === selectedTopicId) ?? null;
  const currentSubtopic = currentTopic?.subtopics.find(s => s.id === selectedSubtopicId) ?? null;
  const contextLabel = currentSubtopic?.name ?? currentTopic?.name ?? 'System Design';

  const flatItems = allTopics.flatMap(t => [
    { id: t.id, type: 'topic', topicId: t.id, label: t.name },
    ...t.subtopics.map(s => ({ id: s.id, type: 'subtopic', topicId: t.id, label: s.name })),
  ]);
  const activeId = selectedSubtopicId ?? selectedTopicId;
  const currentIdx = flatItems.findIndex(x => x.id === activeId);
  const prevItem = currentIdx > 0 ? flatItems[currentIdx - 1] : null;
  const nextItem = currentIdx >= 0 && currentIdx < flatItems.length - 1 ? flatItems[currentIdx + 1] : null;

  const navigateTo = (item: typeof flatItems[0]) => {
    setSelectedTopicId(item.topicId);
    setSelectedSubtopicId(item.type === 'subtopic' ? item.id : null);
    setSections(initSections());
    setQuizBatch(0);
    setExpandedTopics(prev => new Set([...prev, item.topicId]));
  };

  const selectTopic = (id: string) => {
    setSelectedTopicId(id);
    setSelectedSubtopicId(null);
    setSections(initSections());
    setQuizBatch(0);
    setExpandedTopics(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  };

  const generateSection = (sectionId: string) => {
    if (!currentTopic) return;
    setSections(prev => ({ ...prev, [sectionId]: { ...prev[sectionId], generating: true } }));
    setTimeout(() => {
      setSections(prev => ({ ...prev, [sectionId]: { generated: true, generating: false, content: getContent(sectionId, currentTopic) } }));
    }, 1500);
  };

  const handleAddCustom = () => {
    if (!customInput.trim()) return;
    setAddingCustom(true);
    setTimeout(() => {
      const t: SDTopic = { id: `custom-${Date.now()}`, name: customInput.trim(), brief: 'Custom system design problem.', category: 'Custom', scale: '1M RPS', subtopics: [] };
      setCustomTopics(prev => [...prev, t]);
      setCustomInput('');
      setAddingCustom(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-background pt-[60px] flex flex-col">
      <div className="flex-1 flex overflow-hidden" style={{ height: 'calc(100vh - 60px)' }}>

        {/* ── LEFT Sidebar ──────────────────────────────────────────────── */}
        <aside className="w-[260px] flex-shrink-0 border-r border-border bg-card flex flex-col">
          <div className="p-14 border-b border-border flex-shrink-0">
            <h2 className="font-heading text-sm font-semibold text-foreground flex items-center gap-9">
              <Icon name="ServerStackIcon" size={15} className="text-primary" />System Design Lab
            </h2>
            <p className="text-xs text-muted-foreground mt-3">Select problem → Generate sections</p>
          </div>

          <div className="flex-1 overflow-y-auto py-6">
            {allTopics.map(topic => (
              <div key={topic.id}>
                <button onClick={() => selectTopic(topic.id)}
                  className={`w-full text-left flex items-center gap-8 px-14 py-9 text-xs font-semibold transition-smooth hover:bg-muted ${selectedTopicId === topic.id && !selectedSubtopicId ? 'bg-primary/10 text-primary border-r-2 border-primary' : 'text-foreground'}`}>
                  <Icon name="ServerStackIcon" size={12} />
                  <div className="flex-1 min-w-0">
                    <span className="block truncate">{topic.name}</span>
                    <span className="text-[10px] text-muted-foreground">{topic.scale}</span>
                  </div>
                  <Icon name={expandedTopics.has(topic.id) ? 'ChevronDownIcon' : 'ChevronRightIcon'} size={11} className="text-muted-foreground flex-shrink-0" />
                </button>
                {expandedTopics.has(topic.id) && topic.subtopics.length > 0 && (
                  <div>
                    {topic.subtopics.map(sub => (
                      <button key={sub.id}
                        onClick={() => { setSelectedTopicId(topic.id); setSelectedSubtopicId(sub.id); setSections(initSections()); setQuizBatch(0); setExpandedTopics(prev => new Set([...prev, topic.id])); }}
                        className={`w-full text-left flex flex-col pl-26 pr-14 py-8 text-xs transition-smooth hover:bg-muted ${selectedSubtopicId === sub.id ? 'bg-secondary/10 text-secondary border-r-2 border-secondary' : 'text-muted-foreground'}`}>
                        <span className="font-medium truncate">↳ {sub.name}</span>
                        <span className="text-[10px] opacity-70 truncate mt-1">{sub.brief}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="p-12 border-t border-border flex-shrink-0">
            <div className="flex gap-6">
              <input value={customInput} onChange={e => setCustomInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAddCustom()}
                placeholder="Add custom problem..."
                className="flex-1 min-w-0 bg-input border border-border rounded-md px-9 py-6 text-xs focus-ring placeholder:text-muted-foreground" />
              <button onClick={handleAddCustom} disabled={addingCustom || !customInput.trim()}
                className="p-6 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-smooth disabled:opacity-50 flex-shrink-0">
                {addingCustom ? <span className="w-12 h-12 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin block" /> : <Icon name="PlusIcon" size={14} />}
              </button>
            </div>
          </div>
        </aside>

        {/* ── CENTER ────────────────────────────────────────────────────── */}
        <main className="flex-1 overflow-y-auto">
          {!currentTopic ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-24">
              <Icon name="ServerStackIcon" size={48} variant="outline" className="text-muted-foreground/30 mb-18" />
              <h2 className="font-heading text-xl font-semibold text-foreground mb-9">Select a System Design Problem</h2>
              <p className="text-sm text-muted-foreground max-w-sm">Choose a problem from the sidebar. Each of the 16 sections generates on-demand.</p>
            </div>
          ) : (
            <div className="p-20 space-y-14">
              <div className="bg-card border border-border rounded-lg p-20 shadow-sm">
                <div className="flex items-start justify-between gap-18 flex-wrap">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-9 mb-9">
                      <span className="text-xs bg-primary/10 text-primary px-9 py-4 rounded-md">{currentTopic.category}</span>
                      <span className="text-xs bg-muted text-muted-foreground px-9 py-4 rounded-md font-code">Scale: {currentTopic.scale}</span>
                      {currentSubtopic && <span className="text-xs bg-secondary/10 text-secondary px-9 py-4 rounded-md">Deep Dive</span>}
                    </div>
                    <h1 className="font-heading text-2xl font-bold text-foreground mb-6">{currentSubtopic?.name ?? currentTopic.name}</h1>
                    <p className="text-sm text-muted-foreground">{currentSubtopic?.brief ?? currentTopic.brief}</p>
                  </div>
                </div>
              </div>

              {SECTION_DEFS.map((def, idx) => {
                const s = sections[def.id] ?? { generated: false, generating: false, content: '' };
                return (
                  <OnDemandSection key={def.id} sectionIndex={idx + 1} icon={def.icon} title={def.label} subtitle={def.subtitle}
                    content={s.content} isGenerated={s.generated} isGenerating={s.generating} onGenerate={() => generateSection(def.id)}>
                    {def.id === 'quiz' && s.generated ? (
                      <QuizCarousel questions={QUIZ_BANK.slice(quizBatch * 4, quizBatch * 4 + 4)} hasMore={true} onGenerateMore={() => setQuizBatch(b => b + 1)} />
                    ) : undefined}
                  </OnDemandSection>
                );
              })}

              <div className="flex items-center justify-between py-18 border-t border-border mt-24">
                <button disabled={!prevItem} onClick={() => prevItem && navigateTo(prevItem)}
                  className="flex items-center gap-9 px-16 py-10 rounded-md border border-border text-sm text-foreground hover:bg-muted transition-smooth disabled:opacity-30 disabled:pointer-events-none">
                  <Icon name="ArrowLeftIcon" size={14} />{prevItem?.label ?? 'No previous'}
                </button>
                <button disabled={!nextItem} onClick={() => nextItem && navigateTo(nextItem)}
                  className="flex items-center gap-9 px-16 py-10 rounded-md border border-border text-sm text-foreground hover:bg-muted transition-smooth disabled:opacity-30 disabled:pointer-events-none">
                  {nextItem?.label ?? 'No next'}<Icon name="ArrowRightIcon" size={14} />
                </button>
              </div>
            </div>
          )}
        </main>

        {/* ── RIGHT: Copilot ─────────────────────────────────────────────── */}
        <aside className="w-[280px] flex-shrink-0 border-l border-border flex flex-col">
          <LabCopilot context={contextLabel} labType="system-design" />
        </aside>
      </div>
    </div>
  );
}
