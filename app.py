import sys
import traceback
from datetime import datetime
from tkinter import Tk, filedialog, messagebox, simpledialog, Toplevel, Label, Button, Text, END
from tkinter import ttk
import threading
import queue
import time

from mains import produce  # your existing processing function

# --- Global queue for logs ---
log_queue = queue.Queue()
cancel_requested = False

# --- Validate date string ---
def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# --- Logging helper ---
def log(msg: str):
    log_queue.put(msg)

# --- Cancel processing ---
def request_cancel():
    global cancel_requested
    cancel_requested = True

# --- Processing window ---
class ProcessingWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Processing...")
        self.geometry("500x400")
        self.resizable(False, False)

        Label(self, text="Processing file, please wait…", font=("Helvetica", 12)).pack(pady=10)

        # Spinner (indeterminate)
        self.spinner = ttk.Progressbar(self, mode="indeterminate")
        self.spinner.pack(fill="x", padx=20)
        self.spinner.start(10)

        # Determinate progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=20, troughcolor="#2c2c2c", background="#4a90e2")
        self.progress = ttk.Progressbar(self, style="TProgressbar", mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=20, pady=5)

        # Logging window
        self.log_box = Text(self, height=10, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        # Cancel button
        Button(self, text="Cancel", command=self.cancel).pack(pady=5)

        # Poll log queue
        self.after(100, self.poll_log_queue)

    def poll_log_queue(self):
        while not log_queue.empty():
            msg = log_queue.get()
            self.log_box.config(state="normal")
            self.log_box.insert(END, msg + "\n")
            self.log_box.see(END)
            self.log_box.config(state="disabled")
        self.after(100, self.poll_log_queue)

    def cancel(self):
        if messagebox.askyesno("Cancel", "Cancel processing?"):
            request_cancel()

# --- Threaded produce ---
def run_produce_thread(begins, ends, input_file, output_file, progress_bar, on_done):
    global cancel_requested
    cancel_requested = False
    try:
        def progress_callback(percent):
            if cancel_requested:
                raise Exception("Processing cancelled by user")
            progress_bar["value"] = percent

        log("Starting processing…")
        time.sleep(0.1)

        produce(
            begins=begins,
            ends=ends,
            file_path=input_file,
            file_output=output_file,
            progress_callback=progress_callback
        )

        log("Processing completed successfully.")
        on_done(True)

    except Exception as e:
        log(f"Error: {e}")
        on_done(False, str(e))

# --- Main application ---
def main():
    try:
        root = Tk()
        root.title("Pathology Processor")
        root.withdraw()
        root.update()

        # ---- Input / Output files ----
        input_file = filedialog.askopenfilename(
            title="Select raw pathology Excel file",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not input_file:
            messagebox.showinfo("Cancelled", "No input file selected.")
            root.destroy()
            return

        output_file = filedialog.asksaveasfilename(
            title="Save processed pathology file",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not output_file:
            messagebox.showinfo("Cancelled", "No output file selected.")
            root.destroy()
            return

        # ---- Manual date input ----
        def ask_date(prompt):
            while True:
                date_str = simpledialog.askstring(prompt, f"{prompt} (DD/MM/YYYY):", parent=root)
                if date_str is None:
                    return None
                if validate_date(date_str):
                    return date_str
                messagebox.showerror("Invalid Date", "Please enter date in DD/MM/YYYY format.")

        begins = ask_date("Start date")
        if begins is None:
            messagebox.showerror("Error", "Start date required.")
            root.destroy()
            return

        ends = ask_date("End date")
        if ends is None:
            messagebox.showerror("Error", "End date required.")
            root.destroy()
            return

        if datetime.strptime(begins, "%d/%m/%Y") > datetime.strptime(ends, "%d/%m/%Y"):
            messagebox.showerror("Error", "Start date must be before end date.")
            root.destroy()
            return

        # ---- Processing window ----
        processing_window = ProcessingWindow(root)

        def on_done(success, error=None):
            processing_window.spinner.stop()
            processing_window.destroy()
            if success:
                messagebox.showinfo("Success", f"File processed successfully!\nSaved to:\n{output_file}")
            else:
                messagebox.showerror("Error", error or "Processing failed.")
            root.destroy()

        # ---- Start thread ----
        thread = threading.Thread(
            target=run_produce_thread,
            args=(begins, ends, input_file, output_file, processing_window.progress, on_done),
            daemon=True
        )
        thread.start()

        root.mainloop()

    except Exception as e:
        error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(error_msg)
        messagebox.showerror("Application Error", str(e))

if __name__ == "__main__":
    main()