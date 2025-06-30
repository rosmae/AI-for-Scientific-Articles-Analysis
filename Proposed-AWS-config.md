# Prime Time Medical Research - AWS Cloud Configuration

A comprehensive AWS architecture recommendation for hosting the AI-powered medical research opportunity analysis platform - Prime Time.

## 🏗️ Recommended AWS Architecture Overview

This configuration provides a scalable, secure, and cost-effective solution for hosting the full-stack application including SvelteKit frontend, FastAPI backend, PostgreSQL database, and machine learning models.

---

## 🔧 Core Infrastructure Components

### **1. Application Hosting - FastAPI Backend**

#### **Primary Option: AWS App Runner**
```yaml
Service: AWS App Runner
Configuration:
  CPU: 2 vCPUs
  Memory: 4GB RAM
  Auto-scaling: 1-5 instances
  Health Check: /health endpoint
  Runtime: Python 3.11
  Container Port: 8000
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

#### **Alternative: AWS Elastic Beanstalk**
```yaml
Platform: Python 3.11 running on Amazon Linux 2
Instance Type: t3.medium (2 vCPUs, 4GB RAM)
Auto Scaling: 1-5 instances
Load Balancer: Application Load Balancer (ALB)
Health Check: /health endpoint
Environment: Production
```

### **2. Frontend Hosting - SvelteKit Static Assets**

#### **Amazon S3 + CloudFront CDN**
```yaml
S3 Bucket Configuration:
  Bucket Name: prime-time-frontend-{environment}
  Static Website Hosting: Enabled
  Public Read Access: Via CloudFront only
  Versioning: Enabled
  Lifecycle Rules: Delete old versions after 30 days

CloudFront Distribution:
  Origin: S3 bucket
  Cache Behavior: 
    - Default TTL: 86400 seconds (24 hours)
    - Max TTL: 31536000 seconds (1 year)
  Compression: Enabled
  HTTP/2: Enabled
  SSL Certificate: AWS Certificate Manager
  Custom Domain: your-domain.com
  Error Pages: 
    - 404 -> /index.html (SPA routing)
    - 403 -> /index.html
```

### **3. Database - PostgreSQL**

#### **Amazon RDS PostgreSQL**
```yaml
Engine: PostgreSQL 15.x
Instance Class: db.t3.medium (2 vCPUs, 4GB RAM)
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
Maintenance Window: Sunday 04:00-05:00 UTC
Security Groups: Database tier (port 5432)
Subnet Group: Private subnets only
Extensions:
  - pgvector (for semantic embeddings)
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
```

---

## 🤖 Machine Learning Infrastructure

### **1. Model Hosting - Amazon SageMaker**

#### **PubMedBERT Model Endpoint**
```yaml
Model Name: pubmedbert-keyword-generation
Instance Type: ml.m5.large (2 vCPUs, 8GB RAM)
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
```

#### **Alternative: Lambda + Container Images**
```yaml
Function Name: pubmedbert-inference
Runtime: Container Image (ECR)
Memory: 10GB (maximum)
Timeout: 15 minutes
Architecture: x86_64
Environment Variables:
  - MODEL_CACHE_DIR: /tmp/models
  - TRANSFORMERS_CACHE: /tmp/transformers
Container Image:
  Base: python:3.11-slim
  Size: ~3-4GB (with models)
```

### **2. Background Processing - AWS Lambda**

#### **Analysis Pipeline Functions**
```yaml
Functions:
  clustering-analysis:
    Runtime: python3.11
    Memory: 3008MB
    Timeout: 15 minutes
    Environment:
      - HDBSCAN_MIN_CLUSTER_SIZE: 5
      - UMAP_N_NEIGHBORS: 15
    
  citation-forecasting:
    Runtime: python3.11
    Memory: 1024MB
    Timeout: 10 minutes
    Environment:
      - ARIMA_ORDER: (1,1,1)
      - FORECAST_PERIODS: 12
    
  opportunity-scoring:
    Runtime: python3.11
    Memory: 2048MB
    Timeout: 8 minutes
    Environment:
      - NOVELTY_WEIGHT: 0.4
      - VELOCITY_WEIGHT: 0.4
      - RECENCY_WEIGHT: 0.2
