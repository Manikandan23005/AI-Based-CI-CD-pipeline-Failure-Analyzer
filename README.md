# CI/CD Pipeline Failure Analyzer

## 📄 Abstract

Modern software development relies extensively on Continuous Integration and Continuous Deployment (CI/CD) pipelines to automate build, test, and deployment processes. Tools such as Jenkins generate detailed logs for every pipeline execution; however, analyzing these logs to identify the root cause of failures is largely manual, time-consuming, and error-prone. As the number of pipelines and builds increases, manual log inspection becomes inefficient and inconsistent, leading to increased debugging time and reduced development productivity.

This project implements a CI/CD Pipeline Failure Analyzer, a Python-based system that automatically collects Jenkins pipeline logs, analyzes build outcomes, classifies failure types, and visualizes insights through a centralized dashboard. 

## ⚙️ Features
- **Jenkins API Integration**: Extracts logs and build configurations efficiently.
- **Rules-based Classification**: ML-inspired regex engines parse console logs into distinct categories:
  - Build Failure
  - Test Failure
  - Dependency Error
  - Environment Issue 
  - Unknown Error
- **Predictive Dashboard**: Visualize historical failure trends, pipeline health, and root-cause mapping.
- **Real-Time Assessment Framework**: Responsive Bootstrap 5 interface built on Flask and SQLAlchemy. 

## 🛠️ Technology Stack
- **Backend**: Python 3, Flask, Requests
- **Database**: SQLite & SQLAlchemy ORM
- **DevOps**: Jenkins CI, Jenkins REST API
- **Frontend**: HTML5, CSS3, Bootstrap 5, Chart.js

---

## 🚀 Getting Started

### 1. Requirements

Ensure you have **Docker** and **Docker Compose** installed on your system.
This project uses **Poetry** for dependency management inside the interactive Docker container.

### 2. Running the Application via Docker

To start the CI/CD Pipeline Failure Analyzer with hot-reloading (auto-refresh) enabled:
```bash
docker compose up --build
```

### 3. Populating Mock Data (Optional)

To test the dashboard immediately without configuring Jenkins, you can run the mock generator from a different terminal while the docker container is running:
```bash
docker compose exec web python mock_data_generator.py
```

The server will be available at **`http://localhost:5000`**. Since your project directory is mounted inside the container, saving files locally will automatically restart the Flask server.

---

> _“The proposed system enhances Jenkins by adding automated failure intelligence and cross-pipeline observability rather than replacing existing CI/CD functionality.”_
