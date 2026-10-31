
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


// ============================================
// Application State
// ============================================

let currentDatasetId = sessionStorage.getItem(
    "querypilot_dataset_id"
);

const savedFileName = sessionStorage.getItem(
    "querypilot_file_name"
);

const savedRowCount = sessionStorage.getItem(
    "querypilot_row_count"
);


// ============================================
// Restore Previous Dataset
// ============================================

if (currentDatasetId && savedFileName) {

    fileInfo.hidden = false;

    fileName.textContent = savedFileName;

    fileMeta.textContent =
        `${savedRowCount || 0} rows loaded`;

    fileStatus.textContent = "Uploaded";

    uploadStatus.textContent =
        "Dataset ready for analysis.";

    resultsOutput.textContent =
        "Ask a question to explore your dataset.";

    console.log("Restored dataset:", currentDatasetId);
}


// ============================================
// API Response Handler
// ============================================

async function readApiResponse(response) {

    const responseText = await response.text();

    console.log("API Status:", response.status);
    console.log("Raw API Response:", responseText);

    let data;

    try {

        data = JSON.parse(responseText);

    } catch {

        throw new Error(
            `Invalid server response (${response.status}).`
        );

    }

    if (!response.ok) {

        throw new Error(
            data?.detail || "Request failed."
        );

    }

    if (!data || typeof data !== "object") {

        throw new Error(
            "Backend returned an empty or invalid response."
        );

    }

    return data;
}


// ============================================
// Clear Saved Dataset
// ============================================

function clearSavedDataset() {

    currentDatasetId = null;

    sessionStorage.removeItem("querypilot_dataset_id");
    sessionStorage.removeItem("querypilot_file_name");
    sessionStorage.removeItem("querypilot_row_count");

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

        uploadStatus.textContent =
            "Please select a CSV file.";

        fileInput.value = "";

        return;
    }


    // Validate file size (5 MB)

    if (file.size > 5 * 1024 * 1024) {

        uploadStatus.textContent =
            "File size exceeds the 5 MB limit.";

        fileInput.value = "";

        return;
    }


    // New file requires a new upload

    clearSavedDataset();


    // Keep selected file visible

    fileInfo.hidden = false;

    fileName.textContent = file.name;

    fileMeta.textContent = "Ready to upload";

    fileStatus.textContent = "Selected";

    uploadStatus.textContent = "";


    // Reset previous results

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


    // Prepare upload data

    const formData = new FormData();

    formData.append("file", file);


    try {

        uploadBtn.disabled = true;

        uploadBtn.textContent = "Uploading...";

        fileInfo.hidden = false;

        fileStatus.textContent = "Uploading";

        fileMeta.textContent = "Processing dataset...";

        uploadStatus.textContent =
            "Uploading your dataset...";


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


        // Validate backend response

        if (!data.dataset_id) {

            throw new Error(
                "Upload response does not contain a dataset ID."
            );

        }


        // Save dataset ID

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
            String(data.rows_loaded)
        );


        // Update dataset preview

        fileInfo.hidden = false;

        fileName.textContent = file.name;

        fileMeta.textContent =
            `${data.rows_loaded} rows loaded`;

        fileStatus.textContent = "Uploaded";

        uploadStatus.textContent =
            "Dataset ready for analysis.";


        // Reset SQL and results

        sqlOutput.textContent =
            "Your SQL query will appear here.";

        resultsOutput.textContent =
            "Ask a question to explore your dataset.";


        console.log(
            "Dataset uploaded successfully:",
            currentDatasetId
        );

    } catch (error) {

        console.error("Upload failed:", error);


        // Do not remove the selected file preview

        currentDatasetId = null;

        fileInfo.hidden = false;

        fileStatus.textContent = "Failed";

        fileMeta.textContent =
            "Selected file — upload unsuccessful";

        uploadStatus.textContent =
            error.message;


        // Prevent queries against an unsuccessful upload

        console.warn(
            "Dataset was not uploaded successfully."
        );

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

        queryBtn.textContent =
            "Generating insights...";

        sqlOutput.textContent =
            "Generating SQL...";

        resultsOutput.textContent =
            "Analyzing your dataset...";


        console.log("Sending query:", question);

        console.log(
            "Using dataset:",
            currentDatasetId
        );


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

        queryBtn.textContent =
            "Generate insights →";

    }

});


// ============================================
// Display Query Results
// ============================================

function displayResults(rows) {

    resultsOutput.innerHTML = "";


    if (!Array.isArray(rows) || rows.length === 0) {

        resultsOutput.textContent =
            "No results found.";

        return;
    }


    const columns = Object.keys(rows[0]);


    // Create wrapper

    const wrapper = document.createElement("div");

    wrapper.className = "results-wrapper";


    // Create table

    const table = document.createElement("table");

    table.className = "results-table";


    // ========================================
    // Table Header
    // ========================================

    const thead = document.createElement("thead");

    const headerRow = document.createElement("tr");


    columns.forEach(column => {

        const th = document.createElement("th");

        th.textContent = column.replaceAll("_", " ");

        headerRow.appendChild(th);

    });


    thead.appendChild(headerRow);

    table.appendChild(thead);


    // ========================================
    // Table Body
    // ========================================

    const tbody = document.createElement("tbody");


    rows.forEach(row => {

        const tr = document.createElement("tr");


        columns.forEach(column => {

            const td = document.createElement("td");

            const value = row[column];


            if (typeof value === "number") {

                td.textContent = Number.isInteger(value)
                    ? value.toLocaleString("en-IN")
                    : value.toLocaleString("en-IN", {
                        maximumFractionDigits: 2
                    });

                td.classList.add("numeric");

            } else {

                td.textContent = value ?? "-";

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


