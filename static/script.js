async function submitForm(form) {
    const data = new FormData(form);

    const response = await fetch("/process", {
        method: "POST",
        body: data
    });

    const result = await response.json();

    if (result.output_path) {
        const saveResult = await window.pywebview.api.save_file(result.output_path);
        alert(saveResult.status === "saved"
            ? "File saved successfully"
            : "Save cancelled");
    }
}

document.getElementById("uploadForm").addEventListener("submit", function (e) {
    e.preventDefault();
    submitForm(this);
});
