import uvicorn
import argparse
import sys
import os

if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    base_path = sys._MEIPASS  # Temp folder where bundled files are unpacked
    sys.path.insert(0, os.path.join(base_path, "app"))  # Add app folder to sys.path
else:
    base_path = os.path.abspath(os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser(description="Start Tagging Dashboard server.")
    parser.add_argument("--port", type=int, default=8888, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    uvicorn.run("app.main:app", host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
