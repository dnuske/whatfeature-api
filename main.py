import os, sys
import uvicorn

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", log_level="info")
