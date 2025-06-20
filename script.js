const apiBase = "http://localhost:5000";

document.getElementById("uploadForm").onsubmit = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch(`${apiBase}/upload`, {
        method: "POST",
        body: formData
    });

    const result = await res.json();
    alert(result.message);
    listFiles();
};

async function listFiles() {
    const res = await fetch(`${apiBase}/list`);
    const files = await res.json();
    const list = document.getElementById("fileList");
    list.innerHTML = "";
    files.forEach(file => {
        const item = document.createElement("li");
        item.innerHTML = `<a href="${apiBase}/download/${file.id}">${file.name}</a>`;
        list.appendChild(item);
    });
}

window.onload = listFiles;
