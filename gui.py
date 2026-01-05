import threading
import webview
import shutil
from app import app
from tkinter import Tk, filedialog

def run_flask():
    app.run(port=5050, debug=False)

class API:
    def save_file(self, temp_path):
        root = Tk()
        root.withdraw()

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if save_path:
            shutil.copy(temp_path, save_path)
            return {"status": "saved", "path": save_path}

        return {"status": "cancelled"}

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    webview.create_window(
        "Pathology Processor",
        "http://127.0.0.1:5050",
        js_api=API(),
        width=1000,
        height=700
    )
    webview.start()