```

#### **Event-Driven Processing**
```yaml
Amazon SQS:
  Queue Name: ml-analysis-queue
  Visibility Timeout: 16 minutes
  Message Retention: 14 days
  Dead Letter Queue: Enabled
  Max Receive Count: 3

Amazon EventBridge:
  Rules:
    - daily-analysis-trigger
    - search-completion-trigger
  Targets:
    - Lambda functions
    - SQS queues
```

---

## 🚀 Supporting Services

### **1. Caching - Amazon ElastiCache**

#### **Redis Configuration**
```yaml
Engine: Redis 7.x
Node Type: cache.t3.micro (1 vCPU, 0.5GB RAM)
Number of Nodes: 1 (development) / 2 (production)
Subnet Group: Private subnets
Security Groups: Cache tier (port 6379)
Backup:
  Snapshot Retention: 5 days
  Snapshot Window: 05:00-06:00 UTC
Use Cases:
  - API response caching
  - Session storage
  - Temporary ML results
  - Rate limiting counters
```

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

#### **Amazon CloudWatch**
```yaml
Log Groups:
  - /aws/apprunner/prime-time-api
  - /aws/lambda/clustering-analysis
  - /aws/lambda/citation-forecasting
  - /aws/lambda/opportunity-scoring
  - /aws/rds/prime-time-db

Metrics & Alarms:
  API Response Time: > 2 seconds
  Database CPU: > 80%
  Database Connections: > 15
  Lambda Errors: > 5%
  SageMaker Endpoint Latency: > 5 seconds

Dashboards:
  - Application Performance
  - Database Health
  - ML Model Performance
  - Cost Optimization
```

#### **AWS X-Ray Tracing**
```yaml
Services to Trace:
  - App Runner (FastAPI)
  - Lambda functions
  - SageMaker endpoints
  - RDS queries
  
Sampling Rules:
  - 10% of all requests
  - 100% of error requests
  - Custom rules for ML endpoints
```

---

## 💰 Cost Analysis

### **Development Environment** (Monthly Estimates)

```yaml
Compute Services:
  App Runner (t3.medium equivalent): $50-80
  Lambda (occasional processing): $10-20
  SageMaker (development endpoint): $30-50

Storage & Database:
  RDS PostgreSQL (t3.micro): $25-35
  S3 Storage (all buckets): $10-20
  ElastiCache (t3.micro): $15-25

Networking & CDN:
  CloudFront: $5-15
  Data Transfer: $5-10
  Load Balancer: $25

Monitoring:
  CloudWatch: $10-20
  X-Ray: $5-10

Total Development: $190-310/month
```

### **Production Environment** (Monthly Estimates)

```yaml
Compute Services:
  App Runner (auto-scaling): $150-250
  Lambda (heavy processing): $20-40
  SageMaker (production endpoint): $100-150

Storage & Database:
  RDS PostgreSQL (t3.medium, Multi-AZ): $120-180
  S3 Storage (all buckets): $30-50
  ElastiCache (cache.t3.small): $30-50

Networking & CDN:
  CloudFront: $20-40
  Data Transfer: $15-30
  Application Load Balancer: $25-35

Monitoring & Security:
  CloudWatch: $25-40
  X-Ray: $10-20
  WAF (optional): $10-20

Total Production: $535-815/month
```

### **Budget Optimization Options**

#### **Lightweight Configuration** (~$100-150/month)
```yaml
Alternative Services:
  AWS Lightsail VPS: $40-80/month
    - Instance: 4GB RAM, 2 vCPUs
    - Includes: Compute, networking, storage
    - Database: Lightsail PostgreSQL $15-30/month
  
  Frontend: S3 + CloudFront: $10-20/month
  Lambda: On-demand ML processing: $10-30/month
  
