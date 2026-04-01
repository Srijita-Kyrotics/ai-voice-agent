import sys
import os

# Add the app directory to sys.path
sys.path.append(os.path.abspath("app"))

from app.main import main

if __name__ == "__main__":
    print("--- Production Voice AI Agent ---")
    main()
