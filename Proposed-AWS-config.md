# Prime Time Medical Research - AWS Cloud Configuration

A comprehensive AWS architecture recommendation for hosting the AI-powered medical research opportunity analysis platform - Prime Time.

*"Sleep well; the dream pipeline is deployed, monitored and under budget."*

## 🏗️ Recommended AWS Architecture Overview

This configuration provides a scalable, secure, and cost-effective solution for hosting the full-stack application including SvelteKit frontend, FastAPI backend, PostgreSQL database, and machine learning models.

**Updated with 2025 AWS best practices.**

---

## 🔧 Core Infrastructure Components

### **1. Application Hosting - FastAPI Backend**

#### **Primary Option: AWS App Runner (Development/MVP)**
```yaml
Service: AWS App Runner
Configuration:
  CPU: 2 vCPUs
  Memory: 4GB RAM
  Auto-scaling: 1-5 instances
  Health Check: /health endpoint
  Runtime: Python 3.11
  Container Port: 8000
  VPC Configuration:
    Enable VPC egress
    Private App Runner service behind Interface VPC Endpoint
  Environment Variables:
    - DATABASE_URL (from Parameter Store)
    - PUBMED_API_KEY (from Secrets Manager)
    - ML_MODEL_ENDPOINT (SageMaker endpoint)
```

**Benefits:**
- Fully managed container service
- Automatic scaling based on traffic
- Built-in load balancing
- Easy CI/CD integration
- Pay-per-use pricing

**Limitations:**
- 30-40% higher cost than Fargate
- No EFS mount support for large models
- 25 instance scaling quota
- Best for development and small workloads

#### **Recommended Production: ECS + Fargate (Graviton)**
```yaml
Service: Amazon ECS with AWS Fargate (Graviton)
Configuration:
  Platform: ARM64 (Graviton3)
  CPU: 2 vCPUs
  Memory: 4GB RAM
  Auto-scaling: 2-10 tasks
  Load Balancer: Application Load Balancer
  VPC: Private subnets only
  Service Connect: Enabled for service discovery
  Security:
    WAF: AWS Managed Rule sets + Shield Standard
    Private networking via PrivateLink
Environment:
  EFS Mount: For model artifacts and shared data
  Graviton Benefits: 50% cost reduction per vCPU
  Blue/Green Deployments: Via CodeDeploy
```

#### **Alternative High-Scale: Amazon EKS**
```yaml
Platform: Amazon EKS on Fargate
Node Groups: Graviton3 instances (m7g.large)
Scaling: Kubernetes HPA + VPA
Service Mesh: AWS App Mesh
Benefits:
  - Maximum flexibility and control
  - GPU worker node support
  - Advanced networking and security
  - Multi-tenant isolation
```

### **2. Frontend Hosting - SvelteKit Static Assets**

#### **Amazon S3 + CloudFront CDN (2025 Best Practices)**
```yaml
S3 Bucket Configuration:
  Bucket Name: prime-time-frontend-{environment}
  Static Website Hosting: Enabled
  Public Read Access: Via CloudFront only (Origin Access Control)
  Versioning: Enabled
  Lifecycle Rules: 
    - Delete old versions after 30 days
    - Abort incomplete multipart uploads after 7 days
  Intelligent Tiering: Enabled for cost optimization

CloudFront Distribution:
  Origin: S3 bucket with Origin Access Control (OAC)
  Cache Behavior: 
    - Default TTL: 86400 seconds (24 hours)
    - Max TTL: 31536000 seconds (1 year)
    - Origin Request Policy: CORS-S3Origin
  Compression: Enabled
  HTTP/2: Enabled
  HTTP/3: Enabled
  SSL Certificate: AWS Certificate Manager
  Custom Domain: your-domain.com
  Security Headers: Via CloudFront Functions
    - Strict-Transport-Security
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - Referrer-Policy: strict-origin-when-cross-origin
  Error Pages: 
    - 404 -> /index.html (SPA routing)
    - 403 -> /index.html
  Web Application Firewall: AWS WAF with managed rule sets
  Real User Monitoring: CloudWatch RUM enabled
```

**2025 Security Enhancements:**
- **Origin Access Control (OAC)** instead of legacy Origin Access Identity
- **CloudFront Functions** for security headers injection
- **AWS WAF** mandatory with Bot Control
- **Real User Monitoring** for frontend performance tracking

### **3. Database - PostgreSQL**

#### **Production Recommendation: Amazon Aurora PostgreSQL Limitless (2025)**
```yaml
Engine: Aurora PostgreSQL 16.x with Limitless Database
Cluster Configuration:
  Writer Instance: db.r7g.large (Graviton3, 2 vCPUs, 16GB RAM)
  Reader Instances: 1-3 auto-scaling replicas
  Limitless Database: Horizontal scaling for large datasets
Storage:
  Type: Aurora storage (auto-scaling)
  Encryption: AWS KMS encryption enabled
  Backup: Continuous backups to S3
Multi-AZ: Yes (cross-AZ replicas)
Backup:
  Retention: 35 days (maximum)
  Window: 03:00-04:00 UTC
  Point-in-time Recovery: Enabled
Maintenance Window: Sunday 04:00-05:00 UTC
Security Groups: Database tier (port 5432)
Subnet Group: Private subnets only
Extensions:
  - pgvector (for semantic embeddings)
  - pgaudit (for HIPAA-class logging)
  - pg_stat_statements (for query analysis)
Enhanced Monitoring: 60-second granularity
Performance Insights: Enabled with 7-day retention
```