Trade-offs:
  - Manual scaling
  - Limited ML capabilities
  - Basic monitoring
  - Single availability zone
```

#### **High-Performance Configuration** (~$1000-2000/month)
```yaml
Enhanced Services:
  ECS Fargate Cluster: $200-400/month
  Aurora Serverless v2: $150-300/month
  Multiple SageMaker Endpoints: $300-600/month
  Enhanced Monitoring: $50-100/month
  
Benefits:
  - Container orchestration
  - Auto-scaling database
  - Multiple ML models
  - Advanced monitoring
  - High availability
```

---

## 🛡️ Security Configuration

### **Network Security**

#### **VPC Configuration**
```yaml
VPC CIDR: 10.0.0.0/16

Subnets:
  Public Subnets:
    - 10.0.1.0/24 (AZ-1)
    - 10.0.2.0/24 (AZ-2)
    Purpose: Load balancers, NAT gateways
    
  Private Subnets:
    - 10.0.10.0/24 (AZ-1)
    - 10.0.11.0/24 (AZ-2)
    Purpose: Application servers, Lambda
    
  Database Subnets:
    - 10.0.20.0/24 (AZ-1)
    - 10.0.21.0/24 (AZ-2)
    Purpose: RDS, ElastiCache

NAT Gateways: 2 (one per AZ)
Internet Gateway: 1
Route Tables: Separate for each tier
```

#### **Security Groups**
```yaml
Web Tier (ALB):
  Inbound:
    - HTTP (80) from 0.0.0.0/0
    - HTTPS (443) from 0.0.0.0/0
  Outbound: All traffic

Application Tier:
  Inbound:
    - HTTP (8000) from Web Tier SG
    - HTTPS (443) from Web Tier SG
  Outbound: All traffic

Database Tier:
  Inbound:
    - PostgreSQL (5432) from Application Tier SG
  Outbound: None

Cache Tier:
  Inbound:
    - Redis (6379) from Application Tier SG
  Outbound: None
```

### **Access Control & Encryption**

#### **IAM Roles & Policies**
```yaml
App Runner Execution Role:
  Policies:
    - RDS access (specific database)
    - S3 read/write (specific buckets)
    - SageMaker invoke endpoint
    - CloudWatch logs write
    - Parameter Store read
    - Secrets Manager read

Lambda Execution Roles:
  Policies:
    - VPC access (if needed)
    - RDS access
    - S3 read/write
    - CloudWatch logs
    - SQS send/receive

SageMaker Role:
  Policies:
    - S3 model access
    - CloudWatch logs
    - ECR read (for custom containers)
```

#### **Encryption Configuration**
```yaml
At Rest Encryption:
  RDS: AWS KMS encryption enabled
  S3: SSE-S3 (or SSE-KMS for sensitive data)
  ElastiCache: Encryption at rest enabled
  Lambda: Environment variables encrypted

In Transit Encryption:
  CloudFront: HTTPS only
  ALB: HTTPS redirect
  RDS: SSL/TLS required
  ElastiCache: TLS enabled
  SageMaker: HTTPS endpoints
```

### **Secrets Management**

#### **AWS Secrets Manager**
```yaml
Secrets:
  prime-time/database:
    username: admin
    password: {auto-generated}
    engine: postgres
    host: {rds-endpoint}
    port: 5432
    dbname: prime_time_db
    
  prime-time/api-keys:
    pubmed_api_key: PUBMED_KEY
    crossref_api_key: CROSSREF_KEY
    
Rotation:
  Database Password: 30 days
  API Keys: Manual rotation
```

#### **AWS Systems Manager Parameter Store**
```yaml
Parameters:
  /prime-time/config/max-results: 100
  /prime-time/config/cache-ttl: 3600
  /prime-time/ml/model-version: v1.2.3
  /prime-time/ml/batch-size: 8
  
