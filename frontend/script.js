
// ============================================
// QueryPilot - Frontend JavaScript
// ============================================

console.log("QueryPilot page loaded:", new Date().toISOString());


// TEMPORARY: Detect and prevent unexpected form submissions.
document.addEventListener("submit", (event) => {
    console.error("Unexpected form submission detected:", event.target);
    event.preventDefault();
    event.stopPropagation();
}, true);

// TEMPORARY: Detect page navigation/reload.
window.addEventListener("beforeunload", () => {
    console.warn("QueryPilot is about to reload or navigate.");
});

const API_BASE_URL = "http://127.0.0.1:8000";

// ============================================
// 1. DOM ELEMENTS
// ============================================

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileMeta = document.getElementById("fileMeta");
const fileStatus = document.getElementById("fileStatus");

const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const queryBtn = document.getElementById("queryBtn");

const sqlOutput = document.getElementById("sqlOutput");
const resultsOutput = document.getElementById("resultsOutput");


// ============================================
// 2. APPLICATION STATE
// ============================================

let selectedFile = null;
let currentDatasetId = sessionStorage.getItem("querypilot_dataset_id");


// ============================================
// 3. API RESPONSE HANDLER
// ============================================

async function readApiResponse(response) {
    const responseText = await response.text();

    let data;

    try {
        data = responseText ? JSON.parse(responseText) : {};
    } catch {
        throw new Error("The server returned an invalid response.");
    }

    if (!response.ok) {
        const message =
            data.detail ||
            data.message ||
            `Request failed with status ${response.status}.`;

        throw new Error(message);
    }

    if (data === null || typeof data !== "object") {
        throw new Error("The server returned an empty response.");
    }

    return data;
}


// ============================================
// 4. RESTORE PREVIOUS DATASET
// ============================================

function restoreDataset() {
    const savedDatasetId = sessionStorage.getItem("querypilot_dataset_id");
    const savedFileName = sessionStorage.getItem("querypilot_file_name");
    const savedRows = sessionStorage.getItem("querypilot_rows");

    if (!savedDatasetId) {
        currentDatasetId = null;
        fileInfo.hidden = true;
        return;
    }

    currentDatasetId = savedDatasetId;

    fileInfo.hidden = false;

    fileName.textContent = savedFileName || "Uploaded dataset";
    fileMeta.textContent = savedRows
        ? `${savedRows} rows uploaded`
        : "Dataset uploaded successfully";

    fileStatus.textContent = "Uploaded";

    uploadStatus.textContent = "Your previous dataset is ready.";
    resultsOutput.textContent = "Ask a question to explore your data.";
}


// ============================================
// 5. FILE SELECTION
// ============================================

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (!file) {
        return;
    }

    selectedFile = file;

    // Clear the previous dataset selection.
    currentDatasetId = null;

    sessionStorage.removeItem("querypilot_dataset_id");
    sessionStorage.removeItem("querypilot_file_name");
    sessionStorage.removeItem("querypilot_rows");

    // Reset previous results.
    sqlOutput.textContent = "Your SQL query will appear here.";
    resultsOutput.textContent = "Upload your dataset to get started.";

    uploadStatus.textContent = "";

    fileInfo.hidden = false;

    fileName.textContent = file.name;
    fileMeta.textContent =
        `${(file.size / (1024 * 1024)).toFixed(2)} MB · Ready to upload`;

    fileStatus.textContent = "Selected";

    // Basic file validation.
    const isCSV = file.name.toLowerCase().endsWith(".csv");
    const maxSize = 5 * 1024 * 1024;

    if (!isCSV) {
        uploadStatus.textContent = "Please select a CSV file.";
        selectedFile = null;
        return;
    }

    if (file.size > maxSize) {
        uploadStatus.textContent = "File size must not exceed 5 MB.";
        selectedFile = null;
        return;
    }

    uploadStatus.textContent = "File selected successfully.";
});


// ============================================
// 6. UPLOAD DATASET
// ============================================

