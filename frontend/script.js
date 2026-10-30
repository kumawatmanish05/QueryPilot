

// ============================================
// QueryPilot - Frontend JavaScript
// ============================================

const API_BASE_URL = "http://127.0.0.1:8000";

console.log("QueryPilot script loaded successfully.");


// ============================================
// DOM Elements
// ============================================

const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileMeta = document.getElementById("fileMeta");
const fileStatus = document.getElementById("fileStatus");

const queryBtn = document.getElementById("queryBtn");
const questionInput = document.getElementById("questionInput");

const sqlOutput = document.getElementById("sqlOutput");
const resultsOutput = document.getElementById("resultsOutput");


// Check that required HTML elements exist

const requiredElements = {
    fileInput,
    uploadBtn,
    uploadStatus,
    fileInfo,
    fileName,
    fileMeta,
    fileStatus,
    queryBtn,
    questionInput,
    sqlOutput,
    resultsOutput
};

for (const [name, element] of Object.entries(requiredElements)) {
    if (!element) {
        console.error(`Missing HTML element: ${name}`);
    }
}


// ============================================
// Application State
// ============================================

let currentDatasetId =
    sessionStorage.getItem("querypilot_dataset_id");

const savedFileName =
    sessionStorage.getItem("querypilot_file_name");

const savedRowCount =
    sessionStorage.getItem("querypilot_row_count");

// Restore previously uploaded dataset
if (currentDatasetId && savedFileName) {
    fileInfo.hidden = false;

    fileName.textContent = savedFileName;
    fileMeta.textContent = `${savedRowCount} rows loaded`;
    fileStatus.textContent = "Uploaded";

    uploadStatus.textContent = "Dataset ready for analysis.";
}


// ============================================
// API Response Handler
// ============================================

async function readApiResponse(response) {
    const text = await response.text();

    let data;

    try {
        data = JSON.parse(text);
    } catch {
        throw new Error(
            `Server returned an invalid response (${response.status}).`
        );
    }

    if (!response.ok) {
        const message =
            typeof data.detail === "string"
                ? data.detail
                : "Request failed.";

        throw new Error(message);
    }

    return data;
}


// ============================================
// File Selection
// ============================================

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (!file) return;

    console.log("Selected file:", file.name);

    // Validate CSV extension
    if (!file.name.toLowerCase().endsWith(".csv")) {

        uploadStatus.textContent = "Please select a CSV file.";

        fileInput.value = "";
        fileInfo.hidden = true;

        return;
    }

    // Validate file size (5 MB)
    if (file.size > 5 * 1024 * 1024) {

        uploadStatus.textContent =
            "File size exceeds the 5 MB limit.";

        fileInput.value = "";
        fileInfo.hidden = true;

        return;
    }

    // A newly selected file needs a new upload
    currentDatasetId = null;
    sessionStorage.removeItem("querypilot_dataset_id");
    sessionStorage.removeItem("querypilot_file_name");
    sessionStorage.removeItem("querypilot_row_count");

    fileInfo.hidden = false;

    fileName.textContent = file.name;
    fileMeta.textContent = "Ready to upload";
    fileStatus.textContent = "Selected";

    uploadStatus.textContent = "";

    resultsOutput.textContent =
        "Upload your selected dataset to start analyzing.";

    sqlOutput.textContent =
        "Your SQL query will appear here.";
});


// ============================================
// CSV Upload
// ============================================

uploadBtn.addEventListener("click", async () => {

    console.log("Upload button clicked.");

    const file = fileInput.files[0];

    // Check file selection
    if (!file) {

        uploadStatus.textContent =
            "Please select a CSV file first.";

        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    try {

        uploadBtn.disabled = true;
        uploadBtn.textContent = "Uploading...";

        fileInfo.hidden = false;

        fileStatus.textContent = "Uploading";
        fileMeta.textContent = "Processing dataset...";

        uploadStatus.textContent = "Uploading your dataset...";

        console.log("Sending upload request...");

        const response = await fetch(
            `${API_BASE_URL}/datasets/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await readApiResponse(response);

        console.log("Upload response:", data);

        // Store uploaded dataset ID
        if (!data.dataset_id) {
            throw new Error(
                "Upload succeeded but no dataset ID was returned."
            );
        }

        currentDatasetId = data.dataset_id;

        sessionStorage.setItem(
            "querypilot_dataset_id",
            currentDatasetId
        );

        sessionStorage.setItem(
            "querypilot_file_name",
            file.name
        );

        sessionStorage.setItem(
            "querypilot_row_count",
            data.rows_loaded
        );

        // Keep uploaded file visible
        fileInfo.hidden = false;

        fileName.textContent = file.name;

        fileMeta.textContent =
            `${data.rows_loaded} rows loaded`;

        fileStatus.textContent = "Uploaded";

        uploadStatus.textContent =
            "Dataset ready for analysis.";

        // Reset SQL and results panels
        sqlOutput.textContent =
            "Your SQL query will appear here.";

        resultsOutput.textContent =
            "Ask a question to explore your dataset.";

        console.log("Dataset ID:", currentDatasetId);

    } catch (error) {

        console.error("Upload failed:", error);

        currentDatasetId = null;

        fileStatus.textContent = "Failed";
        fileMeta.textContent = "Upload unsuccessful";

        uploadStatus.textContent = error.message;

    } finally {

        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload dataset";

    }
});


// ============================================
// Generate SQL and Execute Query
// ============================================

queryBtn.addEventListener("click", async () => {

    console.log("Generate insights button clicked.");

    const question = questionInput.value.trim();

    // Check uploaded dataset
    if (!currentDatasetId) {

        resultsOutput.textContent =
            "Please upload a dataset first.";

        console.warn("No dataset ID available.");

        return;
    }

    // Check question
    if (!question) {

        resultsOutput.textContent =
            "Please enter a question.";

        return;
    }

    try {

        queryBtn.disabled = true;
        queryBtn.textContent = "Generating insights...";

        sqlOutput.textContent = "Generating SQL...";

        resultsOutput.textContent =
            "Analyzing your dataset...";

        console.log("Sending query:", question);
        console.log("Using dataset:", currentDatasetId);

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

        console.log("Query response:", data);

        // Display generated SQL
        sqlOutput.textContent =
            data.sql || "No SQL was generated.";

        // Display query results
        displayResults(data.rows);

    } catch (error) {

        console.error("Query failed:", error);

        sqlOutput.textContent =
            "Query generation failed.";

        resultsOutput.textContent =
            error.message;

    } finally {

        queryBtn.disabled = false;
        queryBtn.textContent = "Generate insights →";

    }

});


// ============================================
// Display Query Results
// ============================================

function displayResults(rows) {
    resultsOutput.innerHTML = "";

    if (!rows || rows.length === 0) {
        resultsOutput.textContent = "No results found.";
        return;
    }

    const columns = Object.keys(rows[0]);

    const wrapper = document.createElement("div");
    wrapper.className = "results-wrapper";

    const table = document.createElement("table");
    table.className = "results-table";

    // Create table header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column.replaceAll("_", " ");
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement("tbody");

    rows.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(column => {
            const td = document.createElement("td");
            const value = row[column];

            td.textContent =
                typeof value === "number"
                    ? Number.isInteger(value)
                        ? value.toLocaleString("en-IN")
                        : value.toLocaleString("en-IN", {
                            maximumFractionDigits: 2
                        })
                    : value ?? "-";

            if (typeof value === "number") {
                td.classList.add("numeric");
            }

            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    resultsOutput.appendChild(wrapper);
}

// ============================================
// End of QueryPilot Frontend
// ============================================