Secure Parameters (encrypted):
  /prime-time/database/url: CONNECTION_STRING
  /prime-time/jwt/secret: KWT_SECRET
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
      - Email: octavian.andronic@umfcd.ro ; raul.radulescu00@e-uvt.ro
      - SMS: (se introduce dupa)
      - Slack: #alerts-critical
      
  monitoring-alerts:
    Endpoints:
      - Email: octavian.andronic@umfcd.ro ; raul.radulescu00@e-uvt.ro
      - Slack: #alerts-monitoring
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

#### **Disaster Recovery Plan**
```yaml
RTO (Recovery Time Objective): 4 hours
RPO (Recovery Point Objective): 1 hour

DR Procedures:
  1. Activate standby RDS instance
  2. Update DNS to DR region
  3. Deploy application to DR environment
  4. Restore S3 data from replicas
  5. Validate all services operational
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

### **Performance Optimization**

#### **Database Optimization**
```yaml
Connection Pooling:
  Library: psycopg2-pool or SQLAlchemy
  Pool Size: 20 connections
  Overflow: 10 additional connections
  Recycle Time: 3600 seconds

Query Optimization:
  - Add indexes for frequent queries
  - Use EXPLAIN ANALYZE for slow queries
  - Implement read replicas for analytics
  - Cache frequent queries in Redis

Vector Storage:
  - Use pgvector extension for embeddings
  - Create appropriate indexes for similarity search
  - Consider separate table for vectors
```

#### **API Optimization**
```yaml
Caching Strategy:
  Response Caching: 5-60 minutes TTL
  Database Query Caching: 15 minutes TTL
  ML Model Results: 24 hours TTL
  Static Content: 30 days TTL

Rate Limiting:
  General API: 1000 requests/hour
  ML Endpoints: 100 requests/hour
  Search Endpoints: 50 requests/hour
  Export Endpoints: 10 requests/hour
```

### **Cost Optimization**

#### **Reserved Instances & Savings Plans**
```yaml
Recommendations:
  RDS: 1-year Reserved Instance (30-40% savings)
  App Runner: Compute Savings Plan (10-20% savings)
  S3: Intelligent Tiering for automatic optimization
  CloudFront: Consider pricing class based on geography
```

#### **Resource Right-Sizing**
```yaml
Monthly Review:
  - Analyze CloudWatch metrics
  - Identify underutilized resources
  - Adjust instance sizes based on usage
  - Remove unused resources
  - Optimize storage classes
```

### **Security Best Practices**

#### **Ongoing Security Tasks**
```yaml
Regular Activities:
  - Security patch management
  - Access review and cleanup
  - Penetration testing (quarterly)
  - Security configuration assessment
  - Compliance audit preparation

Automation:
  - AWS Config for compliance monitoring
  - AWS Security Hub for centralized findings
  - AWS GuardDuty for threat detection
  - AWS Inspector for vulnerability assessment
```

---

## 🚀 Getting Started

### **Phase 1: Foundation** (Week 1-2)
1. **Set up VPC and networking**
2. **Deploy RDS PostgreSQL database**
3. **Configure basic App Runner service**
4. **Set up S3 and CloudFront for frontend**

### **Phase 2: Core Application** (Week 3-4)
1. **Deploy FastAPI backend to App Runner**
2. **Configure database connections and migrations**
3. **Set up basic monitoring and logging**
4. **Deploy SvelteKit frontend**

### **Phase 3: Machine Learning** (Week 5-6)
1. **Deploy SageMaker endpoint for PubMedBERT**
2. **Configure Lambda functions for analysis**
3. **Set up SQS for background processing**
4. **Implement caching with ElastiCache**

### **Phase 4: Production Readiness** (Week 7-8)
1. **Configure auto-scaling and load balancing**
2. **Set up comprehensive monitoring and alerting**
3. **Implement security best practices**
4. **Performance testing and optimization**
5. **Documentation and runbooks**

---

**This AWS configuration provides a robust, scalable, and secure infrastructure for the Prime Time Medical Research platform, designed to handle the computational demands of AI-powered medical research analysis while maintaining cost efficiency and operational excellence.**

*Configuration Last Updated: June 30, 2025*