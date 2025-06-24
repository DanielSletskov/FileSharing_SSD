const apiBase = "http://localhost:5000";

// Upload file with login redirect if unauthorized
document.getElementById("uploadForm").onsubmit = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) return alert("Please select a file to upload.");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch(`${apiBase}/upload`, {
        method: "POST",
        body: formData
    });

    if (res.status === 401) {
        alert("You are not logged in. Redirecting to login...");
        login();
        return;
    }

    const result = await res.json();
    alert(result.message);
    listFiles();
};

// List uploaded files
async function listFiles() {
    const res = await fetch(`${apiBase}/list`);
    if (res.status === 401) {
        alert("Session expired. Redirecting to login...");
        login();
        return;
    }

    const files = await res.json();
    const list = document.getElementById("fileList");
    list.innerHTML = "";
    files.forEach(file => {
        const item = document.createElement("li");
        item.innerHTML = `<a href="${apiBase}/download/${file.id}">${file.name}</a>`;
        list.appendChild(item);
    });
}

// Redirect to GitHub login
function login() {
    window.location.href = `${apiBase}/login/github`;
}

// bind manual login button)
const loginBtn = document.getElementById("loginBtn");
if (loginBtn) {
    loginBtn.onclick = login;
}

// Attach logout behavior to the logout button
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        try {
            const res = await fetch(`${apiBase}/logout`, {
                method: "GET", // or "POST" depending on Flask setup
                credentials: "include" // needed if you're using sessions/cookies
            });

            if (res.ok) {
                alert("Logged out successfully.");
                window.location.href = `${apiBase}/`; // or redirect to login/home page
            } else {
                alert("Logout failed.");
            }
        } catch (err) {
            console.error("Logout error:", err);
            alert("An error occurred during logout.");
        }
    });
}

// Load file list on page load
window.onload = listFiles;