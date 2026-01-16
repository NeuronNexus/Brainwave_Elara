# ProjectIQ

**Automated Project Evaluation for Technical Hiring**

> Objective Scores. Smarter Hiring. Stronger Projects.

AI-powered platform revolutionizing how technical projects are assessed for recruitment and learning.

---

## 🎯 The Problem We're Solving

Manual project reviews are fundamentally broken:

- **Time Consuming**: Recruiters spend under 5 minutes per project—insufficient for thorough evaluation
- **Inconsistent Standards**: No unified framework for assessing technical depth or creative problem-solving
- **Zero Feedback Loop**: Developers receive rejection without guidance on improvement areas

Current tools like SonarQube focus only on code quality, Lighthouse only on frontend UX, and GitHub Copilot assists with code but doesn't evaluate it. **No tool evaluates both code quality and innovation holistically.**

---

## 💡 Our Solution

ProjectIQ creates a universal **"Project Merit Score"** that transforms hiring decisions and accelerates developer learning.

### AI-Powered Objective Scoring

Upload any GitHub repository or project link. Our system automatically evaluates across **11 critical dimensions**, generating a calibrated **100-point score** with actionable improvement recommendations.

- **For Recruiters**: Identify top talent instantly with objective rankings
- **For Developers**: Understand exactly what to improve with evidence-based feedback

---

## 🚀 How It Works

Our end-to-end assessment pipeline combines static analysis, dynamic testing, and machine learning:

```
1. Repository Ingestion
   ↓ Secure sandbox containerization isolates code execution
   
2. Static Analysis
   ↓ Code structure, documentation, and complexity metrics
   
3. Dynamic Testing
   ↓ Functionality, performance, and security vulnerabilities
   
4. UX & Innovation Check
   ↓ Lighthouse audit and originality via embeddings analysis
   
5. ML Scoring
   ↓ Calibrated confidence levels with evidence-based scoring
   
6. Final Report
   → 100-point score + confidence level + actionable recommendations
```

---

## 📊 Scoring Framework

Balanced evaluation across **11 weighted parameters** ensures fair, comprehensive project assessment:

| Dimension              | Weight | Metric                              |
|------------------------|--------|-------------------------------------|
| Technical Correctness  | 20%    | Test pass rate                      |
| Code Quality           | 15%    | Cyclomatic complexity               |
| Security               | 10%    | Vulnerability score                 |
| Innovation             | 10%    | Originality via embeddings          |
| Maintainability        | 10%    | Documentation & coverage            |
| UX & Accessibility     | 8%     | Lighthouse audit                    |
| Deployment             | 7%     | Docker & CI/CD presence             |
| Performance            | 6%     | p95 response time                   |
| Data Ethics            | 6%     | PII handling practices              |
| Community Impact       | 5%     | Stars, forks, adoption              |
| Business Impact        | 3%     | Problem clarity & fit               |

**Output**: Final score, confidence level, and evidence-based recommendations for improvement

---

## 🛠️ Technology Stack

Proven, scalable infrastructure built on industry-standard tools with enterprise-grade security:

### Frontend
- **React/Next.js** with Chart.js for interactive dashboards and real-time visualizations

### Backend
- **Python** with Flask/FastAPI
- **PostgreSQL** database
- Scalable API layer

### ML & AI
- **scikit-learn** for machine learning models
- **OpenAI embeddings** for innovation and originality detection
- **SonarQube metrics** for intelligent code quality scoring

### Infrastructure
- **Docker** for containerization
- **Kubernetes** for orchestration
- **AWS Lambda** for serverless scalability and cost efficiency

### Security First
- Container isolation ensures safe code execution
- API-level access controls protect data privacy
- Sandboxed environment prevents malicious code execution

---

## 🎨 What Makes Us Novel

ProjectIQ is the **only platform** combining holistic multi-dimensional evaluation with machine learning precision:

| Tool           | Focus            | Limitation                    | Our Edge                                    |
|----------------|------------------|-------------------------------|---------------------------------------------|
| SonarQube      | Code Quality     | No UX or innovation metrics   | Multi-dimensional AI scoring                |
| Lighthouse     | Web UX           | Frontend only                 | Full-stack evaluation                       |
| GitHub Copilot | Code Assistance  | No evaluation                 | Objective merit scoring                     |
| **ProjectIQ**  | **Holistic Eval**| **—**                         | **End-to-end + confidence + actionable feedback** |

---

## 🎯 Core Features

### For Recruiters
- **Instant Project Evaluation**: Upload GitHub link, get comprehensive score in minutes
- **Objective Rankings**: Sort candidates by merit score, not resume keywords
- **Recruiter Dashboard**: View top candidates ranked by objective merit
- **Unlimited Evaluations**: Review as many projects as needed

### For Developers
- **Actionable Feedback**: Understand exactly what to improve
- **Evidence-Based Scoring**: See why you got your score with specific examples
- **Learning Pathway**: Get recommendations for skill development
- **Portfolio Enhancement**: Improve projects systematically

### For Educational Institutions
- **Automated Grading**: Reduce manual assessment workload
- **Learning Analytics**: Track student progress across cohorts
- **API Integration**: Embed scoring into existing LMS platforms

---

## 🌟 Market Opportunity

A **$3.5B+ market** exists for code/project evaluation and assessment tools (2025):

- **15M+** student developers submit projects annually seeking feedback
- **10M+** portfolio reviews conducted yearly by recruiters
- **$43B** HR Tech market with AI-based screening tools gaining rapid adoption

