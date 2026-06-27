# cv and system design sidebar outline

Here's your seed topic tree for the Computer Vision Lab left sidebar:
* * *

**Computer Vision Lab — Sidebar Topics**

```markdown
1. Image Basics & Representation [Easy]
   - Pixels, Channels, Color Spaces (RGB, HSV, LAB)
   - Image Reading, Writing, Display with OpenCV
   - Image Resizing, Cropping, Rotation

2. Image Filtering & Convolution [Easy]
   - Kernels & Convolution Operation
   - Gaussian Blur & Box Blur
   - Sharpening Filters

3. Thresholding & Binarization [Easy]
   - Global Thresholding (Otsu's Method)
   - Adaptive Thresholding
   - Color-based Segmentation (HSV masking)

4. Edge Detection [Easy-Medium]
   - Sobel & Laplacian Operators
   - Canny Edge Detection
   - Edge Detection for Real-World Images

5. Morphological Operations [Easy]
   - Erosion, Dilation
   - Opening, Closing
   - Practical Use: Noise Removal & Gap Filling

6. Contour Detection & Shape Analysis [Medium]
   - Finding & Drawing Contours
   - Contour Properties (area, perimeter, bounding box)
   - Shape Classification using Contours

7. Feature Detection & Matching [Medium]
   - Harris Corner Detection
   - ORB Feature Detector
   - Feature Matching between Images (BFMatcher)

8. Histogram Analysis [Easy-Medium]
   - Histogram Computation & Visualization
   - Histogram Equalization (CLAHE)
   - Histogram Backprojection

9. Geometric Transformations & Homography [Medium]
   - Affine Transformations
   - Perspective Transform (Bird's Eye View)
   - Homography Estimation with RANSAC

10. Template Matching & Object Localization [Medium]
    - Template Matching Methods
    - Multi-scale Template Matching
    - Limitations & When to Use

11. Optical Flow & Motion Estimation [Medium-Hard]
    - Lucas-Kanade Optical Flow
    - Dense Optical Flow (Farneback)
    - Motion Detection & Tracking Applications

12. Image Segmentation (Classical) [Medium]
    - Watershed Algorithm
    - GrabCut
    - Mean Shift Segmentation

13. Camera Calibration & Stereo Vision [Hard]
    - Intrinsic & Extrinsic Parameters
    - Chessboard Calibration
    - Stereo Matching & Depth Maps

14. Introduction to CNNs [Medium]
    - Convolution, Pooling, Stride, Padding
    - Building a CNN from Scratch (PyTorch)
    - Training on CIFAR-10

15. Transfer Learning & Fine-Tuning [Medium]
    - Using Pretrained Models (ResNet, EfficientNet)
    - Feature Extraction vs Fine-Tuning
    - Custom Dataset Training Pipeline

16. Image Classification Architectures [Medium-Hard]
    - LeNet → AlexNet → VGG (evolution)
    - ResNet & Skip Connections
    - EfficientNet & Neural Architecture Search

17. Object Detection with YOLO [Medium-Hard]
    - YOLO Architecture & How It Works
    - YOLOv8 Training on Custom Dataset
    - Real-Time Detection Deployment

18. Object Detection (Two-Stage) [Hard]
    - R-CNN → Fast R-CNN → Faster R-CNN
    - Region Proposal Networks
    - Anchor Boxes, IoU, NMS, mAP Metrics

19. Semantic Segmentation [Hard]
    - Fully Convolutional Networks (FCN)
    - U-Net Architecture & Medical Imaging
    - DeepLabV3+ & Atrous Convolution

20. Instance Segmentation [Hard]
    - Mask R-CNN Architecture
    - Panoptic Segmentation
    - Segment Anything Model (SAM)

21. GANs (Generative Adversarial Networks) [Hard]
    - GAN Fundamentals & Training Loop
    - DCGAN Implementation
    - CycleGAN (Unpaired Image Translation)

22. Diffusion Models [Hard]
    - DDPM (Denoising Diffusion Probabilistic Models)
    - Stable Diffusion Architecture
    - Controlnet & Guided Generation

23. Vision Transformers (ViT) [Hard]
    - Self-Attention for Images
    - ViT Architecture & Patch Embeddings
    - Swin Transformer & Hierarchical Features

24. CLIP & Multimodal Vision [Hard]
    - Contrastive Learning for Vision-Language
    - Zero-Shot Classification with CLIP
    - Building a CLIP-based Image Search

25. Video Understanding [Medium-Hard]
    - Frame Extraction & Video Processing
    - Object Tracking (DeepSORT, ByteTrack)
    - Action Recognition (SlowFast, I3D)

26. Face Detection & Recognition [Medium]
    - Haar Cascades & HOG Detectors
    - MTCNN & RetinaFace
    - FaceNet Embeddings & Face Matching

27. OCR & Document Analysis [Medium]
    - Tesseract OCR Pipeline
    - Scene Text Detection (EAST, CRAFT)
    - Document Layout Analysis

28. Pose Estimation [Medium-Hard]
    - OpenPose & MediaPipe
    - HRNet Architecture
    - Applications: Fitness, AR, Sign Language

29. 3D Vision & Depth Estimation [Hard]
    - Monocular Depth Estimation (MiDaS)
    - Point Clouds & PointNet
    - NeRF (Neural Radiance Fields)

30. Model Deployment for Vision [Medium]
    - ONNX Export & Optimization
    - TensorRT & OpenVINO
    - Edge Deployment (Jetson Nano, Mobile)

31. Data Augmentation & Training Tricks [Easy-Medium]
    - Albumentations Library
    - Mixup, Cutout, CutMix
    - Handling Class Imbalance

32. Adversarial Attacks & Robustness [Hard]
    - FGSM & PGD Attacks
    - Adversarial Training
    - Model Robustness Evaluation

33. Self-Supervised Learning for Vision [Hard]
    - Contrastive Learning (SimCLR, MoCo)
    - Masked Autoencoders (MAE)
    - DINO & Self-Distillation

34. Explainability & Interpretability [Medium-Hard]
    - Grad-CAM & Saliency Maps
    - SHAP for Image Models
    - What Does the Network Actually See?

35. End-to-End Projects [Mixed]
    - Build a Real-Time License Plate Reader [Medium]
    - Build a Visual Search Engine [Hard]
    - Build a Defect Detection System (Manufacturing) [Hard]
    - Build an AR Filter (Face Mesh + Overlay) [Medium]
    - Build a Document Scanner App [Easy-Medium]
```