#### **Budget Alternative: Amazon RDS PostgreSQL**
```yaml
Engine: PostgreSQL 16.x
Instance Class: db.r7g.medium (Graviton3, 1 vCPU, 8GB RAM)
Storage:
  Type: GP3 SSD
  Allocated: 100GB
  Auto Scaling: Up to 1TB
  IOPS: 3000 baseline
Multi-AZ: Yes (for production)
Backup:
  Retention: 7 days
  Window: 03:00-04:00 UTC
  Point-in-time Recovery: Enabled
Security Groups: Database tier (port 5432)
Subnet Group: Private subnets only
Extensions:
  - pgvector (for semantic embeddings)
  - pgaudit (for compliance logging)
  - pg_stat_statements (for query analysis)
```

**Connection Configuration:**
```yaml
Connection Pool:
  Min Connections: 5
  Max Connections: 20
  Connection Timeout: 30 seconds
  Idle Timeout: 300 seconds
SSL Mode: require
Security:
  Encryption at rest: KMS
  Encryption in transit: TLS 1.3
  Audit logging: pgaudit enabled
  VPC Flow Logs: Enabled
```

**Scaling Strategy:**
- **Read Replicas:** For analytics workloads and reporting
- **Aurora Limitless:** For horizontal scaling beyond single-node limits
- **Connection Pooling:** pgBouncer or RDS Proxy for connection management

---

## 🤖 Machine Learning Infrastructure (2025 Optimized)

### **1. Model Hosting - SageMaker Serverless & GPU Optimization**

#### **Primary: SageMaker Serverless Inference (Cost-Optimized)**
```yaml
Model Name: pubmedbert-keyword-generation
Configuration:
  Memory Size: 4GB
  Max Concurrency: 20
  Serverless Benefits:
    - Pay per inference (no idle costs)
    - Auto-scaling to zero
    - Sub-second cold starts
Model Storage: S3 bucket with versioning
Inference Container: Hugging Face Transformers
Environment Variables:
  - MODEL_NAME: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract
  - MAX_LENGTH: 512
  - BATCH_SIZE: 4
```

#### **High-Performance: GPU Spot Instances**
```yaml
Model Name: pubmedbert-gpu-inference
Instance Type: ml.g5.2xlarge (GPU Spot - 70% discount)
Auto Scaling:
  Min Instances: 0
  Max Instances: 2
  Target Invocations: 200 per minute
Benefits:
  - 5x faster inference than CPU
  - 70% cost savings with Spot
  - Automatic failover to on-demand
Model Storage: S3 with model artifacts
Container: Custom PyTorch container with GPU optimization
```

#### **Alternative: Real-time Endpoint**
```yaml
Model Name: pubmedbert-realtime
Instance Type: ml.m5.xlarge (4 vCPUs, 16GB RAM)
Auto Scaling:
  Min Instances: 1
  Max Instances: 3
  Target Invocations: 100 per minute
Model Storage: S3 bucket
Inference Container: Hugging Face Transformers
Environment Variables:
  - MODEL_NAME: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract
  - MAX_LENGTH: 512
  - BATCH_SIZE: 8
Monitor: InitDuration for cold start performance
```

### **2. Background Processing - AWS Batch + Lambda Optimization**

#### **Heavy Analytics: AWS Batch on Fargate Spot**
```yaml
Compute Environment:
  Type: FARGATE_SPOT
  Service Role: AWSBatchServiceRole
  Allocation Strategy: SPOT_CAPACITY_OPTIMIZED
  Bid Percentage: 80% of On-Demand price

Job Queue:
  Name: ml-analytics-queue
  Priority: 100
  Compute Environment: Fargate Spot

Job Definitions:
  clustering-analysis:
    Platform: Fargate
    vCPUs: 4
    Memory: 16GB
    Job Role: BatchExecutionRole
    Environment:
      - HDBSCAN_MIN_CLUSTER_SIZE: 5
      - UMAP_N_NEIGHBORS: 15
      - S3_BUCKET: prime-time-ml-models
    
  citation-forecasting:
    Platform: Fargate
    vCPUs: 2
    Memory: 8GB
    Environment:
      - ARIMA_ORDER: (1,1,1)
      - FORECAST_PERIODS: 12
    
  opportunity-scoring:
    Platform: Fargate
    vCPUs: 2
    Memory: 8GB
    Environment:
      - NOVELTY_WEIGHT: 0.4
      - VELOCITY_WEIGHT: 0.4
      - RECENCY_WEIGHT: 0.2
```

#### **Light Processing: Optimized Lambda Functions**
```yaml
Functions:
  quick-analysis:
    Runtime: python3.11
    Memory: 1024MB
    Timeout: 5 minutes
    Architecture: arm64 (Graviton)
    Environment:
      - MODEL_CACHE_DIR: /tmp/models
      - BATCH_SIZE: 4
    Optimization:
      - Provisioned concurrency for low latency
      - Lambda Layers for shared dependencies
      - Monitor InitDuration metrics
    
  data-preprocessing:
    Runtime: python3.11
    Memory: 512MB
    Timeout: 3 minutes
    Architecture: arm64 (Graviton)
    Triggers: SQS queue messages
```

#### **Event-Driven Processing**
```yaml
Amazon SQS:
  Queue Name: ml-analysis-queue
  Visibility Timeout: 16 minutes
  Message Retention: 14 days
  Dead Letter Queue: Enabled
  Max Receive Count: 3
  Redrive Policy: Automatic retry with exponential backoff

Amazon EventBridge:
  Rules:
    - daily-analysis-trigger: Scheduled analysis jobs
    - search-completion-trigger: Real-time processing
    - batch-job-monitor: Job status notifications
  Targets:
    - AWS Batch jobs for heavy processing
    - Lambda functions for light processing
    - SNS topics for notifications
```

### **3. Semantic Search - OpenSearch Serverless**
```yaml
Service: Amazon OpenSearch Serverless
Collection Type: Search
Configuration:
  Compute Units: Auto-scaling
  Storage: Pay-per-use
  Index Strategy: 
    - Article embeddings index
    - Keyword similarity index
    - Citation network index
Security:
  Network: VPC access only
  Encryption: At rest and in transit
  Access Control: Fine-grained IAM policies
Use Cases:
  - Vector similarity search for articles
  - Full-text search with semantic ranking
  - Real-time research trend analysis
```

