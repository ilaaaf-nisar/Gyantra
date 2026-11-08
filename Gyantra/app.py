import sys
import threading
import tkinter as tk
import os
from pathlib import Path
from tkinter import messagebox


ROOT = Path(__file__).resolve().parent
INTERFACE_PATH = ROOT / "ignou_llm_web_interface.html"


def show_error(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("GYANTRA could not start", message)
    root.destroy()


def main():
    if not INTERFACE_PATH.is_file():
        show_error(
            "The chat interface file is missing.\n\n"
            f"Expected to find:\n{INTERFACE_PATH}\n\n"
            "Restore ignou_llm_web_interface.html to the project folder, "
            "or update INTERFACE_PATH in app.py to match its new name."
        )
        return 1

    try:
        import webview
    except ImportError:
        show_error(
            "The desktop window dependency is missing.\n\n"
            "Install it by running:\n"
            ".\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt"
        )
        return 1

    try:
        os.chdir(ROOT)
        import chat_server
        from http.server import ThreadingHTTPServer

        server = ThreadingHTTPServer(
            (chat_server.HOST, chat_server.PORT),
            chat_server.ChatHandler,
        )
    except OSError as error:
        show_error(
            f"Could not start GYANTRA's local model server at "
            f"http://127.0.0.1:8000.\n\n{error}\n\n"
            "Close any other app using port 8000 and try again."
        )
        return 1
    except Exception as error:
        show_error(f"The local model could not be loaded.\n\n{error}")
        return 1

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        webview.create_window(
            "GYANTRA – Your Private AI Learning Companion",
            INTERFACE_PATH.as_uri(),
            width=1200,
            height=850,
            min_size=(720, 560),
        )
        webview.start()
    except Exception as error:
        show_error(
            "GYANTRA's desktop window could not open.\n\n"
            f"{error}\n\n"
            "On Windows, install or repair the Microsoft Edge WebView2 Runtime."
        )
        return 1
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    return 0


if __name__ == "__main__":
    sys.exit(main())