* * *

35 topics, easy to hard, covers classical CV through cutting-edge research. Good mix for progressive learning. Want me to save this into your doc?

Here's the upgraded System Design seed list, heavy on Microsoft/Apple/FAANG-level topics:
* * *

**System Design Lab, Sidebar Topics (Microsoft/Apple/FAANG Edition)**

```markdown
1. Scaling Fundamentals [Easy]
   - Vertical vs Horizontal Scaling
   - Stateless vs Stateful Services
   - When to Scale What

2. Load Balancing [Easy]
   - L4 vs L7 Load Balancers
   - Algorithms (Round Robin, Weighted, Consistent Hashing)
   - Health Checks, Failover, Global Server Load Balancing (GSLB)

3. Caching Strategies [Easy-Medium]
   - Cache-Aside, Write-Through, Write-Behind, Read-Through
   - Eviction Policies (LRU, LFU, TTL)
   - Cache Stampede, Thundering Herd, Hot Key Solutions
   - Multi-Layer Caching (L1 local, L2 distributed)

4. CDN & Edge Computing [Easy-Medium]
   - Pull vs Push CDN
   - Edge Functions & Compute at Edge
   - Cache Invalidation at Global Scale

5. Database Fundamentals [Easy-Medium]
   - SQL vs NoSQL Decision Framework
   - ACID vs BASE
   - Indexing (B-Tree, LSM, Bloom Filters)
   - Connection Pooling & Query Optimization

6. Database Sharding & Partitioning [Medium-Hard]
   - Sharding Strategies (hash, range, geo, directory-based)
   - Rebalancing, Hotspot Handling, Cross-Shard Joins
   - Vitess, CockroachDB, Spanner Approaches
   - [FAANG asks: How would you handle resharding with zero downtime?]

7. Database Replication & Consistency [Medium-Hard]
   - Leader-Follower, Multi-Leader, Leaderless
   - Synchronous vs Async Replication
   - Quorum Reads/Writes (W+R > N)
   - [Microsoft asks: How does Cosmos DB handle multi-region consistency?]

8. CAP Theorem & Consistency Models [Medium]
   - CAP, PACELC, FLP Impossibility
   - Strong, Eventual, Causal, Linearizable Consistency
   - Real Systems: Dynamo (AP), Spanner (CP), Cassandra (tunable)

9. Consistent Hashing & Data Distribution [Medium]
   - Virtual Nodes, Token Ring
   - Bounded Load Consistent Hashing
   - Rendezvous Hashing (Highest Random Weight)

10. Message Queues & Event Streaming [Medium-Hard]
    - Queue vs Pub/Sub vs Log-Based Streaming
    - At-Least-Once, At-Most-Once, Exactly-Once Semantics
    - Backpressure, Dead Letter Queues, Poison Pills
    - Kafka vs RabbitMQ vs Azure Service Bus vs SQS
    - [Microsoft asks: Design event ordering guarantees across partitions]

11. API Design & Gateway [Medium]
    - REST vs gRPC vs GraphQL vs WebSockets vs SSE
    - Pagination (cursor vs offset vs keyset)
    - Idempotency Keys & Retry Safety
    - API Versioning Strategies
    - [Apple asks: How do you design APIs for backward compatibility across 5 iOS versions?]

12. Rate Limiting & Throttling [Easy-Medium]
    - Token Bucket, Leaky Bucket, Sliding Window, Fixed Window
    - Distributed Rate Limiting (Redis + Lua)
    - Adaptive Rate Limiting & Fair Queuing
    - [FAANG asks: How to rate-limit without a single point of failure?]

13. Microservices & Service Mesh [Medium-Hard]
    - Monolith → Microservices Decomposition
    - Service Discovery (client-side vs server-side)
    - Saga Pattern (choreography vs orchestration)
    - Service Mesh (Istio, Envoy sidecars)
    - [Microsoft asks: How do you handle distributed transactions across 10 services?]

14. Event-Driven Architecture [Medium-Hard]
    - Event Sourcing & Append-Only Logs
    - CQRS (Command Query Responsibility Segregation)
    - Outbox Pattern & Change Data Capture (CDC)
    - Temporal Coupling & Event Schema Evolution

15. Distributed Consensus & Coordination [Hard]
    - Paxos, Raft, ZAB (ZooKeeper)
    - Leader Election & Fencing Tokens
    - Split Brain, Network Partitions, Byzantine Faults
    - Distributed Locks (Redlock controversy)
    - [FAANG asks: Why is Redlock not safe? What would you use instead?]

16. Distributed Transactions [Hard]
    - Two-Phase Commit (2PC) & Three-Phase Commit
    - Saga Pattern Deep Dive
    - TCC (Try-Confirm-Cancel)
    - Calvin & Deterministic Databases
    - [Microsoft asks: How does Azure handle cross-region transactions?]

17. Data Pipelines & Stream Processing [Hard]
    - Batch vs Stream vs Micro-Batch
    - Lambda Architecture vs Kappa Architecture
    - Windowing (Tumbling, Sliding, Session, Watermarks)
    - Exactly-Once in Streaming (Flink, Kafka Streams)
    - Backfill, Schema Evolution, Late-Arriving Data
    - [FAANG asks: How do you handle out-of-order events in a 10M events/sec pipeline?]

18. Design a URL Shortener [Easy]
    - Base62 Encoding vs Hash-Based
    - Counter Service & Snowflake IDs
    - Analytics, Expiration, Abuse Prevention

19. Design a Rate Limiter Service [Medium]
    - Multi-Tier (per-user, per-IP, per-API, global)
    - Distributed Sliding Window (Redis Sorted Sets)
    - Graceful Degradation vs Hard Rejection

20. Design a Key-Value Store (DynamoDB/Redis) [Medium-Hard]
    - LSM Tree, Memtable, SSTable, Compaction
    - Replication (Sloppy Quorum, Hinted Handoff)
    - Vector Clocks & Conflict Resolution
    - Anti-Entropy & Merkle Trees
    - [Amazon/FAANG asks: Walk me through a write path end-to-end]

21. Design Twitter / X [Hard]
    - Fan-Out on Write vs Read (Hybrid for celebrities)
    - Timeline Ranking (ML + Heuristics)
    - Real-Time Tweet Delivery (WebSocket + Push)
    - Trending Topics (Count-Min Sketch, Lossy Counting)
    - [FAANG asks: How do you handle a user with 100M followers posting?]

22. Design Instagram [Medium-Hard]
    - Photo Upload Pipeline (resize, compress, CDN)
    - News Feed Generation & Ranking
    - Explore Feed (collaborative filtering + engagement signals)
    - Stories (ephemeral content, TTL-based storage)

23. Design WhatsApp / iMessage [Hard]
    - Real-Time Messaging (WebSocket, MQTT)
    - End-to-End Encryption (Signal Protocol, Key Exchange)
    - Message Delivery States (sent, delivered, read receipts)
    - Group Messaging (fan-out, ordering guarantees)
    - Offline Queue & Multi-Device Sync
    - [Apple asks: How does iMessage sync across iPhone, Mac, iPad with E2E encryption?]

24. Design YouTube / Netflix [Hard]
    - Video Ingestion & Transcoding Pipeline (DAG of jobs)
    - Adaptive Bitrate Streaming (HLS, DASH, CMAF)
    - CDN Strategy & Origin Shield
    - Recommendation Engine (candidate generation → ranking → re-ranking)
    - Live Streaming (low-latency HLS, WebRTC for interactive)
    - [FAANG asks: How do you serve 1M concurrent viewers for a live event?]

25. Design Google Drive / OneDrive / iCloud [Hard]
    - File Chunking, Deduplication, Delta Sync
    - Conflict Resolution (OT, CRDT, Last-Writer-Wins)
    - Sync Protocol & Notification (long polling, WebSocket)
    - Versioning, Trash, Cross-Device Consistency
    - [Microsoft asks: How does OneDrive handle sync conflicts across 5 devices?]
    - [Apple asks: How does iCloud maintain consistency with intermittent connectivity?]

26. Design Uber / Ola [Hard]
    - Geospatial Indexing (Geohash, H3, Quadtree, S2 Cells)
    - Real-Time Location Updates (GPS ingestion at scale)
    - Ride Matching (dispatch optimization, Hungarian algorithm)
    - ETA Prediction (graph + ML hybrid)
    - Surge Pricing Engine
    - [FAANG asks: How do you match 10K drivers to 10K riders in < 100ms?]

27. Design a Notification System [Medium-Hard]
    - Multi-Channel (Push/APNS/FCM, Email, SMS, In-App)
    - Priority Queuing & Throttling
    - Deduplication, Preference Management, Quiet Hours
    - Template Engine & A/B Testing
    - [Apple asks: How does APNS guarantee delivery with device offline for days?]

28. Design a Payment System (Stripe/Razorpay) [Hard]
    - Idempotency & Exactly-Once Payment Processing
    - Payment State Machine (authorize → capture → settle)
    - Double-Entry Ledger & Reconciliation
    - PCI-DSS Compliance, Tokenization, 3DS
    - Retry Strategy & Timeout Handling
    - [FAANG asks: How do you prevent double-charging during network partition?]

29. Design a Distributed Message Queue (Kafka) [Hard]
    - Log-Based Architecture, Partitions, Consumer Groups
    - ISR (In-Sync Replicas) & Leader Election
    - Exactly-Once Semantics (idempotent producer + transactions)
    - Compaction, Retention, Tiered Storage
    - [FAANG asks: What happens when a broker dies mid-produce?]

30. Design a Search Engine (Bing/Elasticsearch) [Hard]
    - Inverted Index Construction
    - Tokenization, Stemming, TF-IDF, BM25
    - Distributed Search (scatter-gather)
    - Real-Time Indexing & Near-Real-Time Search
    - Ranking (PageRank + ML-based re-ranking)
    - [Microsoft asks: How does Bing serve 10B queries/day with < 200ms latency?]

31. Design a Search Autocomplete / Typeahead [Medium-Hard]
    - Trie + Top-K with Precomputed Results
    - Personalization & Trending Boost
    - Real-Time Updates & Serving at Edge
    - [FAANG asks: How do you update suggestions within 5 minutes of a trending event?]

32. Design a Web Crawler (Bing Bot) [Medium-Hard]
    - URL Frontier & Priority Queue (politeness, freshness)
    - Distributed Crawling (partitioned by domain)
    - Deduplication (SimHash, MinHash for near-duplicates)
    - Robots.txt, Rate Limiting, Trap Detection
    - [Microsoft asks: How does BingBot prioritize 1B URLs with limited crawl budget?]

33. Design Google Maps / Apple Maps [Hard]
    - Map Tile Rendering & Serving (vector tiles, zoom levels)
    - Routing (Contraction Hierarchies, A*, traffic-aware)
    - ETA Prediction (real-time traffic + historical + ML)
    - Places Search (geospatial index, relevance ranking)
    - Offline Maps & Incremental Updates
    - [Apple asks: How do you serve offline turn-by-turn navigation?]

34. Design a Recommendation Engine [Hard]
    - Candidate Generation (collaborative filtering, ANN)
    - Ranking Model (deep learning, feature interactions)
    - Real-Time Personalization vs Batch
    - Cold Start (content-based, popular items, onboarding signals)
    - Feature Store Architecture
    - [FAANG asks: How do you balance exploration vs exploitation at scale?]

35. Design an Ad Click Aggregation System [Hard]
    - Real-Time Counting (billions/day)
    - Lambda vs Kappa for Aggregation
    - Deduplication & Click Fraud Detection
    - Windowed Aggregation & Late Events
    - Exactly-Once Counting Guarantees
    - [FAANG asks: How do you reconcile real-time counts with batch audit?]

36. Design a Metrics & Monitoring System (Azure Monitor/Datadog) [Hard]
    - Time-Series Ingestion (millions of metrics/sec)
    - Storage (downsampling, rollups, retention tiers)
    - Query Engine (PromQL-style aggregation)
    - Alerting (threshold, anomaly detection, alert fatigue)
    - [Microsoft asks: How does Azure Monitor handle 10M time-series with sub-minute alerting?]

37. Design a Distributed Task Scheduler [Hard]
    - DAG Execution & Dependency Resolution
    - Exactly-Once Task Execution (fencing, lease-based)
    - Priority Queuing & Fair Scheduling
    - Failure Recovery, Retry, Timeout, Poison Task Isolation
    - Multi-Tenant Resource Isolation
    - [FAANG asks: How do you guarantee exactly-once execution in a scheduler with worker crashes?]

38. Design a Real-Time Collaborative Editor (Office 365) [Hard]
    - Operational Transformation (OT) vs CRDTs
    - Cursor & Presence Synchronization
    - Conflict Resolution & Intent Preservation
    - Offline Editing & Merge
    - [Microsoft asks: How does Word Online handle 50 concurrent editors on one document?]

39. Design Cortana / Siri (Voice Assistant Backend) [Hard]
    - Speech-to-Text Pipeline (streaming ASR)
    - Intent Recognition & Slot Filling (NLU)
    - Orchestration Layer (skill routing)
    - Context Management & Multi-Turn Dialogue
    - Low-Latency Response Generation
    - [Apple asks: How do you achieve < 500ms response time for voice queries?]
    - [Microsoft asks: How does Cortana route to the right skill with ambiguous intent?]

40. Design Xbox Cloud Gaming / Game Streaming [Hard]
    - Video Encoding & Frame Streaming (sub-50ms latency)
    - Input Pipeline (predictive input, client-side prediction)
    - Server Allocation & Session Management
    - Adaptive Quality (network-aware bitrate switching)
    - [Microsoft asks: How do you achieve < 60ms input-to-display latency globally?]

41. Design App Store / Microsoft Store [Medium-Hard]
    - App Submission & Review Pipeline
    - Content Delivery (delta updates, chunked downloads)
    - Search & Ranking (relevance + quality signals)
    - Billing & Subscription Management
    - [Apple asks: How do you push a 2GB app update to 1B devices efficiently?]

42. Design iCloud Photo Library / OneDrive Photos [Hard]
    - Smart Storage (full-res in cloud, optimized on device)
    - ML-Based Organization (faces, objects, scenes, memories)
    - Cross-Device Sync with Bandwidth Optimization
    - Shared Albums & Permission Model
    - [Apple asks: How do you sync 100K photos across 5 devices without draining battery?]

43. Design a Fraud Detection System [Hard]
    - Real-Time Feature Computation (< 50ms)
    - Rule Engine + ML Scoring Hybrid
    - Graph-Based Fraud Detection (link analysis)
    - Model Retraining & Feedback Loop
    - Explainability for Compliance
    - [FAANG asks: How do you detect a new fraud pattern within hours, not weeks?]

44. Design a Global DNS System [Hard]
    - Hierarchical Resolution & Caching
    - Anycast Routing & GeoDNS
    - DNS Failover & Health Checking
    - DNSSEC & DNS-over-HTTPS
    - [FAANG asks: How does a DNS change propagate globally in < 60 seconds?]

45. Design a Distributed File System (HDFS/Azure Blob) [Hard]
    - Block Storage, Replication Factor, Rack Awareness
    - NameNode HA & Metadata Management
    - Erasure Coding vs Replication (cost vs durability)
    - Multi-Tenant Isolation & Quotas
    - [Microsoft asks: How does Azure Blob Storage achieve 11 nines durability?]

46. Design a Content Moderation Pipeline [Medium-Hard]
    - Multi-Modal Detection (text, image, video, audio)
    - ML Pipeline (pre-filter → classifier → human review)
    - Appeal System & Escalation
    - Latency Budget (pre-publish vs post-publish moderation)
    - [Apple asks: How do you moderate 500M iMessage images/day without breaking E2E encryption?]

47. Design a CI/CD System (Azure DevOps) [Medium-Hard]
    - Pipeline DAG & Parallel Stage Execution
    - Artifact Storage, Caching, Incremental Builds
    - Deployment Strategies (Blue-Green, Canary, Ring-Based)
    - Rollback, Feature Flags, Progressive Delivery
    - [Microsoft asks: How does Azure DevOps run 50K concurrent builds with isolation?]

48. Design a Feature Flag / Experimentation Platform [Medium-Hard]
    - Flag Evaluation (client-side vs server-side, latency)
    - Audience Targeting & Gradual Rollout (1% → 5% → 100%)
    - A/B Testing (statistical significance, metric guardrails)
    - Kill Switch & Emergency Rollback
    - [FAANG asks: How do you evaluate flags for 1B requests/day in < 5ms?]

49. Design a Multi-Tenant SaaS Platform [Hard]
    - Isolation Models (shared DB, schema-per-tenant, DB-per-tenant)
    - Noisy Neighbor Problem & Resource Quotas
    - Tenant Onboarding & Data Migration
    - Per-Tenant Customization & Configuration
    - [Microsoft asks: How does Azure/M365 isolate 10M tenants cost-effectively?]

50. Design a Distributed Lock Service (Chubby/ZooKeeper) [Hard]
    - Lease-Based Locking & Fencing Tokens
    - Lock Ordering & Deadlock Prevention
    - Session Management & Ephemeral Nodes
    - Consensus-Backed Consistency
    - [FAANG asks: What happens if a client holds a lock and gets GC-paused for 30 seconds?]

51. Design a Service Health & Dependency Manager [Medium-Hard]
    - Circuit Breaker Pattern (closed, open, half-open)
    - Bulkhead Isolation & Timeout Budgets
    - Cascading Failure Prevention
    - Graceful Degradation & Fallback Strategies
    - [FAANG asks: How do you prevent one slow downstream from taking down your entire service?]

52. Design a Secrets Management System (Azure Key Vault) [Medium-Hard]
    - HSM-Backed Key Storage
    - Automatic Rotation & Zero-Downtime Rollover
    - Access Policies & Audit Logging
    - Envelope Encryption Pattern
    - [Microsoft asks: How do you rotate a secret used by 1000 services simultaneously?]

53. Design a Global Configuration Management System [Medium]
    - Push vs Pull Config Distribution
    - Version Control & Rollback
    - Canary Config Deployment
    - Strongly Consistent vs Eventually Consistent Reads

54. Design Windows Update / iOS OTA Update System [Hard]
    - Delta Patching & Binary Diffing
    - Staged Rollout (ring-based deployment)
    - Rollback & Recovery (bricked device handling)
    - Bandwidth Optimization (P2P delivery, BITS)
    - [Microsoft asks: How do you push an update to 1.5B Windows devices without DDoS-ing yourself?]
    - [Apple asks: How does iOS update 2B devices with < 0.001% failure rate?]

55. Design a Distributed Tracing System (Jaeger/Zipkin) [Medium-Hard]
    - Trace Propagation (W3C TraceContext, B3)
    - Sampling Strategies (head-based, tail-based, adaptive)
    - Storage (columnar, time-bucketed)
    - Trace-to-Logs-to-Metrics Correlation

56. Design a Machine Learning Feature Store [Hard]
    - Online Store (low-latency serving) vs Offline Store (batch training)
    - Feature Freshness & Point-in-Time Correctness
    - Feature Registry & Discovery
    - Backfill & Time Travel
    - [FAANG asks: How do you serve 1M feature lookups/sec with < 10ms p99?]

57. Design a Multi-Region Active-Active System [Hard]
    - Conflict Resolution (CRDTs, Last-Writer-Wins, App-Level Merge)
    - Global Traffic Routing & Failover
    - Data Replication Topology (mesh, hub-spoke)
    - Regional Isolation & Blast Radius
    - [Microsoft asks: How do you keep Azure AD consistent across 60 regions?]
    - [FAANG asks: What's your conflict resolution strategy when US and EU write the same record simultaneously?]

58. Design a Capacity Planning & Auto-Scaling System [Medium-Hard]
    - Predictive vs Reactive Scaling
    - Custom Metrics & Scaling Policies
    - Warm Pool & Pre-Provisioning
    - Cost-Aware Scaling (spot instances, reserved)
    - [FAANG asks: How do you handle a 10x traffic spike that arrives in 30 seconds?]

59. Design a Data Lake / Lakehouse (Delta Lake, Iceberg) [Hard]
    - Schema Evolution & Time Travel
    - ACID on Object Storage
    - Partition Pruning & File Compaction
    - Unified Batch + Streaming Ingestion
    - [FAANG asks: How do you query petabytes of data with sub-second latency?]

60. Design an Identity & Access Management System (Azure AD / Entra) [Hard]
    - OAuth 2.0 / OIDC Flows at Scale
    - Token Issuance & Validation (JWT, opaque)
    - Conditional Access & Risk-Based Auth
    - Federation & SSO Across Tenants
    - Session Management & Token Revocation
    - [Microsoft asks: How does Entra ID authenticate 1B+ sign-ins/day with < 100ms?]

--- LOW-LEVEL DESIGN (LLD) ---

61. Design an LRU Cache [Easy] [LLD]
    - HashMap + Doubly Linked List
    - Thread-Safe with Lock Striping
    - TTL Extension & Eviction Callbacks

62. Design a Parking Lot System [Easy] [LLD]
    - Object Modeling (Vehicle, Spot, Floor, Ticket)
    - Strategy Pattern for Spot Assignment
    - Concurrent Entry/Exit Handling

63. Design BookMyShow / Ticketmaster [Medium] [LLD]
    - Seat Locking (optimistic locking + TTL)
    - Distributed Lock for Hot Events
    - Waitlist & Notification on Release
    - [FAANG asks: 10M users trying to book 50K seats simultaneously, how?]

64. Design an Elevator System [Easy-Medium] [LLD]
    - State Machine (Idle, Moving Up/Down, Stopped)
    - Scheduling (SCAN, LOOK, Destination Dispatch)
    - Multi-Elevator Coordination & Load Balancing

65. Design Splitwise [Medium] [LLD]
    - Debt Simplification (min-cash-flow algorithm)
    - Group Balances & Settlement
    - Concurrent Expense Addition

66. Design a Pub-Sub System [Medium] [LLD]
    - Topic Management, Subscriber Registry
    - At-Least-Once Delivery & Acknowledgment
    - Backpressure & Slow Consumer Detection

67. Design a Thread-Safe Blocking Queue [Medium] [LLD]
    - Producer-Consumer with Condition Variables
    - Bounded vs Unbounded
    - Priority Queue Variant

68. Design a Connection Pool [Medium] [LLD]
    - Idle Timeout & Max Lifetime
    - Health Checking & Eviction
    - Wait Queue & Timeout

69. Design an In-Memory Database (Redis) [Medium-Hard] [LLD]
    - Data Structures (String, List, Set, ZSet, Hash)
    - Persistence (RDB snapshots, AOF)
    - Single-Threaded Event Loop + IO Multiplexing
    - [FAANG asks: How does Redis achieve 100K+ ops/sec single-threaded?]

70. Design a Rate Limiter Library [Medium] [LLD]
    - Plugin Architecture (Token Bucket, Sliding Window, Leaky Bucket)
    - Configuration DSL
    - Distributed Backend (Redis, local fallback)
```

* * *

70 topics, Microsoft/Apple/FAANG-heavy, with interviewer-specific questions tagged inline. Every hard topic includes the exact curveball interviewers throw. Want me to save this to your doc alongside the full prompt?