---

## 🚀 Supporting Services

### **1. Caching - Amazon ElastiCache (Graviton Optimized)**

#### **Redis Configuration (2025 Best Practices)**
```yaml
Engine: Redis 7.x
Node Type: cache.t4g.small (Graviton3, 2 vCPUs, 1.5GB RAM)
Number of Nodes: 2 (production with replication)
Subnet Group: Private subnets
Security Groups: Cache tier (port 6379)
Cluster Mode: Disabled (single primary with replica)
Backup:
  Snapshot Retention: 5 days
  Snapshot Window: 05:00-06:00 UTC
  Automatic Failover: Enabled
Encryption:
  At Rest: Enabled
  In Transit: TLS 1.3
Auth Token: Required (from Secrets Manager)
Use Cases:
  - API response caching (TTL: 5-60 minutes)
  - Session storage (TTL: 24 hours)
  - Temporary ML results (TTL: 24 hours)
  - Rate limiting counters (TTL: 1 hour)

Monitoring:
  CloudWatch Metrics: CPU, Memory, Cache Hit Ratio
  Alarms: Memory usage > 80%, CPU > 70%
  Restore Drills: Monthly automated tests
```

**Why t4g.small over t3.micro:**
- Graviton3 processor (better price/performance)
- 1.5GB memory vs 512MB (prevents OOM issues)
- Better reliability for snapshot restore operations
- 20% cost reduction with ARM64 architecture

### **2. File Storage - Amazon S3**

#### **Bucket Strategy**
```yaml
Buckets:
  prime-time-ml-models:
    Purpose: ML model artifacts and embeddings
    Storage Class: Standard
    Versioning: Enabled
    Lifecycle: Transition to IA after 30 days
    
  prime-time-exports:
    Purpose: CSV exports and user downloads
    Storage Class: Standard
    Lifecycle: Delete after 7 days
    
  prime-time-logs:
    Purpose: Application logs and backups
    Storage Class: Standard
    Lifecycle: Transition to Glacier after 90 days
    
  prime-time-static:
    Purpose: Frontend assets (if not using App Runner)
    Storage Class: Standard
    Public Access: Via CloudFront only
```

### **3. Monitoring & Logging**

#### **Amazon CloudWatch (Enhanced Monitoring)**
```yaml
Log Groups:
  - /aws/ecs/prime-time-api (if using ECS)
  - /aws/apprunner/prime-time-api (if using App Runner)
  - /aws/lambda/clustering-analysis
  - /aws/lambda/citation-forecasting
  - /aws/lambda/opportunity-scoring
  - /aws/rds/prime-time-db
  - /aws/waf/prime-time-waf

Log Retention: 30-90 days (to avoid $1K+ monthly bills)
Log Insights: Enabled for query analysis

Metrics & Alarms:
  High Priority (Immediate Response):
    - Application Error Rate > 5%
    - Database CPU > 90%
    - API Response Time > 5 seconds
    - SageMaker Endpoint Failures > 10%
    
  Medium Priority:
    - Database Connections > 80%
    - Lambda Cold Starts > 20%
    - Cache Miss Rate > 50%
    - Disk Space > 85%
    
  Cost Monitoring:
    - Daily cost increase > 20%
    - Service Quotas approaching limits

Dashboards:
  - Application Performance (API metrics, error rates)
  - Database Health (CPU, connections, slow queries)
  - ML Model Performance (latency, accuracy, throughput)
  - Cost Optimization (spend analysis, waste detection)
  - Security Dashboard (WAF blocks, failed authentications)

Custom Metrics:
  Application Metrics:
    prime_time.search.duration: Search execution time
    prime_time.articles.ingested: Articles processed per hour
    prime_time.ml.processing_time: ML analysis duration
    prime_time.opportunity.score_calculated: Scores computed
    
  Business Metrics:
    prime_time.users.active: Active user sessions
    prime_time.searches.completed: Successful searches
    prime_time.exports.generated: CSV exports created
```

#### **AWS X-Ray Tracing (Enhanced)**
```yaml
Services to Trace:
  - ECS/App Runner (FastAPI)
  - Lambda functions
  - SageMaker endpoints
  - RDS queries
  - ElastiCache operations
  - S3 operations
  
Sampling Rules:
  - 100% of all requests (until baselines known)
  - 100% of error requests (always)
  - Custom rules for ML endpoints
  - Reduced to 10% after establishing performance baselines

Trace Analysis:
  - Service Map visualization
  - Performance insights
  - Error correlation
  - Dependency mapping
```

#### **Real User Monitoring (CloudWatch RUM)**
```yaml
SvelteKit Frontend Monitoring:
  Application Name: prime-time-frontend
  Domain: your-domain.com
  Session Sample Rate: 0.1 (10% of sessions)
  
Metrics Collected:
  - Page load times
  - Core Web Vitals (LCP, FID, CLS)
  - JavaScript errors
  - User interactions
  - Network performance
  - Browser compatibility

Dashboards:
  - Frontend Performance
  - User Experience Metrics
  - Error Tracking
  - Browser Analytics
```

---

## 💰 Cost Analysis (Updated 2025 Reality Check)

### **Development Environment** (Monthly Estimates)

```yaml
Compute Services:
  App Runner (development): $50-80
  Lambda (occasional processing): $10-20
  SageMaker Serverless (pay-per-use): $20-40

Storage & Database:
  RDS PostgreSQL (db.t4g.micro): $20-30
  S3 Storage (all buckets): $10-20
  ElastiCache (cache.t4g.small): $25-35

Networking & CDN:
  CloudFront: $5-15
  Data Transfer: $5-10
  NAT Gateway: $45 (2 AZs)

Monitoring & Security:
  CloudWatch (with log retention): $15-25
  X-Ray: $5-10
  WAF: $10-15

Total Development: $200-305/month
```

