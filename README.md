# CyberShield Agent

AI-powered repository analysis platform that combines rule-based security scanning with Gemini-assisted code review to help developers identify potential security risks in GitHub repositories.

## Demo

<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/be0977a1-0c45-415f-9741-01d6dfc23bb1" />
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/4b047c9a-195b-46cf-b825-e99e12627141" />


## Features

- Analyze public GitHub repositories
- Rule-based security checks
- AI-assisted repository review using Gemini
- GitHub Actions workflow inspection
- Severity-based findings (High, Medium, Low, Info)
- MongoDB-powered scan history
- Interactive React dashboard

## Architecture

Frontend (React)
        ↓
Backend (FastAPI)
        ↓
GitHub API + Gemini API
        ↓
MongoDB

## Tech Stack

### Frontend
- React
- Axios

### Backend
- FastAPI
- Python

### Database
- MongoDB

### AI
- Gemini API

## Example Findings

- Missing `.gitignore`
- Hardcoded secret patterns
- Overly permissive GitHub Actions workflows
- Missing explicit workflow permissions
- Missing dependency manifests

## API Endpoints

| Method | Endpoint        | Description         |
|--------|-----------------|---------------------|
| GET    | /health         | Service health      |
| POST   | /api/scans/scan | Run repository scan |
| GET    | /api/scans/{id} | Retrieve saved scan |
| GET    | /api/scans      | List scan history   |

## Team Contributions
- Backend: repository scanning flow, API design, analysis logic, AI integration, and persistence.
- Frontend: input flow, scan UX, and result presentation.
- Built collaboratively as a full-stack security project.



## Future Improvements
- Export reports (PDF/CSV)
- GitHub Issue creation
- Scheduled scans
- Additional security rules
- Multi-repository dashboards


## Setup
- Clone the repository.
- Create and activate a Python virtual environment.
- Install project dependencies such as FastAPI, Uvicorn, MongoDB client libraries, and Google GenAI SDK support.
- Add environment variables for the application, GitHub token, MongoDB connection, and Gemini API key.
- Run the FastAPI application and verify /health and /api/db-test.
- Start the frontend and connect it to the backend scan endpoint.



# Run
uvicorn cybershield_backend.app.main:app --reload
