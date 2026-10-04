const uploadButton = document.getElementById("uploadButton");
const askButton = document.getElementById("askButton");

const fileInput = document.getElementById("fileInput");
const questionInput = document.getElementById("questionInput");

const uploadStatus = document.getElementById("uploadStatus");

const answerSection = document.getElementById("answerSection");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");

const documentStats = document.getElementById("documentStats");

let currentFilename = null;


// ========================================
// UPLOAD DOCUMENT
// ========================================

uploadButton.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Please select a PDF.";
        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    uploadStatus.textContent = "Processing document...";
    documentStats.innerHTML = "";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Upload failed."
            );
        }

        // Remember the currently selected document
        currentFilename = data.filename;


        // --------------------------------
        // New document
        // --------------------------------

if (data.status === "Document indexed successfully") {

    uploadStatus.textContent =
        `✓ ${data.filename} processed successfully.`;

} else if (data.status === "Document already indexed.") {

    uploadStatus.textContent =
        `✓ ${data.filename} is already indexed.`;

} else {

    uploadStatus.textContent =
        `✓ ${data.filename} is ready.`;
}


const stats = data.statistics;

if (stats) {

    documentStats.innerHTML = `
        <div class="stats">

            <div class="stat">
                <strong>${stats.pages_with_text}</strong>
                <span>Pages</span>
            </div>

            <div class="stat">
                <strong>${stats.total_chunks}</strong>
                <span>Chunks</span>
            </div>

            <div class="stat">
                <strong>${stats.total_words.toLocaleString()}</strong>
                <span>Words</span>
            </div>

            <div class="stat">
                <strong>${stats.average_words_per_page}</strong>
                <span>Avg. Words/Page</span>
            </div>

        </div>
    `;
}

        // --------------------------------
        // Existing document
        // --------------------------------

        else if (data.status === "Document already indexed.") {

            uploadStatus.textContent =
                `✓ ${data.filename} is already indexed.`;

            documentStats.innerHTML = `
                <p>Document is ready for questions.</p>
            `;
        }


        // --------------------------------
        // Unknown successful response
        // --------------------------------

        else {

            uploadStatus.textContent =
                `✓ ${data.filename} is ready.`;
        }


    } catch (error) {

        uploadStatus.textContent =
            `Error: ${error.message}`;
    }
});


// ========================================
// ASK QUESTION
// ========================================

askButton.addEventListener("click", async () => {

    // Check whether a document has been uploaded
    if (!currentFilename) {

        answerSection.style.display = "block";

        answer.textContent =
            "Please upload a document first.";

        sources.innerHTML = "";

        return;
    }


    // Get question
    const question = questionInput.value.trim();


    // Check question
    if (!question) {

        answerSection.style.display = "block";

        answer.textContent =
            "Please enter a question.";

        sources.innerHTML = "";

        return;
    }


    answer.textContent =
        "Searching document...";

    sources.innerHTML = "";

    answerSection.style.display = "block";


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    query: question,
                    filename: currentFilename
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Question failed."
            );
        }


        // Display answer
        answer.textContent =
            data.answer;


        // Display sources
        if (
            data.sources &&
            data.sources.length > 0
        ) {

            data.sources.forEach(source => {

                const sourceElement =
                    document.createElement("div");

                sourceElement.className =
                    "source";

                sourceElement.textContent =
                    `📄 ${source.filename} — Page ${source.page_number}`;

                sources.appendChild(
                    sourceElement
                );
            });

        } else {

            sources.textContent =
                "No sources found.";
        }


    } catch (error) {

        answer.textContent =
            `Error: ${error.message}`;

        sources.innerHTML = "";
    }
});