### **Production Environment** (Realistic Monthly Estimates)

```yaml
Compute Services:
  ECS Fargate (Graviton, 2 always-on): $200-400
  Lambda (heavy processing): $30-50
  SageMaker Endpoints (auto-scaled): $164-492
  AWS Batch (Spot instances): $50-100

Storage & Database:
  Aurora PostgreSQL (db.r7g.large): $200-350
  S3 Storage (all buckets): $40-70
  ElastiCache (cache.t4g.small, replicated): $50-70
  OpenSearch Serverless: $100-200

Networking & CDN:
  CloudFront (with security features): $30-60
  Data Transfer: $25-50
  Application Load Balancer: $25-35
  NAT Gateway: $90 (2 AZs)

Monitoring & Security:
  CloudWatch (3GB/day logs + custom metrics): $75-120
  X-Ray (100% sampling initially): $20-40
  WAF with Bot Control: $20-40
  Secrets Manager: $5-15

Total Production: $1,125-1,897/month
```

### **Cost Optimization Strategies**

#### **Immediate Savings (30-50% reduction)**
```yaml
Graviton Migration:
  ECS Fargate: 20% savings with ARM64
  RDS: 20% cost reduction with Graviton3
  ElastiCache: 20% savings with t4g instances
  Lambda: 15% cost reduction with arm64

Compute Savings Plans:
  1-year commitment: 20% savings
  3-year commitment: 40% savings
  Covers: App Runner, Fargate, Lambda

Storage Optimization:
  S3 Intelligent Tiering: Automatic cost optimization
  Lifecycle policies: Move logs to Glacier after 90 days
  Reserved Capacity: For predictable storage needs

Spot Instances:
  AWS Batch: 70% savings for ML workloads
  SageMaker Training: 90% cost reduction
  Development environments: 60-70% savings
```

#### **Long-term Cost Management**
```yaml
Monthly Reviews:
  CloudWatch Cost Dashboard: Track spend by service
  AWS Cost Explorer: Identify cost trends
  Trusted Advisor: Right-sizing recommendations
  Service Quotas: Monitor usage vs limits

Automated Cost Controls:
  Budget Alerts: Email/SMS when exceeding thresholds
  Auto-scaling policies: Scale down during low usage
  Scheduled start/stop: Development environments
  Cost allocation tags: Track costs by team/project

Reserved Instances Strategy:
  Year 1: Spot and on-demand to establish baselines
  Year 2: Purchase RIs for consistent workloads
  Year 3: Optimize mix of RIs, Savings Plans, and Spot
```

### **Budget Optimization Options**

#### **Ultra-Lightweight Configuration** (~$80-120/month)
```yaml
Alternative Services:
  AWS Lightsail VPS: $40-80/month
    - Instance: 8GB RAM, 4 vCPUs
    - Includes: Compute, networking, storage
    - Database: Lightsail PostgreSQL $15-30/month
  
  Frontend: S3 + CloudFront: $10-20/month
  Lambda: On-demand ML processing: $15-30/month
  
Trade-offs:
  - Manual scaling only
  - Limited ML capabilities
  - Basic monitoring
  - Single availability zone
  - No enterprise features
```

#### **Enterprise High-Performance Configuration** (~$3000-5000/month)
```yaml
Enhanced Services:
  EKS Cluster: $500-1000/month
  Aurora Limitless: $400-800/month
  Multiple GPU SageMaker Endpoints: $1000-2000/month
  Enhanced Security & Compliance: $200-400/month
  24/7 Support (Business): $100/month
  
Benefits:
  - Kubernetes orchestration
  - Unlimited database scaling
  - GPU acceleration for all models
  - Advanced security features
  - High availability across regions
  - Professional support
```

---

## 🛡️ Security Configuration (HIPAA-Class Standards)

### **Network Security (Zero Trust Architecture)**

#### **VPC Configuration (PrivateLink Everywhere)**
```yaml
VPC CIDR: 10.0.0.0/16

Subnets:
  Public Subnets (Load Balancers Only):
    - 10.0.1.0/24 (AZ-1)
    - 10.0.2.0/24 (AZ-2)
    Purpose: ALB, NAT gateways only
    
  Private Subnets (Application Tier):
    - 10.0.10.0/24 (AZ-1)
    - 10.0.11.0/24 (AZ-2)
    Purpose: ECS/Fargate, Lambda (VPC)
    
  Database Subnets (Isolated):
    - 10.0.20.0/24 (AZ-1)
    - 10.0.21.0/24 (AZ-2)
    Purpose: RDS, ElastiCache only

Network ACLs: Restrictive rules per subnet tier
NAT Gateways: 2 (one per AZ) with EIP
Internet Gateway: 1 (public subnets only)
Route Tables: Separate for each tier

VPC Endpoints (PrivateLink):
  - S3 (Gateway endpoint)
  - DynamoDB (Gateway endpoint)
  - SageMaker Runtime (Interface endpoint)
  - Secrets Manager (Interface endpoint)
  - CloudWatch Logs (Interface endpoint)
  - ECR (Interface endpoint)

VPC Flow Logs:
  Destination: CloudWatch Logs
  Filter: ALL traffic (Accept and Reject)
  Retention: 90 days
```

#### **Security Groups (Least Privilege)**
```yaml
Web Tier (ALB):
  Inbound:
    - HTTPS (443) from 0.0.0.0/0
    - HTTP (80) from 0.0.0.0/0 (redirect to HTTPS)
  Outbound: To Application Tier SG only

Application Tier:
  Inbound:
    - HTTP (8000) from Web Tier SG only
    - HTTPS (443) from Web Tier SG only
  Outbound: 
    - Database Tier SG (port 5432)
    - Cache Tier SG (port 6379)
    - HTTPS (443) to 0.0.0.0/0 (external APIs)

Database Tier:
  Inbound:
    - PostgreSQL (5432) from Application Tier SG only
  Outbound: None

Cache Tier:
  Inbound:
    - Redis (6379) from Application Tier SG only
  Outbound: None

Lambda Security Group:
  Inbound: None
  Outbound: Database and Cache tiers only
```

