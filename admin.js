// Sidebar toggle
const sidebar = document.querySelector('.sidebar');
document.querySelector('.sidebar-toggle').addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// Light/Dark mode toggle
const themeBtn = document.querySelector('.theme-toggle');
themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark');
});

// Backend API URL
const API_URL = "http://localhost:3000/api/players";

// Elements
const playersTableBody = document.getElementById("playersTableBody");
const addPlayerForm = document.getElementById("addPlayerForm");

// Show temporary message
function showMessage(msg, color = "#10b981") {
    const messageDiv = document.createElement("div");
    messageDiv.textContent = msg;
    messageDiv.style.background = color;
    messageDiv.style.color = "#fff";
    messageDiv.style.padding = "10px";
    messageDiv.style.margin = "10px 0";
    messageDiv.style.borderRadius = "5px";
    document.querySelector(".content").prepend(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

// Add a single player to table
function addPlayerToTable(player) {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${player.full_name}</td>
        <td>${player.age || ''}</td>
        <td>${player.position || ''}</td>
        <td>${player.team || ''}</td>
        <td>
            <button class="btn-small danger delete-btn">Delete</button>
        </td>
    `;

    // Delete button
    row.querySelector(".delete-btn").addEventListener("click", async () => {
        if (!confirm("Are you sure you want to delete this player?")) return;
        try {
            await fetch(`${API_URL}/${player.id}`, { method: "DELETE" });
            row.remove();
            showMessage("Player deleted successfully", "#ef4444");
        } catch (err) {
            console.error("Error deleting player:", err);
            showMessage("Error deleting player", "#f59e0b");
        }
    });

    playersTableBody.appendChild(row);
}

// Fetch all players
async function loadPlayers() {
    try {
        const res = await fetch(API_URL);
        const players = await res.json();
        playersTableBody.innerHTML = "";
        players.forEach(player => addPlayerToTable(player));
    } catch (err) {
        console.error("Error loading players:", err);
        showMessage("Failed to load players", "#f59e0b");
    }
}

// Add player form
addPlayerForm.addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = new FormData(addPlayerForm);
    const playerData = {
        full_name: formData.get("name"),
        age: parseInt(formData.get("age")) || null,
        position: formData.get("position"),
        team: formData.get("team")
    };

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(playerData)
        });

        if (!res.ok) throw new Error("Failed to add player");

        const newPlayer = await res.json();
        addPlayerForm.reset();
        addPlayerToTable(newPlayer);
        showMessage("Player added successfully");
    } catch (err) {
        console.error("Error adding player:", err);
        showMessage("Failed to add player", "#f59e0b");
    }
});

// Initial load
loadPlayers();