---

## 🏗️ Project Architecture

```
projectiq/
│
├── frontend/                → Next.js dashboard
│   ├── components/          → Reusable UI components
│   ├── pages/               → Route handlers
│   └── public/              → Static assets
│
├── backend/                 → FastAPI application
│   ├── app/
│   │   ├── main.py          → API endpoints
│   │   ├── worker.py        → Background job runner
│   │   ├── analyzer.py      → Core analysis logic
│   │   ├── scoring.py       → ML scoring engine
│   │   └── utils.py         → Helper functions
│   │
│   ├── models/              → ML models and weights
│   ├── jobs/                → Uploaded project storage
│   └── requirements.txt
│
├── ml/                      → Machine learning pipeline
│   ├── training/            → Model training scripts
│   ├── embeddings/          → Innovation detection
│   └── evaluation/          → Scoring calibration
│
├── docker/                  → Containerization configs
└── infrastructure/          → Kubernetes & AWS configs
```

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/projectiq.git
cd projectiq

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Access the application:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Or use individual containers
docker build -t projectiq-backend ./backend
docker build -t projectiq-frontend ./frontend
```

---

## 📖 API Documentation

### Submit Project for Evaluation

```http
POST /api/evaluate
Content-Type: multipart/form-data

{
  "project_type": "fullstack|frontend|backend|python",
  "description": "Project description",
  "github_url": "https://github.com/user/repo",
  "zip_file": <file>  // Optional: direct ZIP upload
}
```

**Response:**
```json
{
  "job_id": "uuid-123-456",
  "status": "queued",
  "estimated_time": "5-10 minutes"
}
```

### Get Evaluation Results

```http
GET /api/result/{job_id}
```

**Response:**
```json
{
  "status": "completed",
  "score": 87,
  "confidence": 0.92,
  "breakdown": {
    "technical_correctness": 18,
    "code_quality": 13,
    "security": 9,
    "innovation": 8,
    "maintainability": 9,
    "ux_accessibility": 7,
    "deployment": 6,
    "performance": 5,
    "data_ethics": 5,
    "community_impact": 4,
    "business_impact": 3
  },
  "recommendations": [
    "Add comprehensive test coverage (currently 45%)",
    "Implement CI/CD pipeline with GitHub Actions",
    "Address 3 high-severity security vulnerabilities"
  ]
}
```

---

## 🔬 Innovation & Novelty

### What Makes ProjectIQ Unique

1. **Holistic Multi-Dimensional Analysis**
   - First platform to combine code quality, UX, security, and innovation in one score
   - 11 weighted parameters capture complete project merit

2. **ML-Powered Originality Detection**
   - OpenAI embeddings detect project uniqueness
   - Distinguish between template projects and original work

3. **Dynamic Testing in Sandbox**
   - Actually runs code to verify functionality
   - Performance benchmarking with real metrics

4. **Confidence Calibration**
   - Every score comes with confidence level
   - Transparent about evaluation certainty

5. **Actionable Feedback Loop**
   - Not just a score—specific, evidence-based improvement recommendations
   - Developers learn what to fix, not just that something is wrong

---

## 🔒 Security & Safety

- **Container Isolation**: Every project runs in isolated Docker container
- **Resource Limits**: CPU, memory, and time constraints prevent abuse
- **Network Isolation**: No outbound connections during evaluation
- **Code Sandboxing**: Restricted filesystem access and execution permissions
- **Automated Cleanup**: Containers destroyed after evaluation

---

## 🎓 Use Cases

1. **Technical Recruitment**
   - Screen candidates objectively before interviews
   - Reduce bias in initial evaluation
   - Focus interviews on high-potential candidates

2. **Coding Bootcamps**
   - Automated project grading
   - Student progress tracking
   - Curriculum effectiveness measurement

3. **Hackathons**
   - Fair, objective judging criteria
   - Quick evaluation of hundreds of submissions
   - Transparent scoring for participants

4. **Open Source Contribution**
   - Assess PR quality before review
   - Project health scoring
   - Contributor ranking systems

5. **Portfolio Enhancement**
   - Developers improve projects systematically
   - Clear learning pathway
   - Competitive advantage in job market

---

## 🛣️ Roadmap

### Phase 1: Foundation (Current)
- ✅ Rule-based evaluation engine
- ✅ Real code execution pipeline
- ✅ Basic scoring framework

### Phase 2: Intelligence
- 🔄 AI-powered project type detection
- 🔄 ML-based scoring calibration
- 🔄 Natural language recommendation generation

### Phase 3: Scale
- 📋 Advanced ML models trained on recruiter feedback
- 📋 Hiring outcome correlation analysis
- 📋 Continuous learning from human reviews

### Phase 4: Enterprise
- 📋 Recruiter dashboard with analytics
- 📋 Candidate ranking systems
- 📋 ATS integration APIs
- 📋 White-label solutions

### Phase 5: Ecosystem
- 📋 Public API for EdTech platforms
- 📋 Plugin marketplace
- 📋 Community-driven scoring models

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact & Support

- **Website**: [projectiq.dev](https://projectiq.dev)
- **Email**: support@projectiq.dev
- **Documentation**: [docs.projectiq.dev](https://docs.projectiq.dev)
- **Discord**: [Join our community](https://discord.gg/projectiq)

---

## 🙏 Acknowledgments

Built with ❤️ to make technical hiring fairer and developer learning faster.

**ProjectIQ** - Because every project deserves an objective evaluation.