### **Access Control & Encryption (Zero Trust)**

#### **IAM Roles & Policies (Condition-Based)**
```yaml
ECS Task Execution Role:
  Policies:
    - ECS Task Execution (AWS managed)
    - Custom policy with conditions:
      Condition:
        StringEquals:
          aws:SourceVpc: ${VpcId}
          s3:ResourceAccount: ${AWS::AccountId}

ECS Task Role:
  Policies:
    - RDS access (specific database ARN)
    - S3 read/write (specific bucket ARNs)
    - SageMaker invoke endpoint (specific endpoint ARN)
    - CloudWatch logs write (specific log group)
    - Parameter Store read (path-based)
    - Secrets Manager read (resource-based)
  Conditions:
    - aws:SourceVpc for all actions
    - Time-based access (working hours only)
    - MFA required for sensitive operations

Lambda Execution Roles:
  Policies:
    - VPC access (when in VPC)
    - RDS access (connection string from Secrets Manager)
    - S3 read/write (model artifacts only)
    - CloudWatch logs write
    - SQS send/receive (specific queue ARNs)
  Conditions:
    - aws:SourceVpc for VPC Lambda functions
    - Resource-specific access only

SageMaker Role:
  Policies:
    - S3 model access (model bucket only)
    - CloudWatch logs write
    - ECR read (for custom containers)
  Conditions:
    - s3:ResourceAccount for bucket access
    - Time-based execution windows
```

#### **Encryption Configuration (End-to-End)**
```yaml
At Rest Encryption:
  RDS: AWS KMS Customer Managed Key (CMK)
    - Key rotation: Annual automatic
    - Cross-region replica keys
  S3: SSE-KMS with CMK
    - Bucket key enabled for cost optimization
    - Lifecycle encryption verification
  ElastiCache: 
    - Encryption at rest with KMS CMK
    - Auth token encryption
  Lambda: 
    - Environment variables encrypted with KMS
    - Code signing for deployment integrity
  EBS Volumes: KMS encryption for all volumes

In Transit Encryption:
  CloudFront: TLS 1.3 minimum, HSTS headers
  ALB: TLS 1.3, SSL policy ELBSecurityPolicy-TLS13-1-2-2021-06
  RDS: SSL/TLS required, certificate verification
  ElastiCache: TLS 1.3 enabled, client certificate auth
  SageMaker: HTTPS endpoints only
  Internal: All service-to-service communication encrypted
```

### **Secrets Management (Automated Rotation)**

#### **AWS Secrets Manager (Auto-Rotation)**
```yaml
Secrets:
  prime-time/database/master:
    Description: RDS master password
    Rotation: Every 30 days (automatic)
    Lambda: AWS managed rotation function
    Value:
      username: admin
      password: ${auto-generated-32-char}
      engine: postgres
      host: ${rds-endpoint}
      port: 5432
      dbname: prime_time_db
      
  prime-time/database/app:
    Description: Application database user
    Rotation: Every 60 days
    Value:
      username: app_user
      password: ${auto-generated-32-char}
      permissions: SELECT, INSERT, UPDATE, DELETE
      
  prime-time/api-keys:
    Description: External API keys
    Rotation: Manual (quarterly)
    Value:
      pubmed_api_key: ${encrypted-key}
      crossref_api_key: ${encrypted-key}
      openai_api_key: ${encrypted-key}
      
  prime-time/redis/auth:
    Description: Redis AUTH token
    Rotation: Every 90 days
    Value:
      auth_token: ${auto-generated-64-char}

Cross-Region Replication:
  Primary: us-east-1
  Replica: us-west-2
  Sync: Automatic for disaster recovery
```

#### **AWS Systems Manager Parameter Store (Configuration)**
```yaml
Standard Parameters:
  /prime-time/config/max-results: 100
  /prime-time/config/cache-ttl: 3600
  /prime-time/ml/model-version: v1.2.3
  /prime-time/ml/batch-size: 8
  /prime-time/alerts/email: octavian.andronic@umfcd.ro
  
Secure Parameters (KMS Encrypted):
  /prime-time/database/connection-string: ${encrypted-value}
  /prime-time/jwt/secret: ${encrypted-value}
  /prime-time/encryption/data-key: ${encrypted-value}

Access Control:
  Read Access: ECS tasks, Lambda functions
  Write Access: CI/CD pipeline only
  Audit: All parameter access logged
```

### **Compliance & Monitoring (HIPAA-Ready)**

#### **AWS Config (Compliance as Code)**
```yaml
Config Rules:
  - encrypted-volumes: All EBS volumes encrypted
  - rds-encrypted: All RDS instances encrypted
  - s3-bucket-ssl-requests-only: HTTPS only
  - iam-password-policy: Strong password requirements
  - root-mfa-enabled: MFA required for root account
  - cloudtrail-enabled: CloudTrail logging active
  - guardduty-enabled-centralized: Threat detection active

Conformance Packs:
  - Security Best Practices
  - HIPAA Security
  - PCI DSS (if applicable)
  - SOC 2 Type II

Remediation:
  Auto-remediation for non-compliant resources
  SNS notifications for manual remediation required
```

#### **Security Monitoring (24/7)**
```yaml
AWS CloudTrail:
  Multi-region trail enabled
  Log file validation: Enabled
  S3 bucket: Separate security account
  CloudWatch integration: Real-time analysis
  Retention: 7 years (compliance requirement)

AWS GuardDuty:
  Threat detection: Enabled in all regions
  Finding types: All categories enabled
  S3 protection: Enabled
  EKS protection: Enabled (if using EKS)
  Malware protection: Enabled
  Integration: Security Hub + SNS alerts

AWS Security Hub:
  Central security dashboard
  Multi-account aggregation
  Custom insights and filters
  Automated remediation workflows
  Integration with third-party tools

AWS Inspector:
  Network assessments: Weekly
  Agent-based assessments: Continuous
  Container image scanning: On push
  Lambda function scanning: Enabled
  Vulnerability management: Integrated
```

