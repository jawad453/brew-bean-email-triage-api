# Brew & Bean Email Triage API

A FastAPI service for classifying Brew & Bean Cafe customer emails.

## Features

- POST `/triage` endpoint
- Authentication using an environment token
- Email classification
- Confidence threshold
- Rate limiting
- Structured JSON logging
- Docker support
- Automated Black, Flake8 and pytest checks
- Automatic Render deployment through GitHub Actions

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt