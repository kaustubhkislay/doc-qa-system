# Document Q&A System

A RAG-based application for querying PDF documents using AI. Upload PDFs and ask questions about their content.

## Tech Stack

- **Backend**: Python, FastAPI, LangChain
- **Frontend**: React, TypeScript, Tailwind CSS
- **AI**: Google Vertex AI (Gemini 2.5 Flash + text-embedding-004)
- **Vector Store**: ChromaDB
- **Infrastructure**: Google Cloud Run, Cloud Storage, Firestore

## Prerequisites

- Python 3.12+
- Node.js 18+
- Google Cloud account with billing enabled
- `gcloud` CLI installed

## GCP Setup

### 1. Create a GCP Project

```bash
gcloud projects create YOUR_PROJECT_ID
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com
```

### 3. Create Cloud Storage Bucket

```bash
gcloud storage buckets create gs://YOUR_PROJECT_ID-pdfs --location=us-central1
```

### 4. Create Firestore Database

```bash
gcloud firestore databases create --location=us-central1
```

### 5. Authenticate

```bash
gcloud auth application-default login
```

## Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
PROJECT_ID=YOUR_PROJECT_ID
BUCKET_NAME=YOUR_PROJECT_ID-pdfs
REGION=us-central1
EOF

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run the dev server
npm run dev
```

Frontend will be available at http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/documents/upload` | Upload a PDF |
| GET | `/documents/` | List all documents |
| GET | `/documents/{id}` | Get document details |
| DELETE | `/documents/{id}` | Delete a document |
| POST | `/query/` | Ask a question |

### Example: Upload a Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@document.pdf" \
  -F "title=My Document"
```

### Example: Ask a Question

```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

## Deployment (Google Cloud Run)

### 1. Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Service Account"

# Grant required roles
PROJECT_ID=$(gcloud config get-value project)

for role in \
  roles/run.admin \
  roles/storage.admin \
  roles/artifactregistry.repoAdmin \
  roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="$role"
done
```

### 2. Setup Workload Identity Federation

```bash
# Create workload identity pool
gcloud iam workload-identity-pools create "github" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow GitHub repo to impersonate service account
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
```

### 3. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create doc-qa \
  --repository-format=docker \
  --location=us-central1
```

### 4. Add GitHub Secrets

In your GitHub repo, go to Settings → Secrets → Actions and add:

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_REGION` | `us-central1` |
| `GCP_BUCKET_NAME` | `YOUR_PROJECT_ID-pdfs` |
| `WIF_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/github-provider` |
| `WIF_SERVICE_ACCOUNT` | `github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com` |

### 5. Push to Deploy

Pushing to `main` branch will trigger the deployment workflow.

## Project Structure

```
doc-qa-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── routes/
│   │   │   ├── documents.py     # Document endpoints
│   │   │   └── query.py         # Query endpoint
│   │   └── services/
│   │       ├── pdf_processor.py # PDF extraction
│   │       ├── vectorstore.py   # ChromaDB
│   │       ├── llm.py           # Vertex AI
│   │       └── storage.py       # GCS + Firestore
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api/client.ts        # API client
│   │   └── components/
│   │       ├── DocumentUpload.tsx
│   │       ├── DocumentList.tsx
│   │       └── ChatInterface.tsx
│   ├── Dockerfile
│   └── package.json
└── .github/workflows/deploy.yml
```

## License

MIT