#### **WAF Configuration (Advanced Protection)**
```yaml
AWS WAF v2:
  Managed Rule Groups:
    - AWS Core Rule Set
    - AWS Known Bad Inputs
    - AWS SQL Database Protection
    - AWS Linux Operating System
    - AWS POSIX Operating System
    - AWS Bot Control (paid tier)
    
  Custom Rules:
    - Rate limiting: 2000 requests per 5 minutes per IP
    - Geo-blocking: Allow specific countries only
    - IP reputation: Block known bad IPs
    - Size restrictions: Limit request body size
    
  Monitoring:
    - CloudWatch metrics for all rules
    - Sampled requests logging
    - Real-time monitoring dashboard
    - Automated blocking of repeat offenders

AWS Shield Advanced:
  DDoS protection for critical applications
  24/7 DDoS Response Team access
  Cost protection for scaling during attacks
  Real-time attack notifications
```

---

## 🔄 Deployment Strategy

### **Infrastructure as Code**

#### **AWS CDK (Recommended)**
```typescript
// Example CDK structure
const app = new cdk.App();

const vpcStack = new VpcStack(app, 'PrimeTimeVpc');
const databaseStack = new DatabaseStack(app, 'PrimeTimeDatabase', {
  vpc: vpcStack.vpc
});
const applicationStack = new ApplicationStack(app, 'PrimeTimeApp', {
  vpc: vpcStack.vpc,
  database: databaseStack.database
});
const mlStack = new MachineLearningStack(app, 'PrimeTimeML', {
  vpc: vpcStack.vpc
});
```

#### **Alternative: Terraform**
```hcl
# Example Terraform structure
module "vpc" {
  source = "./modules/vpc"
}

module "database" {
  source = "./modules/database"
  vpc_id = module.vpc.vpc_id
}

module "application" {
  source = "./modules/application"
  vpc_id = module.vpc.vpc_id
  database_endpoint = module.database.endpoint
}
```

### **CI/CD Pipeline**

#### **AWS CodePipeline Configuration**
```yaml
Pipeline Stages:
  Source:
    Provider: GitHub
    Repository: https://github.com/rosmae/AI-for-Scientific-Articles-Analysis
    Branch: main
    
  Build:
    Provider: CodeBuild
    Environment: Amazon Linux 2
    Runtime: Python 3.11
    Build Commands:
      - pip install -r requirements.txt
      - python -m pytest
      - docker build -t prime-time-api .
      
  Deploy:
    Provider: App Runner
    Configuration: Automatic deployment
    Environment Variables: From Parameter Store
```

### **Environment Management**

#### **Multi-Environment Setup**
```yaml
Environments:
  Development:
    Domain: dev.domain.com
    Database: Single AZ
    Scaling: 1-2 instances
    ML: Development endpoints
    
  Staging:
    Domain: staging.domain.com
    Database: Multi-AZ
    Scaling: 1-3 instances
    ML: Production-like endpoints
    
  Production:
    Domain: domain.com
    Database: Multi-AZ + Read Replicas
    Scaling: 2-5 instances
    ML: Production endpoints
    Monitoring: Enhanced
```

---

## 📊 Monitoring & Observability

### **Application Performance Monitoring**

#### **CloudWatch Dashboards**
```yaml
API Performance Dashboard:
  Widgets:
    - Request count and error rate
    - Response time percentiles (p50, p95, p99)
    - Database connection pool metrics
    - SageMaker endpoint latency
    - Cache hit/miss rates

Database Health Dashboard:
  Widgets:
    - CPU utilization
    - Database connections
    - Read/write IOPS
    - Query performance
    - Slow query logs

ML Model Performance Dashboard:
  Widgets:
    - Model inference latency
    - Prediction accuracy metrics
    - Resource utilization
    - Error rates by model
```

#### **Custom Metrics**
```yaml
Application Metrics:
  prime_time.search.duration: Search execution time
  prime_time.articles.ingested: Articles processed per hour
  prime_time.ml.processing_time: ML analysis duration
  prime_time.opportunity.score_calculated: Scores computed
  
Business Metrics:
  prime_time.users.active: Active user sessions
  prime_time.searches.completed: Successful searches
  prime_time.exports.generated: CSV exports created
```

### **Alerting Strategy**

#### **Critical Alerts** (Immediate Response)
```yaml
High Priority:
  - Application Error Rate > 5%
  - Database CPU > 90%
  - API Response Time > 5 seconds
  - SageMaker Endpoint Failures > 10%
  
Medium Priority:
  - Database Connections > 80%
  - Lambda Cold Starts > 20%
  - Cache Miss Rate > 50%
  - Disk Space > 85%
  
Low Priority:
  - Daily cost increase > 20%
  - Slow query detected
  - Model accuracy degradation
```

#### **Notification Channels**
```yaml
SNS Topics:
  critical-alerts:
    Endpoints:
      - Email: octavian.andronic@umfcd.ro
      - Email: raul.radulescu00@e-uvt.ro
      - SMS: (to be configured)
      - Slack: #alerts-critical
    Encryption: KMS encrypted messages
    
  monitoring-alerts:
    Endpoints:
      - Email: octavian.andronic@umfcd.ro
      - Email: raul.radulescu00@e-uvt.ro
      - Slack: #alerts-monitoring
    
  security-alerts:
    Endpoints:
      - Email: security-team@company.com
      - PagerDuty: Security team escalation
      - Slack: #security-incidents
    Priority: Immediate response required

Lambda-based Alerting:
  Custom alert processor for intelligent filtering
  Alert correlation to reduce noise
  Automatic ticket creation for critical issues
  Escalation rules based on severity and time
```

