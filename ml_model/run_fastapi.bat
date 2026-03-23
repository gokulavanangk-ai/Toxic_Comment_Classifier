@echo off
echo Starting FastAPI Server...
uvicorn src.api:app --reload
pause
