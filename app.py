
# print("Starting app.py...")
# import sys
# print("Python version:", sys.version)


# from flask import Flask, render_template, request, jsonify
# from mains import produce
# import tempfile
# import os

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     return render_template("index.html")

# @app.route("/process", methods=["POST"])
# def process():
#     begins = request.form["begins"]
#     ends = request.form["ends"]
#     file = request.files["file"]

#     if not file:
#         return jsonify({"error": "No file uploaded"}), 400

#     temp_dir = tempfile.gettempdir()
#     input_path = os.path.join(temp_dir, file.filename)
#     file.save(input_path)

#     # Output path is temporary — GUI will move it
#     output_path = os.path.join(temp_dir, f"processed_{file.filename}")

#     produce(begins, ends, input_path, output_path)

#     return jsonify({"output_path": output_path})



import sys
import traceback
from tkinter import Tk, filedialog, messagebox, simpledialog
from mains import produce


def main():
    try:
        # ---- Initialize Tk (hidden root window) ----
        root = Tk()
        root.withdraw()
        root.update()

        # ---- Ask user for input Excel file ----
        input_file = filedialog.askopenfilename(
            title="Select raw pathology Excel file",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )

        if not input_file:
            messagebox.showinfo("Cancelled", "No input file selected.")
            root.destroy()
            return

        # ---- Ask user for output Excel file ----
        output_file = filedialog.asksaveasfilename(
            title="Save processed pathology file",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if not output_file:
            messagebox.showinfo("Cancelled", "No output file selected.")
            root.destroy()
            return

        # ---- Ask user for date range ----
        # (simple version for now; UI date picker can be added later)
        begins = simpledialog.askstring(
                "Start date",
                "Enter start date (DD/MM/YYYY):",
                 parent=root
)

        ends = simpledialog.askstring(
            "End date",
             "Enter end date (DD/MM/YYYY):",
              parent=root
)

        if not begins or not ends:
            messagebox.showerror("Error", "Start and end dates are required.")
            root.destroy()
            return

        # ---- Run processing ----
        produce(
            begins=begins,
            ends=ends,
            file_path=input_file,
            file_output=output_file
        )

        messagebox.showinfo(
            "Success",
            "Processing complete!\n\nFile saved successfully."
        )

        root.destroy()

    except Exception as e:
        # ---- Show full error safely ----
        error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(error_msg)  # visible when run from Terminal
        messagebox.showerror("Application Error", str(e))


if __name__ == "__main__":
    main()
