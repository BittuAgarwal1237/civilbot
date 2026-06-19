let currentResult = null;
async function sendComplaint() {

    const input = document.getElementById("complaint");
    const text = input.value.trim();

    if (!text) return;

    const chatBox = document.getElementById("chat-box");

    // Remove welcome screen
    if (document.querySelector(".hero")) {
        chatBox.innerHTML = "";
    }

    // User Message
    chatBox.innerHTML += `
        <div class="message user">
            <div class="bubble">
                ${text}
            </div>
        </div>
    `;

    input.value = "";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/complaint",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    complaint: text
                })
            }
        );

        if (!response.ok) {
            throw new Error(
                `Server Error: ${response.status}`
            );
        }

        const data = await response.json();

        console.log("API Response:", data);

        const result = data.result;
        currentResult = result;

        // Save history
        saveComplaintHistory(text, result);

        // Show result
        chatBox.innerHTML += generateAnalysisCard(result);

        chatBox.scrollTop = chatBox.scrollHeight;

    }
    catch (error) {

        console.error(error);

        chatBox.innerHTML += `
            <div class="message bot">
                <div class="bubble">
                    ❌ Error contacting server
                    <br><br>
                    ${error.message}
                </div>
            </div>
        `;
    }
}


/* ===================================
   ANALYSIS CARD
=================================== */
function generateAnalysisCard(result) {

    return `

        <div class="message bot">

            <div class="analysis-card">

                <div class="analysis-title">
                    Complaint Analysis
                </div>

                <div class="analysis-row">
                    <span>Category</span>
                    <strong>${result.classification?.category || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Issue Type</span>
                    <strong>${result.classification?.issue_type || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Location</span>
                    <strong>${result.evidence?.location || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Duration</span>
                    <strong>${result.evidence?.duration || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Urgency</span>
                    <strong>${result.classification?.urgency || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Department</span>
                    <strong>${result.department || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Response</span>
                    <strong>${result.response || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Priority</span>
                    <strong>${result.task?.priority || "N/A"}</strong>
                </div>

                <div class="analysis-row">
                    <span>Resolution Time</span>
                    <strong>${result.task?.estimated_resolution || "N/A"}</strong>
                </div>

                <div class="letter-section">

                    <button
                        class="letter-btn"
                        onclick="generateLetter()">

                        📄 Generate Official Letter

                    </button>

                </div>

            </div>

        </div>

    `;
}

/* ===================================
   SAVE HISTORY
=================================== */

function saveComplaintHistory(complaint, result) {

    let history = JSON.parse(
        localStorage.getItem("complaintHistory")
    ) || [];

    history.unshift({
        complaint,
        result
    });

    history = history.slice(0, 10);

    localStorage.setItem(
        "complaintHistory",
        JSON.stringify(history)
    );

    loadHistory();
}


/* ===================================
   LOAD HISTORY
=================================== */

function loadHistory() {

    const historyList =
        document.getElementById("history-list");

    if (!historyList) return;

    const history = JSON.parse(
        localStorage.getItem("complaintHistory")
    ) || [];

    historyList.innerHTML = "";

    history.forEach((item, index) => {

        historyList.innerHTML += `

            <div
                class="history-item"
                onclick="openHistory(${index})">

                ${item.complaint}

            </div>

        `;
    });
}


/* ===================================
   OPEN HISTORY
=================================== */

function openHistory(index) {

    const history = JSON.parse(
        localStorage.getItem("complaintHistory")
    ) || [];

    const item = history[index];

    if (!item) return;

    currentResult = item.result;

    document.getElementById("chat-box").innerHTML = `

        <div class="message user">
            <div class="bubble">
                ${item.complaint}
            </div>
        </div>

    ` + generateAnalysisCard(item.result);
}


/* ===================================
   SUGGESTIONS
=================================== */

function fillSuggestion(text) {

    document.getElementById(
        "complaint"
    ).value = text;
}


/* ===================================
   NEW COMPLAINT
=================================== */

function newComplaint() {

    document.getElementById(
        "complaint"
    ).value = "";

    document.getElementById(
        "chat-box"
    ).innerHTML = `

        <div class="hero">

            <h2>
                Report Civic Issues Smarter
            </h2>

            <p>
                AI-powered complaint analysis,
                evidence extraction,
                department routing and task generation.
            </p>

        </div>

    `;
}


/* ===================================
   ENTER KEY
=================================== */

document
.getElementById("complaint")
.addEventListener(
    "keydown",
    function(e){

        if(e.key === "Enter"){
            sendComplaint();
        }

    }
);


/* ===================================
   PAGE LOAD
=================================== */

window.onload = function () {

    loadHistory();

};

async function generateLetter() {

    if (!currentResult) {
        alert("Please analyze a complaint first.");
        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/generate-letter",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    issue_type:
                        currentResult.classification.issue_type,

                    location:
                        currentResult.evidence.location,

                    department:
                        currentResult.department
                })
            }
        );

        const data = await response.json();

        const chatBox =
            document.getElementById("chat-box");

        chatBox.innerHTML += `

        <div class="message bot">

            <div class="letter-card">

                <div class="letter-header">
                    📄 Official Complaint Letter
                </div>

                <textarea
                    class="letter-content"
                    readonly>${data.letter}</textarea>

                <button class="copy-btn" onclick="copyLetter()">
    Copy Letter
</button>

<button
    class="download-btn"
    onclick="downloadLetter()">

    Download TXT

</button>

            </div>

        </div>

        `;

        chatBox.scrollTop =
            chatBox.scrollHeight;

    }
    catch(error){

        console.error(error);

        alert("Letter generation failed");

    }
}
function copyLetter() {

    const letter =
        document.querySelector(
            ".letter-content"
        );

    navigator.clipboard.writeText(
        letter.value
    );

    alert("Letter copied successfully!");
}
function downloadLetter() {

    const letter =
        document.querySelector(".letter-content");

    if (!letter) {
        alert("No letter found");
        return;
    }

    const blob = new Blob(
        [letter.value],
        { type: "text/plain" }
    );

    const url =
        window.URL.createObjectURL(blob);

    const a =
        document.createElement("a");

    a.href = url;
    a.download = "Complaint_Letter.txt";

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);

    window.URL.revokeObjectURL(url);
}