uploadBtn.addEventListener("click", async () => {
    event.preventDefault();
    if (!selectedFile) {
        uploadStatus.textContent = "Please select a CSV file first.";
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading...";

    uploadStatus.textContent = "Uploading your dataset...";

    try {
        const response = await fetch(
            `${API_BASE_URL}/datasets/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await readApiResponse(response);

        if (!data.dataset_id) {
            throw new Error("Upload response did not contain a dataset ID.");
        }

        // Save dataset information.
        currentDatasetId = data.dataset_id;

        sessionStorage.setItem(
            "querypilot_dataset_id",
            data.dataset_id
        );

        sessionStorage.setItem(
            "querypilot_file_name",
            selectedFile.name
        );

        sessionStorage.setItem(
            "querypilot_rows",
            data.rows_loaded ?? ""
        );

        // Update dataset information.
        fileInfo.hidden = false;

        fileName.textContent = selectedFile.name;

        fileMeta.textContent =
            `${data.rows_loaded ?? "?"} rows · ${data.columns?.length ?? "?"} columns`;

        fileStatus.textContent = "Uploaded";

        uploadStatus.textContent =
            data.message || "Dataset uploaded successfully.";

        resultsOutput.textContent =
            "Dataset ready! Ask a question to explore your data.";

        sqlOutput.textContent =
            "Your SQL query will appear here.";

    } catch (error) {
        console.error("Dataset upload error:", error);

        uploadStatus.textContent = error.message;

    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload dataset";
    }
});


// ============================================
// 7. DISPLAY QUERY RESULTS
// ============================================

function displayResults(rows) {
    resultsOutput.innerHTML = "";

    if (!Array.isArray(rows)) {
        resultsOutput.textContent =
            "The server did not return results in the expected format.";
        return;
    }

    if (rows.length === 0) {
        resultsOutput.textContent = "No results found.";
        return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "results-wrapper";

    const table = document.createElement("table");
    table.className = "results-table";

    const headers = Object.keys(rows[0]);

    // Table header.
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    headers.forEach((header) => {
        const th = document.createElement("th");
        th.textContent = header;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Table body.
    const tbody = document.createElement("tbody");

    rows.forEach((row) => {
        const tr = document.createElement("tr");

        headers.forEach((header) => {
            const td = document.createElement("td");

            const value = row[header];

            td.textContent =
                value === null || value === undefined
                    ? "NULL"
                    : String(value);

            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);

    resultsOutput.appendChild(wrapper);

    const count = document.createElement("p");
    count.textContent = `${rows.length} row(s) returned.`;
    count.style.marginTop = "12px";

    resultsOutput.appendChild(count);
}


// ============================================
// 8. GENERATE SQL AND QUERY RESULTS
// ============================================

queryBtn.addEventListener("click", async () => {
    const question = questionInput.value.trim();

    if (!currentDatasetId) {
        resultsOutput.textContent =
            "Please upload a dataset first.";
        return;
    }

    if (!question) {
        resultsOutput.textContent =
            "Please enter a question about your data.";
        return;
    }

    queryBtn.disabled = true;
    queryBtn.textContent = "Generating insights...";

    sqlOutput.textContent = "Generating SQL...";
    resultsOutput.textContent = "Analyzing your data...";

    try {
        const response = await fetch(
            `${API_BASE_URL}/query`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question,
                    dataset_id: currentDatasetId
                })
            }
        );

        const data = await readApiResponse(response);

        // Display generated SQL.
        sqlOutput.textContent =
            data.sql || "No SQL query was returned.";

        // Display query results.
        displayResults(data.rows);

    } catch (error) {
        console.error("Query error:", error);

        sqlOutput.textContent = "Query generation failed.";

        resultsOutput.textContent = error.message;

    } finally {
        queryBtn.disabled = false;
        queryBtn.textContent = "Generate insights →";
    }
});


// ============================================
// 9. INITIALIZE APPLICATION
// ============================================

restoreDataset();

console.log("QueryPilot frontend initialized successfully.");
