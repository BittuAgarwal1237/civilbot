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

const result = data.result;

currentResult = result;

console.log(data);
console.log(currentResult);
console.log(currentResult.classification);
console.log(currentResult.department);
        
       
        // Save history
        saveComplaintHistory(text, result);

        // Show result
       chatBox.innerHTML += generateActionCard(result);

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



function generateActionCard(result){

return `

<div class="message bot">

    <div class="ai-card">


            <div class="choice-card" onclick="selectOption('email')">

                <div class="choice-number">1</div>

                <div class="choice-info">

                    <h4>Draft Official Email</h4>

                    <p>Generate a professional email.</p>

                </div>

                <div class="choice-arrow">➜</div>

            </div>


            <div class="choice-card" onclick="selectOption('guidelines')">

                <div class="choice-number">2</div>

                <div class="choice-info">

                    <h4>Complaint Guidelines</h4>

                    <p>Understand the complaint process.</p>

                </div>

                <div class="choice-arrow">➜</div>

            </div>

        </div>

    </div>

</div>

`;

}


function showEmailForm(){

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `

    <div class="message bot">

        <div class="email-form">

            <h3>Sender Details</h3>

            <input id="name" placeholder="Full Name">

            <input id="email" placeholder="Email Address">

            <input id="phone" placeholder="Phone Number">

            <input id="address" placeholder="Address">

            <button onclick="continueEmail()">

                Continue →

            </button>

        </div>

    </div>

    `;

}
async function continueEmail(){

    const userData={

        name:document.getElementById("name").value,

        email:document.getElementById("email").value,

        phone:document.getElementById("phone").value,

        address:document.getElementById("address").value

    };

    generateLetter(userData);

}
function selectOption(option){

    switch(option){

       case "email":

    addChatMessage("user","Draft Official Email");

    addChatMessage(
        "bot",
        "📧 I'll prepare an official email.\n\nPlease fill in your details first."
    );

    showEmailForm();

    break;

    
        case "guidelines":

    addChatMessage("user", "Complaint Guidelines");

    addChatMessage(
        "bot",
        "📖 Here are the official complaint guidelines for your issue."
    );

    showGuidelines();

    break;

}

}
function addChatMessage(sender, text){

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `
        <div class="message ${sender}">
            <div class="bubble">
                ${text}
            </div>
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

}
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

    ` + generateActionCard(item.result);
}




function fillSuggestion(text) {

    document.getElementById(
        "complaint"
    ).value = text;
}




function newComplaint(){

    document.getElementById("complaint").value = "";

    document.getElementById("complaint").placeholder =
    "Describe your civic issue...";

    document.getElementById("chat-box").innerHTML = `

    <div class="hero">

        <h2>Report Civic Issues Smarter</h2>

        <p>

            Tell me your civic issue.

            I'll help you file complaints,
            prepare official documents,
            generate emails,
            and guide you through the government process.

        </p>

    </div>

    `;

}



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



window.onload = function () {

    loadHistory();

};