---

## 🔧 Operational Procedures

### **Backup & Disaster Recovery**

#### **Database Backup Strategy**
```yaml
RDS Automated Backups:
  Retention: 7 days
  Backup Window: 03:00-04:00 UTC
  Point-in-time Recovery: Enabled
  
Manual Snapshots:
  Frequency: Before major deployments
  Retention: 30 days
  Cross-region Copy: Enabled (for DR)

Application Data:
  S3 Cross-region Replication: Enabled
  Model Artifacts: Versioned in S3
  Configuration: Stored in Parameter Store
```

#### **Disaster Recovery Plan (Enhanced)**
```yaml
RTO (Recovery Time Objective): 2 hours (improved from 4)
RPO (Recovery Point Objective): 15 minutes (improved from 1 hour)

Multi-Region Setup:
  Primary Region: us-east-1
  DR Region: us-west-2
  Cross-region replication: Automated

DR Procedures:
  1. Automated failover triggers (Route 53 health checks)
  2. Activate standby Aurora cluster in DR region
  3. Update DNS to DR region (Route 53 weighted routing)
  4. Deploy application to pre-warmed ECS cluster
  5. Restore S3 data from cross-region replicas
  6. Validate all services operational
  7. Notify stakeholders of DR activation

Quarterly DR Drills:
  - Complete failover test
  - Performance validation
  - Documentation updates
  - Team training exercises
  - Cold start time measurement

Route 53 Health Checks:
  Primary endpoint monitoring
  Automatic DNS failover
  Regional health checks
  Application-level health validation
```

### **Scaling Procedures**

#### **Horizontal Scaling Triggers**
```yaml
Auto Scaling Metrics:
  Scale Out:
    - CPU > 70% for 5 minutes
    - Memory > 80% for 5 minutes
    - Request count > 1000/minute
    
  Scale In:
    - CPU < 30% for 10 minutes
    - Memory < 50% for 10 minutes
    - Request count < 200/minute

Manual Scaling Events:
  - Marketing campaigns
  - Conference presentations
  - Research publication releases
```

---

## 📝 Additional Recommendations

### **Data Classification & Governance**

#### **Data Tagging Strategy**
```yaml
Required Tags (All Resources):
  Environment: dev/staging/prod
  Project: prime-time-medical-research
  Owner: team-name
  Cost-Center: research-dept
  Data-Classification: public/internal/confidential
  Backup-Required: true/false
  Compliance: hipaa/gdpr/none

Automated Tagging:
  Lambda function for tag enforcement
  CloudFormation/CDK automatic tagging
  Cost allocation by tags
  Compliance reporting by classification
```

#### **Service Quotas Monitoring**
```yaml
Monitored Quotas:
  ECS: Running tasks per service
  Lambda: Concurrent executions
  SageMaker: Endpoint instances
  RDS: DB instances and storage
  S3: Requests per second
  VPC: Security groups and rules

Alerts:
  Warning: 80% of quota reached
  Critical: 90% of quota reached
  Action: Automatic quota increase request (where possible)
```

### **Updated 2025 Reference Architecture**

#### **Next-Generation Stack**
```yaml
Compute Layer:
  Primary: ECS Fargate with Graviton3 processors
  ML Workloads: AWS Batch on Fargate Spot
  Edge Computing: Lambda@Edge for global performance
  
Database Layer:
  Primary: Aurora PostgreSQL Limitless
  Analytics: Amazon Redshift Serverless
  Vector Search: OpenSearch Serverless
  Caching: ElastiCache with Graviton3

AI/ML Services:
  Model Hosting: SageMaker Serverless Inference
  Training: SageMaker Training Jobs on Spot
  Vector Embeddings: Amazon Bedrock integration
  Search: OpenSearch with neural search

Security Posture:
  Zero Trust: PrivateLink everywhere, no public IPs
  Encryption: Customer-managed KMS keys
  Monitoring: Security Hub + GuardDuty + Inspector
  Compliance: AWS Config Conformance Packs

Observability:
  Metrics: CloudWatch with custom dashboards
  Tracing: X-Ray with 100% sampling (initially)
  Logs: Centralized with 90-day retention
  APM: CloudWatch Application Insights
```

### **Operational Excellence Framework**

#### **Final Checklist**
```yaml
Development Practices:
  1. Infrastructure as Code: CDK with unit tests
  2. CI/CD Pipeline: Automated testing and deployment
  3. Configuration Management: Parameter Store + Secrets Manager
  4. Version Control: Git with branch protection
  5. Code Quality: Automated linting and security scanning

Monitoring & Alerting:
  1. Start small, measure, right-size monthly
  2. Implement chaos engineering drills
  3. Monitor business metrics, not just technical ones
  4. Set up intelligent alerting to reduce noise
  5. Regular review of logs and metrics

Security Practices:
  1. Rotate every secret on an auditable schedule
  2. Implement least privilege access everywhere
  3. Regular security assessments and penetration testing
  4. Automated compliance checking with Config
  5. Incident response playbooks and training

Cost Management:
  1. Monthly cost reviews and optimization
  2. Reserved Instance strategy after baseline establishment
  3. Automated resource lifecycle management
  4. Cost allocation tags for accountability
  5. Regular right-sizing based on actual usage

Documentation & Knowledge:
  1. Runbooks for all operational procedures
  2. Architecture decision records (ADRs)
  3. Document why you didn't choose certain options
  4. Regular team training and knowledge sharing
  5. Post-incident reviews and lessons learned

Regional Strategy:
  1. Design the second region now, not later
  2. Plan for data sovereignty requirements
  3. Consider latency implications for global users
  4. Implement proper DNS strategies for failover
  5. Regular disaster recovery testing
```

