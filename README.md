1. Project Title 

Flappy Bird NEAT AI: End-to-End DevOps Integration 

 

2. Problem Statement 

Machine learning applications often suffer from the "it works on my machine" syndrome due to complex dependency trees and environment-specific configurations. The objective of this project is to implement a robust DevOps lifecycle for a NeuroEvolution of Augmenting Topologies (NEAT) model trained to play Flappy Bird. By introducing containerization, automated CI/CD pipelines, and secure secret management, this project ensures that the AI model can be reliably built, tested, and deployed across any environment without manual intervention or exposed credentials. 

 

graph TD
    A[Developer Push/PR] --> B(GitHub Repository)
    B --> C{GitHub Actions CI/CD}
    
    subgraph Pipeline
    C -->|Stage 1| D[Build: Setup Python & Cache Dependencies]
    D -->|Stage 2| E[Test: Run Unit Tests & Linting]
    E -->|Stage 3| F[Deploy: Containerize Application]
    end
    
    F -->|Secure Auth| G[GitHub Secrets]
    F --> H[Local Docker Environment]
    H --> I[Running NEAT Agent Container]

 

 

 

 

 

 

4. CI/CD Pipeline Explanation 

The project utilizes GitHub Actions (.github/workflows/ci.yml) to enforce a multi-stage automated pipeline that triggers on pushes and Pull Requests to the main branch. 

Stage 1: Build & Optimization (Enhancement Feature) 

Checks out the repository code. 

Sets up the Python environment. 

Enhancement: Implements actions/cache for pip dependencies. This significantly reduces workflow execution time by reusing previously downloaded packages instead of fetching them fresh on every run. 

Stage 2: Test 

Installs project dependencies from requirements.txt. 

Runs basic unit tests to verify the integrity of the NEAT configuration and game logic. 

Stage 3: Deploy (Option A - Local Deployment) 

This stage is conditionally restricted to run only when code is merged into the main branch (if: github.ref == 'refs/heads/main'). 

It securely injects configuration values from GitHub Secrets into the environment. 

Validates the Dockerfile by building the container image to ensure the application is ready for local Docker deployment. 

 

5. Git Workflow Used 

This project adheres to a structured, professional Git workflow to maintain code stability: 

Branching Strategy: Direct commits to main are restricted. All new infrastructure and features are developed on isolated feature branches (e.g., feature/devops-enhancement). 

Commit Practices: A minimum of 5 logical, descriptive commits were made to track iterative progress (e.g., git commit -m "chore: add GitHub Actions workflow"). 

Pull Requests (PR): Changes from feature branches are merged into main exclusively via Pull Requests. This ensures the CI/CD pipeline runs and validates the code before integration. 

 

6. Tools Used 

Version Control: Git & GitHub 

CI/CD Automation: GitHub Actions 

Application Stack: Python, Pygame, neat-python 

Containerization & Deployment: Docker, Docker Compose 

Security: GitHub Secrets (for secure environment variable injection) 

 

7. Challenges Faced 

Headless Containerization: Because the application relies on Pygame (which expects a graphical display), containerizing the app for a headless CI/CD runner initially caused the tests to crash. This was resolved by configuring dummy video drivers (SDL_VIDEODRIVER=dummy) within the CI workflow and Dockerfile to allow the NEAT model to train without requiring a physical monitor. 

Secret Management Scope: Ensuring that GitHub Secrets were properly passed from the repository level down into the Docker container required careful mapping of environment variables in the workflow YAML and the docker-compose.yml file to avoid exposing them in the codebase. 

Pipeline Caching Issues: Initially, the pipeline took too long to build. Implementing the dependency caching strategy required correctly targeting the specific pip cache directories for the Ubuntu runner. 
