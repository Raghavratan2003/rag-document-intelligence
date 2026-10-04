const uploadButton = document.getElementById("uploadButton");
const askButton = document.getElementById("askButton");

const fileInput = document.getElementById("fileInput");
const questionInput = document.getElementById("questionInput");

const uploadStatus = document.getElementById("uploadStatus");

const answerSection = document.getElementById("answerSection");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");

const documentStats = document.getElementById("documentStats");


uploadButton.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Please select a PDF.";
        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    uploadStatus.textContent = "Processing document...";

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
            throw new Error(data.detail || "Upload failed.");
        }

        uploadStatus.textContent =
            `✓ ${data.filename} processed successfully.`;

        const stats = data.statistics;

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

    } catch (error) {

        uploadStatus.textContent =
            `Error: ${error.message}`;
    }
});


askButton.addEventListener("click", async () => {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    answer.textContent = "Searching document...";
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
                    query: question
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Question failed.");
        }

        answer.textContent = data.answer;

        data.sources.forEach(source => {

            const sourceElement = document.createElement("div");

            sourceElement.className = "source";

            sourceElement.textContent =
                `📄 ${source.filename} — Page ${source.page_number}`;

            sources.appendChild(sourceElement);
        });

    } catch (error) {

        answer.textContent =
            `Error: ${error.message}`;
    }
});