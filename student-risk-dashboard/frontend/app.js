const API_BASE = "/api";

function uploadData() {
    const fileInput = document.getElementById("csvFileInput");
    const file = fileInput.files[0];
    
    if (!file) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const uploadBtn = document.getElementById("uploadDataBtn");
    if (uploadBtn) {
        uploadBtn.innerText = "UPLOADING...";
        uploadBtn.disabled = true;
    }

    fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
    })
    .then(res => {
        if (res.ok) {
            alert("Student data uploaded and processed successfully!");
            // Open student list in a new window/tab as requested
            window.open("students.html", "_blank");
        } else {
            return res.json().then(data => {
                alert("Upload failed: " + (data.detail || "Unknown error"));
            });
        }
    })
    .catch(err => {
        console.error("Upload error:", err);
        alert("Connection failed. Is the server running?");
    })
    .finally(() => {
        if (uploadBtn) {
            uploadBtn.innerText = "UPLOAD DATA";
            uploadBtn.disabled = false;
        }
    });
}

function generateMessage() {
    let message = "Dear Parent, your child has been identified as needing additional academic support. Please contact the school for counseling and assistance.";
    const textarea = document.querySelector("textarea");
    if (textarea) {
        textarea.value = message;
    }
}

function checkSchemes() {
    alert("Checking eligible government schemes for the student...");
}

document.addEventListener("DOMContentLoaded", function(){
    const buttons = document.querySelectorAll("button");
    
    buttons.forEach(btn => {
        const text = btn.innerText.trim();
        
        if (text.includes("UPLOAD DATA") || btn.id === "uploadDataBtn") {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                uploadData();
            });
        }
        
        if (text.includes("Parent Meeting")) {
             btn.addEventListener("click", (e) => {
                e.preventDefault();
                generateMessage();
            });
        }

        if (text.includes("Scholarship Portal") || text.includes("Scheme")) {
             btn.addEventListener("click", (e) => {
                e.preventDefault();
                checkSchemes();
            });
        }
    });
});
