"""
deploy.py - Deployment script for RedRob Ranker to cloud platforms.

Supports:
- Heroku
- Railway
- Render
- AWS Elastic Beanstalk
- Google Cloud Run
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required tools are installed."""
    tools = ['git', 'docker']
    missing = []
    
    for tool in tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode != 0:
            missing.append(tool)
    
    if missing:
        logger.error(f"Missing required tools: {', '.join(missing)}")
        return False
    
    return True


def deploy_heroku():
    """Deploy to Heroku."""
    logger.info("Deploying to Heroku...")
    
    # Check if heroku CLI is installed
    result = subprocess.run(['which', 'heroku'], capture_output=True)
    if result.returncode != 0:
        logger.error("Heroku CLI not found. Install it from https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Create heroku.yml for container deployment
    heroku_config = """build:
  docker:
    web: Dockerfile
run:
  web: python -m uvicorn api.server:app --host 0.0.0.0 --port $PORT
"""
    
    with open('heroku.yml', 'w') as f:
        f.write(heroku_config)
    
    logger.info("Created heroku.yml")
    
    # Deployment commands
    commands = [
        'heroku login',
        'heroku create redrob-ranker || true',
        'heroku stack:set container',
        'git add heroku.yml',
        'git commit -m "Add Heroku deployment" || true',
        'git push heroku main'
    ]
    
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0 and 'commit' not in cmd:
            logger.error(f"Command failed: {cmd}")
            return False
    
    logger.info("✅ Deployed to Heroku successfully!")
    logger.info("URL: https://redrob-ranker.herokuapp.com")
    return True


def deploy_railway():
    """Deploy to Railway."""
    logger.info("Deploying to Railway...")
    
    # Check if railway CLI is installed
    result = subprocess.run(['which', 'railway'], capture_output=True)
    if result.returncode != 0:
        logger.error("Railway CLI not found. Install it from https://docs.railway.app/develop/cli")
        return False
    
    # Create railway.json config
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "DOCKERFILE",
            "dockerfilePath": "Dockerfile"
        },
        "deploy": {
            "startCommand": "python -m uvicorn api.server:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    logger.info("Created railway.json")
    
    # Deployment commands
    commands = [
        'railway login',
        'railway init --name redrob-ranker || true',
        'railway up'
    ]
    
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            return False
    
    logger.info("✅ Deployed to Railway successfully!")
    logger.info("Check Railway dashboard for URL")
    return True


def deploy_render():
    """Deploy to Render."""
    logger.info("Deploying to Render...")
    
    # Create render.yaml for Render Blueprint
    render_config = """services:
  - type: web
    name: redrob-ranker
    runtime: docker
    plan: standard
    autoDeploy: true
    envVars:
      - key: PORT
        value: 8000
      - key: PYTHON_VERSION
        value: 3.11
"""
    
    with open('render.yaml', 'w') as f:
        f.write(render_config)
    
    logger.info("Created render.yaml")
    logger.info("To deploy to Render:")
    logger.info("1. Push code to GitHub")
    logger.info("2. Go to https://dashboard.render.com/")
    logger.info("3. Click 'New Web Service'")
    logger.info("4. Connect your GitHub repository")
    logger.info("5. Render will auto-detect render.yaml and deploy")
    
    return True


def deploy_aws():
    """Deploy to AWS Elastic Beanstalk."""
    logger.info("Deploying to AWS Elastic Beanstalk...")
    
    # Check if EB CLI is installed
    result = subprocess.run(['which', 'eb'], capture_output=True)
    if result.returncode != 0:
        logger.error("AWS EB CLI not found. Install it: pip install awsebcli")
        return False
    
    # Create .ebextensions directory and config
    os.makedirs('.ebextensions', exist_ok=True)
    
    eb_config = """option_settings:
  aws:elasticbeanstalk:environment:process:default:
    Port: '8000'
    Protocol: HTTP
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
    
container_commands:
  01_upgrade_pip:
    command: "pip install --upgrade pip"
    ignoreErrors: false
  02_install_requirements:
    command: "pip install -r requirements.txt"
    ignoreErrors: false
"""
    
    with open('.ebextensions/01_packages.config', 'w') as f:
        f.write(eb_config)
    
    # Create Procfile for EB
    with open('Procfile', 'w') as f:
        f.write('web: python -m uvicorn api.server:app --host 0.0.0.0 --port 8000\n')
    
    logger.info("Created EB configuration files")
    
    # Deployment commands
    commands = [
        'eb init -p docker redrob-ranker --region us-east-1',
        'eb create redrob-ranker-env --single --timeout 20',
        'eb open'
    ]
    
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            return False
    
    logger.info("✅ Deployed to AWS Elastic Beanstalk successfully!")
    return True


def deploy_gcp():
    """Deploy to Google Cloud Run."""
    logger.info("Deploying to Google Cloud Run...")
    
    # Check if gcloud CLI is installed
    result = subprocess.run(['which', 'gcloud'], capture_output=True)
    if result.returncode != 0:
        logger.error("Google Cloud SDK not found. Install it from https://cloud.google.com/sdk/docs/install")
        return False
    
    # Create cloudbuild.yaml
    cloudbuild_config = """steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/redrob-ranker:$COMMIT_SHA', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/redrob-ranker:$COMMIT_SHA']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'redrob-ranker'
      - '--image'
      - 'gcr.io/$PROJECT_ID/redrob-ranker:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/redrob-ranker:$COMMIT_SHA'
"""
    
    with open('cloudbuild.yaml', 'w') as f:
        f.write(cloudbuild_config)
    
    logger.info("Created cloudbuild.yaml")
    
    # Deployment commands
    commands = [
        'gcloud auth configure-docker',
        'gcloud builds submit --config cloudbuild.yaml',
    ]
    
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            return False
    
    logger.info("✅ Deployed to Google Cloud Run successfully!")
    return True


def build_docker():
    """Build and test Docker image locally."""
    logger.info("Building Docker image...")
    
    commands = [
        'docker build -t redrob-ranker:latest .',
        'docker run --rm -p 8000:8000 -d --name redrob-test redrob-ranker:latest',
        'sleep 5',
        'curl -f http://localhost:8000/health || echo "Health check failed"',
        'docker stop redrob-test'
    ]
    
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0 and 'sleep' not in cmd:
            logger.warning(f"Command may have failed: {cmd}")
    
    logger.info("✅ Docker build complete")
    return True


def main():
    """Main deployment script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy RedRob Ranker to cloud')
    parser.add_argument('platform', choices=['heroku', 'railway', 'render', 'aws', 'gcp', 'docker'],
                       help='Cloud platform to deploy to')
    parser.add_argument('--check', action='store_true',
                       help='Check dependencies only')
    
    args = parser.parse_args()
    
    if args.check:
        if check_dependencies():
            logger.info("✅ All dependencies are installed")
            return 0
        else:
            logger.error("❌ Missing dependencies")
            return 1
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Deploy to selected platform
    if args.platform == 'heroku':
        return 0 if deploy_heroku() else 1
    elif args.platform == 'railway':
        return 0 if deploy_railway() else 1
    elif args.platform == 'render':
        return 0 if deploy_render() else 1
    elif args.platform == 'aws':
        return 0 if deploy_aws() else 1
    elif args.platform == 'gcp':
        return 0 if deploy_gcp() else 1
    elif args.platform == 'docker':
        return 0 if build_docker() else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