async function generateLetter(userData){

    if(!currentResult){
        alert("Please analyze a complaint first.");
        return;
    }

    try{

        const response = await fetch(
            "http://127.0.0.1:8000/generate-letter",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({

                    issue_type: currentResult.classification.issue_type,

                    location: currentResult.evidence.location,

                    department: currentResult.department,

                    user: userData

                })
            }
        );

        const data = await response.json();
        console.log(data);

        /*
            Backend should return:

            {
                "to":"electricity@department.gov.in",
                "subject":"Complaint regarding Street Light",
                "letter":"Dear Sir..."
            }
        */

        const to = encodeURIComponent(data.to);

        const subject = encodeURIComponent(data.subject);

        const body = encodeURIComponent(data.letter);

        window.open(
            `https://mail.google.com/mail/?view=cm&fs=1&to=${to}&su=${subject}&body=${body}`,
            "_blank"
        );

    }
    catch(error){

        console.error(error);

        alert("Email generation failed.");

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
function showGuidelines() {

    const category = currentResult.classification.category;

    let html = "";

    switch(category){

        case "Electricity":
            html = getElectricityGuidelines();
            break;

        case "Water Supply":
            html = getWaterGuidelines();
            break;

        case "Road Maintenance":
            html = getRoadGuidelines();
            break;

        case "Sanitation":
            html = getSanitationGuidelines();
            break;

        default:
            html = getGeneralGuidelines();
    }

    document.getElementById("chat-box").innerHTML += html;
}
function getElectricityGuidelines(){

return `

<div class="message bot">

<div class="ai-card">

<h3>⚡ Electricity Complaint Guidelines</h3>

<h4>Before Filing</h4>

<ul>
<li>✔ Check if nearby houses are also affected.</li>
<li>✔ Note the exact location or pole number.</li>
<li>✔ Mention how long the issue has existed.</li>
<li>✔ Take a photo if safe.</li>
</ul>

<h4>Complaint Process</h4>

<ol>
<li>Report the electricity issue.</li>
<li>Attach evidence (photo/video).</li>
<li>Submit complaint to DGVCL/UGVCL.</li>
<li>Receive complaint number.</li>
<li>Department inspection.</li>
<li>Repair work.</li>
<li>Complaint closed after verification.</li>
</ol>

<h4>Expected Resolution</h4>

<ul>
<li>⚡ Power Cut : 2-6 Hours</li>
<li>💡 Street Light : 2-7 Days</li>
<li>⚠ Exposed Wire : Immediate</li>
</ul>

<h4>If Not Resolved</h4>

<ul>
<li>Contact Customer Care.</li>
<li>Escalate to Executive Engineer.</li>
<li>Register grievance on PG Portal.</li>
</ul>

</div>

</div>

`;

}

function getWaterGuidelines(){

return `

<div class="message bot">

<div class="ai-card">

<h3>🚰 Water Supply Complaint Guidelines</h3>

<h4>Before Filing</h4>

<ul>
<li>✔ Check if neighbors have the same issue.</li>
<li>✔ Note leakage location.</li>
<li>✔ Mention duration.</li>
<li>✔ Capture photos if possible.</li>
</ul>

<h4>Complaint Process</h4>

<ol>
<li>Report water issue.</li>
<li>Upload evidence.</li>
<li>Department inspection.</li>
<li>Repair pipeline or supply.</li>
<li>Complaint closure.</li>
</ol>

<h4>Expected Resolution</h4>

<ul>
<li>💧 Leakage : 24-48 Hours</li>
<li>🚰 No Water Supply : Same Day</li>
<li>🚿 Low Pressure : 1-3 Days</li>
</ul>

<h4>Escalation</h4>

<ul>
<li>Contact Municipal Water Department.</li>
<li>Escalate to Zone Engineer.</li>
</ul>

</div>

</div>

`;

}

function getRoadGuidelines(){

return `

<div class="message bot">

<div class="ai-card">

<h3>🛣 Road Maintenance Guidelines</h3>

<h4>Before Filing</h4>

<ul>
<li>✔ Mention road name.</li>
<li>✔ Mention nearest landmark.</li>
<li>✔ Upload pothole photos.</li>
<li>✔ Estimate pothole size.</li>
</ul>

<h4>Complaint Process</h4>

<ol>
<li>Report road damage.</li>
<li>Road inspection.</li>
<li>Approval for repair.</li>
<li>Repair work starts.</li>
<li>Quality verification.</li>
<li>Complaint closure.</li>
</ol>

<h4>Expected Resolution</h4>

<ul>
<li>🚧 Small Pothole : 3-7 Days</li>
<li>🛣 Major Damage : 7-30 Days</li>
</ul>

<h4>Escalation</h4>

<ul>
<li>Contact Road Department.</li>
<li>Escalate to Municipal Engineer.</li>
</ul>

</div>

</div>

`;

}

function getSanitationGuidelines(){

return `

<div class="message bot">

<div class="ai-card">

<h3>🗑 Sanitation Complaint Guidelines</h3>

<h4>Before Filing</h4>

<ul>
<li>✔ Mention exact garbage location.</li>
<li>✔ Upload photos.</li>
<li>✔ Mention how long garbage has remained.</li>
</ul>

<h4>Complaint Process</h4>

<ol>
<li>Submit sanitation complaint.</li>
<li>Municipal inspection.</li>
<li>Cleaning team assigned.</li>
<li>Garbage removal.</li>
<li>Complaint closed.</li>
</ol>

<h4>Expected Resolution</h4>

<ul>
<li>🗑 Garbage Collection : 24 Hours</li>
<li>🚛 Overflowing Bin : 1-2 Days</li>
<li>☣ Dead Animal : Immediate</li>
</ul>

<h4>Escalation</h4>

<ul>
<li>Contact Sanitation Officer.</li>
<li>Escalate to Health Department.</li>
</ul>

</div>

</div>

`;

}

function getPublicSafetyGuidelines(){

return `

<div class="message bot">

<div class="ai-card">

<h3>🚨 Public Safety Guidelines</h3>

<h4>Before Filing</h4>

<ul>
<li>✔ Stay away from dangerous area.</li>
<li>✔ Take photos only if safe.</li>
<li>✔ Mention exact location.</li>
</ul>

<h4>Complaint Process</h4>

<ol>
<li>Report the hazard.</li>
<li>Emergency inspection.</li>
<li>Safety barriers installed.</li>
<li>Permanent repair.</li>
<li>Complaint closed.</li>
</ol>

<h4>Expected Resolution</h4>

<ul>
<li>⚠ Open Manhole : Immediate</li>
<li>⚡ Exposed Wire : Immediate</li>
<li>🚧 Dangerous Structure : 1-3 Days</li>
</ul>

<h4>Emergency</h4>

<p>If the situation is life-threatening, immediately contact emergency services.</p>

</div>

</div>

`;

}

function getGeneralGuidelines(){

return `

<div class="message bot">

<div class="ai-card">

<h3>📖 General Complaint Guidelines</h3>

<ul>

<li>✔ Provide accurate location.</li>

<li>✔ Describe the issue clearly.</li>

<li>✔ Mention duration.</li>

<li>✔ Upload photos whenever possible.</li>

<li>✔ Track your complaint number.</li>

<li>✔ Escalate if unresolved.</li>

</ul>

</div>

</div>

`;

}

