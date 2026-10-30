
const API_BASE_URL = "http://127.0.0.1:8000";

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileMeta = document.getElementById("fileMeta");
const fileStatus = document.getElementById("fileStatus");

let currentDatasetId = null;

// Show selected file
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
        uploadStatus.textContent = "Please select a CSV file.";
        fileInput.value = "";
        return;
    }

    currentDatasetId = null;
    fileInfo.hidden = false;

    fileName.textContent = file.name;
    fileMeta.textContent = "Ready to upload";
    fileStatus.textContent = "Selected";

    uploadStatus.textContent = "";
});

// Upload dataset
uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Please select a CSV file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        uploadBtn.disabled = true;
        uploadBtn.textContent = "Uploading...";

        fileStatus.textContent = "Uploading";
        fileMeta.textContent = "Processing dataset...";

        const response = await fetch(
            `${API_BASE_URL}/datasets/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed.");
        }

        currentDatasetId = data.dataset_id;

        fileName.textContent = file.name;
        fileMeta.textContent = `${data.rows_loaded} rows loaded`;
        fileStatus.textContent = "Uploaded";

        uploadStatus.textContent = "Dataset ready for analysis.";

    } catch (error) {
        fileStatus.textContent = "Failed";
        fileMeta.textContent = "Upload unsuccessful";
        uploadStatus.textContent = error.message;

        console.error(error);

    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload dataset";
    }
});