#### **Continuous Improvement Process**
```yaml
Monthly Reviews:
  - Cost optimization opportunities
  - Performance metrics analysis
  - Security posture assessment
  - Capacity planning updates

Quarterly Activities:
  - Disaster recovery drills
  - Security penetration testing
  - Architecture review sessions
  - Technology stack evaluation

Annual Planning:
  - Multi-year capacity forecasting
  - Technology roadmap updates
  - Compliance certification renewals
  - Team training and certification

Success Metrics:
  - System availability > 99.9%
  - Cost per transaction trending down
  - Security incidents = 0
  - Mean time to recovery < 2 hours
  - Customer satisfaction > 95%
```

### **Missing Pieces from Original Design**

#### **Enhanced Capabilities**
```yaml
Threat Modeling:
  - Application-level threat assessment
  - Data flow security analysis
  - Attack surface mapping
  - Regular security reviews

Bot Protection:
  - WAF Bot Control for intelligent filtering
  - CAPTCHA integration for suspicious traffic
  - Rate limiting with progressive penalties
  - User behavior analytics

Advanced Analytics:
  - Real-time dashboards for business metrics
  - Predictive analytics for capacity planning
  - Cost forecasting and optimization
  - Performance trend analysis

Integration Capabilities:
  - API Gateway for external integrations
  - Event-driven architecture with EventBridge
  - Webhook support for third-party services
  - GraphQL API for flexible data access
```

---

## 🚀 Getting Started (Phased Approach)

### **Phase 1: Foundation & Security** (Week 1-2)
```yaml
Infrastructure Setup:
  1. Create VPC with proper network segmentation
  2. Set up VPC endpoints for PrivateLink connectivity
  3. Deploy KMS keys for encryption
  4. Configure AWS Config and CloudTrail
  5. Set up Secrets Manager with rotation
  6. Enable GuardDuty and Security Hub

Security Baseline:
  1. Implement least privilege IAM policies
  2. Configure security groups with minimal access
  3. Set up WAF with basic rule sets
  4. Enable encryption for all data stores
  5. Create security monitoring dashboards

Development Environment:
  1. Deploy lightweight configuration for testing
  2. Set up CI/CD pipeline with security scanning
  3. Configure monitoring and alerting
  4. Test disaster recovery procedures
```

### **Phase 2: Core Application & Database** (Week 3-4)
```yaml
Database Deployment:
  1. Deploy Aurora PostgreSQL in private subnets
  2. Configure read replicas for analytics
  3. Set up automated backups and encryption
  4. Install pgvector and pgaudit extensions
  5. Test database performance and tuning

Application Platform:
  1. Deploy ECS cluster with Fargate (Graviton)
  2. Configure auto-scaling policies
  3. Set up Application Load Balancer with WAF
  4. Deploy FastAPI application with health checks
  5. Configure service discovery and networking

Frontend Deployment:
  1. Set up S3 bucket with Origin Access Control
  2. Configure CloudFront with security headers
  3. Deploy SvelteKit application
  4. Enable CloudWatch RUM for monitoring
  5. Test CDN performance globally
```

### **Phase 3: Machine Learning & Analytics** (Week 5-6)
```yaml
ML Infrastructure:
  1. Deploy SageMaker Serverless endpoints
  2. Set up AWS Batch for heavy ML workloads
  3. Configure OpenSearch Serverless for vector search
  4. Deploy Lambda functions for light processing
  5. Set up SQS queues for async processing

Model Deployment:
  1. Deploy PubMedBERT model to SageMaker
  2. Test inference performance and scaling
  3. Configure GPU Spot instances for training
  4. Set up model versioning and artifacts
  5. Implement A/B testing for model updates

Data Pipeline:
  1. Set up ETL processes for article ingestion
  2. Configure vector embedding generation
  3. Implement semantic search capabilities
  4. Set up real-time analytics dashboards
  5. Test end-to-end ML workflows
```

### **Phase 4: Production Hardening** (Week 7-8)
```yaml
Performance Optimization:
  1. Implement caching with ElastiCache
  2. Optimize database queries and indexes
  3. Configure CDN caching strategies
  4. Set up connection pooling
  5. Load test all components

Security Hardening:
  1. Enable advanced WAF rules and Bot Control
  2. Implement network-level security scanning
  3. Configure automated secret rotation
  4. Set up compliance monitoring
  5. Conduct penetration testing

Operational Excellence:
  1. Set up comprehensive monitoring dashboards
  2. Configure intelligent alerting with SNS
  3. Implement chaos engineering tests
  4. Create operational runbooks
  5. Train team on incident response

Multi-Region Setup:
  1. Deploy disaster recovery environment
  2. Configure cross-region replication
  3. Set up Route 53 health checks
  4. Test automated failover procedures
  5. Document DR processes
```

### **Phase 5: Cost Optimization & Scaling** (Week 9-10)
```yaml
Cost Management:
  1. Implement Reserved Instance strategy
  2. Configure Savings Plans for compute
  3. Set up cost monitoring and alerts
  4. Optimize storage classes and lifecycle policies
  5. Regular cost review processes

Scaling Preparation:
  1. Configure auto-scaling for all tiers
  2. Set up service quotas monitoring
  3. Implement horizontal scaling strategies
  4. Test scaling under load
  5. Plan capacity for growth

Documentation & Training:
  1. Complete operational runbooks
  2. Document architecture decisions
  3. Create user training materials
  4. Set up knowledge sharing processes
  5. Plan for ongoing maintenance
```

---

*"The design is thorough and mostly modern, with clear separation of tiers, Infrastructure-as-Code discipline, and a credible first-pass cost model."*

*"Sleep well; the dream pipeline is deployed, monitored and under budget."*

---

**This AWS configuration provides a robust, scalable, and secure infrastructure for the Prime Time Medical Research platform, designed to handle the computational demands of AI-powered medical research analysis while maintaining cost efficiency and operational excellence.**

*Configuration Last Updated: June 30, 2025*