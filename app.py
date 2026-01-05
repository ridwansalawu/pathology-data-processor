import sys
import traceback
from datetime import datetime
from tkinter import Tk, filedialog, messagebox, simpledialog, Toplevel, Label, Button, Text, END
from tkinter import ttk
import threading
import queue
import time

from mains import produce  # Your existing processing function

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
        self.geometry("500x350")
        self.resizable(False, False)

        Label(self, text="Processing file, please wait…", font=("Helvetica", 12)).pack(pady=10)

        # Spinner
        self.spinner = ttk.Progressbar(self, mode="indeterminate")
        self.spinner.pack(fill="x", padx=20)
        self.spinner.start(10)

        # Progress bar (optional)
        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=20, pady=5)

        # Log window
        self.log_box = Text(self, height=10, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        Button(self, text="Cancel", command=self.cancel).pack(pady=5)

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
def run_produce_thread(begins, ends, input_file, output_file, on_done):
    global cancel_requested
    cancel_requested = False
    try:
        log("Starting processing…")
        time.sleep(0.2)

        if cancel_requested:
            log("Processing cancelled by user.")
            on_done(False, "Processing cancelled.")
            return

        produce(
            begins=begins,
            ends=ends,
            file_path=input_file,
            file_output=output_file
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
            args=(begins, ends, input_file, output_file, on_done),
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



# import sys
# import traceback
# from tkinter import Tk, filedialog, messagebox, simpledialog
# from mains import produce

# from datetime import datetime

# import threading
# import queue
# import time
# from tkinter import *
# from tkinter import ttk, messagebox


# def validate_date(date_str: str) -> bool:
#     try:
#         datetime.strptime(date_str, "%d/%m/%Y")
#         return True
#     except ValueError:
#         return False


# from tkcalendar import Calendar

# def pick_date(title: str, parent) -> str:
#     top = Tk()
#     top.title(title)

#     cal = Calendar(
#         top,
#         selectmode="day",
#         date_pattern="dd/mm/yyyy"
#     )
#     cal.pack(padx=10, pady=10)

#     selected_date = {"value": None}

#     def confirm():
#         selected_date["value"] = cal.get_date()
#         top.destroy()

#     from tkinter import Button
#     Button(top, text="OK", command=confirm).pack(pady=10)

#     top.mainloop()
#     return selected_date["value"]



# def main():
#     try:
#         # ---- Initialize Tk (hidden root window) ----
#         root = Tk()
#         root.title("Pathology Processor")
#         root.withdraw()
#         root.update()

#         # ---- Ask user for input Excel file ----
#         input_file = filedialog.askopenfilename(
#             title="Select raw pathology Excel file",
#             filetypes=[("Excel files", "*.xlsx *.xls")]
#         )

#         if not input_file:
#             messagebox.showinfo("Cancelled", "No input file selected.")
#             root.destroy()
#             return

#         # ---- Ask user for output Excel file ----
#         output_file = filedialog.asksaveasfilename(
#             title="Save processed pathology file",
#             defaultextension=".xlsx",
#             filetypes=[("Excel files", "*.xlsx")]
#         )

#         if not output_file:
#             messagebox.showinfo("Cancelled", "No output file selected.")
#             root.destroy()
#             return
        










#         # ---- Ask user for date range ----
#         # (simple version for now; UI date picker can be added later)
#         begins = simpledialog.askstring(
#                 "Start date",
#                 "Enter start date (DD/MM/YYYY):",
#                  parent=root
# )

#         ends = simpledialog.askstring(
#             "End date",
#              "Enter end date (DD/MM/YYYY):",
#               parent=root
# )

#         if not begins or not ends:
#             messagebox.showerror("Error", "Start and end dates are required.")
#             root.destroy()
#             return
        
#         if not validate_date(begins) or not validate_date(ends):
#             messagebox.showerror(
#              "Invalid date",
#              "Dates must be in DD/MM/YYYY format."
#     )
#             root.destroy()
#             return
#         #



#         messagebox.showinfo("Processing", "Processing file, please wait…")

#         produce(
#             begins=begins,
#             ends=ends,
#             file_path=input_file,
#             file_output=output_file
#         )

#         messagebox.showinfo(
#             "Success",
#             "Processing complete!\n\nFile saved successfully."
#         )

#         root.destroy()

#     except Exception as e:
#         # ---- Show full error safely ----
#         error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
#         print(error_msg)  # visible when run from Terminal
#         messagebox.showerror("Application Error", str(e))


# if __name__ == "__main__":
#     main()
