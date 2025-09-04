<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scout Management</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --success: #4cc9f0;
            --danger: #f72585;
            --warning: #f77f00;
            --info: #4895ef;
            --light: #f8f9fa;
            --dark: #212529;
            --background: #f0f2f5;
            --card-bg: #ffffff;
            --text: #333333;
            --border: #dddddd;
            --shadow: rgba(0, 0, 0, 0.1);
        }

        .dark {
            --background: #121212;
            --card-bg: #1e1e1e;
            --text: #f0f0f0;
            --border: #444444;
            --shadow: rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--background);
            color: var(--text);
            line-height: 1.6;
        }

        .dashboard {
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar Styles */
        .sidebar {
            width: 250px;
            background: linear-gradient(to bottom, var(--primary), var(--secondary));
            color: white;
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 2px 0 10px var(--shadow);
            transition: width 0.3s ease;
        }

        .sidebar.collapsed {
            width: 70px;
        }

        .sidebar.collapsed .logo-text,
        .sidebar.collapsed .menu-text {
            display: none;
        }

        .top-bar {
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .sidebar-toggle {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 1.2rem;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.5rem;
            font-weight: bold;
        }

        .menu {
            list-style: none;
            padding: 20px 0;
            flex-grow: 1;
        }

        .menu-item {
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .menu-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .menu-item a {
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 15px;
            width: 100%;
        }

        .dropdown {
            position: relative;
        }

        .submenu {
            list-style: none;
            padding-left: 30px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }

        .dropdown:hover .submenu {
            max-height: 200px;
        }

        .submenu li {
            padding: 10px 0;
        }

        .submenu a {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }

        .submenu a:hover {
            color: white;
        }

        .theme-toggle {
            margin: 20px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            align-self: center;
        }

        /* Main Content Styles */
        .main-content {
            flex: 1;
            margin-left: 250px;
            padding: 20px;
            transition: margin-left 0.3s ease;
        }

        .sidebar.collapsed ~ .main-content {
            margin-left: 70px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--card-bg);
            padding: 8px 15px;
            border-radius: 20px;
            box-shadow: 0 2px 5px var(--shadow);
        }

        .content {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px var(--shadow);
            margin-bottom: 30px;
        }

        h1 {
            color: var(--primary);
            margin-bottom: 10px;
        }

        h2 {
            margin: 25px 0 15px;
            color: var(--secondary);
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }

        form {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        input, select {
            padding: 12px 15px;
            border: 1px solid var(--border);
            border-radius: 5px;
            background: var(--card-bg);
            color: var(--text);
            font-size: 1rem;
        }

        button {
            padding: 12px 20px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            transition: all 0.3s;
        }

        button:hover {
            background: var(--secondary);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px var(--shadow);
        }

        /* Table Styles */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px var(--shadow);
        }

        thead {
            background: var(--primary);
            color: white;
        }

        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }

        tr {
            transition: all 0.3s;
        }

        tr:hover {
            background: rgba(67, 97, 238, 0.05);
            transform: scale(1.01);
            box-shadow: 0 2px 8px var(--shadow);
        }

        .btn-small {
            padding: 8px 12px;
            font-size: 0.85rem;
        }

        .danger {
            background: var(--danger);
        }

        .danger:hover {
            background: #d1144a;
        }

        .success {
            background: var(--success);
        }

        .success:hover {
            background: #3aa8d0;
        }

        .warning {
            background: var(--warning);
        }
        .menu-item a {
  color: white;       /* make text white */
  text-decoration: none; /* remove underline */
}

.menu-item a:hover {
  color: #f1c40f;     /* optional: show yellow on hover */
}
        .warning:hover {
            background: #e57c00;
        }

        .message {
            padding: 12px;
            border-radius: 5px;
            margin: 15px 0;
            text-align: center;
            font-weight: bold;
            animation: fadeIn 0.5s, fadeOut 0.5s 2.5s forwards;
        }

        /* Stats Cards */
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .stat-card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 10px var(--shadow);
            transition: all 0.3s;
            animation: slideIn 0.5s forwards;
            opacity: 0;
            transform: translateY(20px);
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px var(--shadow);
        }

        .stat-card h3 {
            color: var(--secondary);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
            margin: 10px 0;
        }

        .stat-card .description {
            color: #666;
            font-size: 0.9rem;
        }

        .scout-info {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 15px;
        }

        .scout-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .scout-details {
            flex: 1;
            overflow: hidden;
        }

        .scout-name {
            font-weight: bold;
            color: var(--text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .scout-stats {
            display: flex;
            gap: 15px;
            margin-top: 5px;
        }

        .stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .stat-value {
            font-weight: bold;
            color: var(--primary);
        }

        .stat-label {
            font-size: 0.8rem;
            color: #666;
        }

        /* Activity chart */
        .activity-chart {
            height: 100px;
            display: flex;
            align-items: flex-end;
            gap: 5px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border);
        }

        .chart-bar {
            flex: 1;
            background: var(--success);
            border-radius: 3px 3px 0 0;
            transition: all 0.3s;
            position: relative;
        }

        .chart-bar:hover {
            background: var(--primary);
        }

        .chart-bar span {
            position: absolute;
            bottom: -25px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.8rem;
            color: #666;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }

        @keyframes slideIn {
            from { 
                opacity: 0;
                transform: translateY(20px);
            }
            to { 
                opacity: 1;
                transform: translateY(0);
            }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 2000;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: var(--card-bg);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            width: 90%;
            max-width: 500px;
            animation: modalFadeIn 0.3s;
        }

        @keyframes modalFadeIn {
            from { opacity: 0; transform: translateY(-50px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 10px;
            border-bottom: 1px solid var(--border);
        }

        .close-modal {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text);
        }

        /* Loading spinner */
        .loader {
            border: 5px solid var(--background);
            border-top: 5px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
           100% { transform: rotate(360deg); }
        }

        /* Responsive Design */
        @media (max-width: 992px) {
            .sidebar {
                width: 70px;
            }
            
            .logo-text, .menu-text {
                display: none;
            }
            
            .main-content {
                margin-left: 70px;
            }
            
            form {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 0;
                overflow: hidden;
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .sidebar.collapsed {
                width: 70px;
            }
            
            .sidebar-toggle {
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1100;
                background: var(--primary);
                padding: 10px;
                border-radius: 5px;
            }
            
            table {
                display: block;
                overflow-x: auto;
            }
            
            .stats-container {
                grid-template-columns: 1fr;
            }
            
            .scout-stats {
                flex-wrap: wrap;
                gap: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="top-bar">
                <button class="sidebar-toggle"><i class="fas fa-bars"></i></button>
                <div class="logo"><i class="fas fa-futbol"></i> <span class="logo-text">Admin</span></div>
            </div>

            <ul class="menu">
                <li class="menu-item" title="Dashboard">
                    <a href="admin.html"><i class="fas fa-home"></i> <span class="menu-text">Dashboard</span></a>
                </li>

                <!-- Players Dropdown -->
                <li class="menu-item" title="Players">
                    <a href="players.html"><i class="fas fa-user"></i> <span class="menu-text">Players</span></a>
                </li>

                <!-- Scouts Dropdown -->
                 <!-- Scouts -->
                <li class="menu-item" title="Scouts">
                    <i class="fas fa-users"></i> <a href="Scoutmanger.html">Scouts</a>
                </li>

                <!-- Teams Dropdown -->
                <li class="menu-item" title="Teams">
                    <a href="teams.html"><i class="fas fa-futbol"></i> <span class="menu-text">Teams</span></a>
                </li>

                <!-- Subscriptions -->
                <li class="menu-item" title="Subscriptions">
                    <a href="subscriptions.html"><i class="fas fa-credit-card"></i> <span class="menu-text">Subscriptions</span></a>
                </li>

                <!-- Reports -->
                <li class="menu-item" title="Reports">
                    <a href="admin-Reports.html"><i class="fas fa-file-alt"></i> <span class="menu-text">Reports</span></a>
                </li>

                

                <!-- Settings -->
                <li class="menu-item" title="Settings">
                    <a href="settings.html"><i class="fas fa-cog"></i> <span class="menu-text">Settings</span></a>
                </li>
            </ul>

            <button class="theme-toggle"><i class="fas fa-sun"></i></button>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <header>
                <h1>Scout Management</h1>
                <div class="user-info">
                    <span>Admin <i class="fas fa-user-shield"></i></span>
                </div>
            </header>

            <section class="content">
                <h2>Scout Statistics</h2>
                <div class="stats-container" id="statsContainer">
                    <div class="loader" id="statsLoader"></div>
                </div>

                <h2>Add New Scout</h2>
                <form id="addScoutForm">
                    <input type="text" name="name" placeholder="Scout Name" required>
                    <input type="text" name="region" placeholder="Region" required>
                    <input type="text" name="contactInfo" placeholder="Contact Info" required>
                    <select name="experienceLevel" required>
                        <option value="">Select Experience Level</option>
                        <option value="Junior">Junior</option>
                        <option value="Mid-level">Mid-level</option>
                        <option value="Senior">Senior</option>
                    </select>
                    <select name="statusId" id="statusDropdown" required>
                        <option value="">Select Status</option>
                        <!-- Status options will be populated dynamically -->
                    </select>
                    <select name="assignedClubId" id="clubDropdown">
                        <option value="">Select Club (Optional)</option>
                        <!-- Club options will be populated dynamically -->
                    </select>
                    <input type="number" name="playersFound" placeholder="Players Found" min="0" value="0">
                    <input type="number" name="successRate" placeholder="Success Rate (%)" min="0" max="100" value="0">
                    <button type="submit" class="pulse">Add Scout</button>
                </form>

                <h2>Scouts List</h2>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Region</th>
                                <th>Contact Info</th>
                                <th>Status</th>
                                <th>Experience</th>
                                <th>Players Found</th>
                                <th>Success Rate</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="scoutsTableBody">
                            <tr>
                                <td colspan="8" style="text-align: center;">
                                    <div class="loader" id="tableLoader"></div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </div>

    <!-- Edit Scout Modal -->
    <div class="modal" id="editScoutModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Scout</h2>
                <button class="close-modal">&times;</button>
            </div>
            <form id="editScoutForm">
                <input type="hidden" id="editScoutId" name="scoutId">
                <input type="text" id="editScoutName" name="name" placeholder="Scout Name" required>
                <input type="text" id="editScoutRegion" name="region" placeholder="Region" required>
                <input type="text" id="editScoutContact" name="contactInfo" placeholder="Contact Info" required>
                <select id="editScoutExperience" name="experienceLevel" required>
                    <option value="Junior">Junior</option>
                    <option value="Mid-level">Mid-level</option>
                    <option value="Senior">Senior</option>
                </select>
                <select id="editScoutStatus" name="statusId" required>
                    <!-- Status options will be populated dynamically -->
                </select>
                <select id="editScoutClub" name="assignedClubId">
                    <!-- Club options will be populated dynamically -->
                </select>
                <input type="number" id="editPlayersFound" name="playersFound" placeholder="Players Found" min="0">
                <input type="number" id="editSuccessRate" name="successRate" placeholder="Success Rate (%)" min="0" max="100">
                <button type="submit">Update Scout</button>
            </form>
        </div>
    </div>

    <!-- Update Stats Modal -->
    <div class="modal" id="updateStatsModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Update Scout Performance</h2>
                <button class="close-modal">&times;</button>
            </div>
            <form id="updateStatsForm">
                <input type="hidden" id="updateScoutId" name="scoutId">
                <div class="form-group">
                    <label for="updatePlayersFound">Players Found</label>
                    <input type="number" id="updatePlayersFound" name="playersFound" min="0" required>
                </div>
                <div class="form-group">
                    <label for="updateSuccessRate">Success Rate (%)</label>
                    <input type="number" id="updateSuccessRate" name="successRate" min="0" max="100" required>
                </div>
                <button type="submit">Update Performance</button>
            </form>
        </div>
    </div>

    <script>
        // Backend API URL
        const API_URL = "http://localhost:3000/api";

        // Elements
        const scoutsTableBody = document.getElementById("scoutsTableBody");
        const addScoutForm = document.getElementById("addScoutForm");
        const editScoutForm = document.getElementById("editScoutForm");
        const updateStatsForm = document.getElementById("updateStatsForm");
        const editScoutModal = document.getElementById("editScoutModal");
        const updateStatsModal = document.getElementById("updateStatsModal");
        const closeModalBtn = document.querySelectorAll('.close-modal');
        const statsContainer = document.getElementById("statsContainer");
        const statusDropdown = document.querySelector('select[name="statusId"]');
        const clubDropdown = document.querySelector('select[name="assignedClubId"]');

        // Show temporary message
        function showMessage(msg, color = "#10b981") {
            const messageDiv = document.createElement("div");
            messageDiv.classList.add("message");
            messageDiv.textContent = msg;
            messageDiv.style.background = color;
            messageDiv.style.color = "#fff";
            document.querySelector(".content").prepend(messageDiv);
            setTimeout(() => messageDiv.remove(), 3000);
        }

        // Add a single scout to table
        function addScoutToTable(scout, index) {
            const row = document.createElement("tr");
            row.style.animationDelay = `${index * 0.05}s`;
            
            // Determine status color
            let statusColor = "#4cc9f0";
            if (scout.status === "Inactive") statusColor = "#f72585";
            if (scout.status === "Pending") statusColor = "#f77f00";
            
            row.innerHTML = `
                <td>${scout.name}</td>
                <td>${scout.region}</td>
                <td>${scout.contactInfo}</td>
                <td><span style="color: ${statusColor}; font-weight: bold">${scout.status}</span></td>
                <td>${scout.experienceLevel}</td>
                <td>${scout.players_found || 0}</td>
                <td>${scout.success_rate || 0}%</td>
                <td>
                    <button class="btn-small danger delete-btn" data-id="${scout.scoutId}">Delete</button>
                    <button class="btn-small success edit-btn" data-id="${scout.scoutId}">Edit</button>
                    <button class="btn-small warning stats-btn" data-id="${scout.scoutId}">Update Stats</button>
                </td>
            `;

            // Delete button
            row.querySelector(".delete-btn").addEventListener("click", async () => {
                if (!confirm("Are you sure you want to delete this scout?")) return;
                try {
                    const response = await fetch(`${API_URL}/scouts/${scout.scoutId}`, { 
                        method: "DELETE" 
                    });
                    const result = await response.json();
                    
                    if (response.ok) {
                        row.remove();
                        showMessage("Scout deleted successfully", "#ef4444");
                        loadStatistics(); // Refresh statistics
                    } else {
                        throw new Error(result.error);
                    }
                } catch (err) {
                    console.error("Error deleting scout:", err);
                    showMessage("Error deleting scout: " + err.message, "#f59e0b");
                }
            });

            // Edit button
            row.querySelector(".edit-btn").addEventListener("click", () => {
                openEditModal(scout);
            });

            // Update stats button
            row.querySelector(".stats-btn").addEventListener("click", () => {
                openUpdateStatsModal(scout);
            });

            scoutsTableBody.appendChild(row);
        }

        // Open edit modal with scout data
        function openEditModal(scout) {
            document.getElementById("editScoutId").value = scout.scoutId;
            document.getElementById("editScoutName").value = scout.name;
            document.getElementById("editScoutRegion").value = scout.region;
            document.getElementById("editScoutContact").value = scout.contactInfo;
            document.getElementById("editScoutExperience").value = scout.experienceLevel;
            document.getElementById("editPlayersFound").value = scout.players_found || 0;
            document.getElementById("editSuccessRate").value = scout.success_rate || 0;
            
            // Set the status value if available
            if (scout.statusId) {
                document.getElementById("editScoutStatus").value = scout.statusId;
            }
            
            // Set the club value if available
            if (scout.assignedClubId) {
                document.getElementById("editScoutClub").value = scout.assignedClubId;
            }
            
            editScoutModal.style.display = "flex";
        }

        // Open update stats modal with scout data
        function openUpdateStatsModal(scout) {
            document.getElementById("updateScoutId").value = scout.scoutId;
            document.getElementById("updatePlayersFound").value = scout.players_found || 0;
            document.getElementById("updateSuccessRate").value = scout.success_rate || 0;
            
            updateStatsModal.style.display = "flex";
        }

        // Close modals
        closeModalBtn.forEach(btn => {
            btn.addEventListener("click", () => {
                editScoutModal.style.display = "none";
                updateStatsModal.style.display = "none";
            });
        });

        // Close modals when clicking outside
        window.addEventListener("click", (e) => {
            if (e.target === editScoutModal) {
                editScoutModal.style.display = "none";
            }
            if (e.target === updateStatsModal) {
                updateStatsModal.style.display = "none";
            }
        });

        // Load scouts from the database
        async function loadScouts() {
            try {
                const response = await fetch(`${API_URL}/scouts`);
                if (!response.ok) throw new Error('Failed to fetch scouts');
                
                const scouts = await response.json();
                scoutsTableBody.innerHTML = "";
                
                if (scouts.length === 0) {
                    scoutsTableBody.innerHTML = `<tr><td colspan="8" style="text-align: center;">No scouts found</td></tr>`;
                    return;
                }
                
                scouts.forEach((scout, index) => addScoutToTable(scout, index));
            } catch (err) {
                console.error("Error loading scouts:", err);
                scoutsTableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger);">Error loading scouts: ${err.message}</td></tr>`;
            }
        }

        // Load statuses for dropdown
        async function loadStatuses() {
            try {
                const response = await fetch(`${API_URL}/statuses`);
                if (!response.ok) throw new Error('Failed to fetch statuses');
                
                const statuses = await response.json();
                statusDropdown.innerHTML = '<option value="">Select Status</option>';
                document.getElementById("editScoutStatus").innerHTML = '<option value="">Select Status</option>';
                
                statuses.forEach(status => {
                    const option = document.createElement("option");
                    option.value = status.statusId;
                    option.textContent = status.description;
                    statusDropdown.appendChild(option.cloneNode(true));
                    document.getElementById("editScoutStatus").appendChild(option);
                });
            } catch (err) {
                console.error("Error loading statuses:", err);
                showMessage("Failed to load statuses", "#f59e0b");
            }
        }

        // Load clubs for dropdown
        async function loadClubs() {
            try {
                const response = await fetch(`${API_URL}/clubs`);
                if (!response.ok) throw new Error('Failed to fetch clubs');
                
                const clubs = await response.json();
                clubDropdown.innerHTML = '<option value="">Select Club (Optional)</option>';
                document.getElementById("editScoutClub").innerHTML = '<option value="">Select Club (Optional)</option>';
                
                clubs.forEach(club => {
                    const option = document.createElement("option");
                    option.value = club.clubId;
                    option.textContent = club.name;
                    clubDropdown.appendChild(option.cloneNode(true));
                    document.getElementById("editScoutClub").appendChild(option);
                });
            } catch (err) {
                console.error("Error loading clubs:", err);
                showMessage("Failed to load clubs", "#f59e0b");
            }
        }

        // Load statistics
        async function loadStatistics() {
            try {
                const response = await fetch(`${API_URL}/scouts/stats`);
                if (!response.ok) throw new Error('Failed to fetch statistics');
                
                const stats = await response.json();
                
                statsContainer.innerHTML = `
                    <div class="stat-card" style="animation-delay: 0.1s;">
                        <h3><i class="fas fa-users"></i> Total Scouts</h3>
                        <div class="value">${stats.totalScouts}</div>
                        <div class="description">${stats.activeScouts} active, ${stats.inactiveScouts} inactive</div>
                    </div>

                    <div class="stat-card" style="animation-delay: 0.2s;">
                        <h3><i class="fas fa-star"></i> Top Performer</h3>
                        <div class="scout-info">
                            <div class="scout-avatar">${stats.mostActive.initials}</div>
                            <div class="scout-details">
                                <div class="scout-name">${stats.mostActive.name || 'No data'}</div>
                                <div class="scout-stats">
                                    <div class="stat">
                                        <span class="stat-value">${stats.mostActive.players_found || 0}</span>
                                        <span class="stat-label">Players</span>
                                    </div>
                                    <div class="stat">
                                        <span class="stat-value">${stats.mostActive.success_rate || 0}%</span>
                                        <span class="stat-label">Success</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="stat-card" style="animation-delay: 0.3s;">
                        <h3><i class="fas fa-chart-line"></i> Performance</h3>
                        <div class="value">${stats.avgSuccessRate}%</div>
                        <div class="description">Average success rate</div>
                        <div class="activity-chart">
                            ${stats.weeklyActivity.map(day => 
                                `<div class="chart-bar" style="height: ${day.value}%;"><span>${day.label}</span></div>`
                            ).join('')}
                        </div>
                    </div>
                `;
            } catch (err) {
                console.error("Error loading statistics:", err);
                statsContainer.innerHTML = `<div class="message">Error loading statistics: ${err.message}</div>`;
            }
        }

        // Add scout form
        addScoutForm.addEventListener("submit", async function(e) {
            e.preventDefault();

            const formData = new FormData(addScoutForm);
            const scoutData = {
                name: formData.get("name"),
                region: formData.get("region"),
                contactInfo: formData.get("contactInfo"),
                experienceLevel: formData.get("experienceLevel"),
                statusId: parseInt(formData.get("statusId")),
                assignedClubId: formData.get("assignedClubId") ? parseInt(formData.get("assignedClubId")) : null,
                players_found: parseInt(formData.get("playersFound")) || 0,
                success_rate: parseInt(formData.get("successRate")) || 0
            };

            try {
                const response = await fetch(`${API_URL}/scouts`, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json" 
                    },
                    body: JSON.stringify(scoutData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    addScoutForm.reset();
                    showMessage("Scout added successfully");
                    loadScouts(); // Refresh the list
                    loadStatistics(); // Refresh statistics
                } else {
                    throw new Error(result.error);
                }
            } catch (err) {
                console.error("Error adding scout:", err);
                showMessage("Failed to add scout: " + err.message, "#f59e0b");
            }
        });

        // Edit scout form
        editScoutForm.addEventListener("submit", async function(e) {
            e.preventDefault();

            const formData = new FormData(editScoutForm);
            const scoutId = formData.get("scoutId");
            const scoutData = {
                name: formData.get("name"),
                region: formData.get("region"),
                contactInfo: formData.get("contactInfo"),
                experienceLevel: formData.get("experienceLevel"),
                statusId: parseInt(formData.get("statusId")),
                assignedClubId: formData.get("assignedClubId") ? parseInt(formData.get("assignedClubId")) : null,
                players_found: parseInt(formData.get("playersFound")) || 0,
                success_rate: parseInt(formData.get("successRate")) || 0
            };

            try {
                const response = await fetch(`${API_URL}/scouts/${scoutId}`, {
                    method: "PUT",
                    headers: { 
                        "Content-Type": "application/json" 
                    },
                    body: JSON.stringify(scoutData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    editScoutModal.style.display = "none";
                    showMessage("Scout updated successfully");
                    loadScouts(); // Refresh the list
                    loadStatistics(); // Refresh statistics
                } else {
                    throw new Error(result.error);
                }
            } catch (err) {
                console.error("Error updating scout:", err);
                showMessage("Failed to update scout: " + err.message, "#f59e0b");
            }
        });

        // Update stats form
        updateStatsForm.addEventListener("submit", async function(e) {
            e.preventDefault();

            const formData = new FormData(updateStatsForm);
            const scoutId = formData.get("scoutId");
            const statsData = {
                players_found: parseInt(formData.get("playersFound")) || 0,
                success_rate: parseInt(formData.get("successRate")) || 0
            };

            try {
                const response = await fetch(`${API_URL}/scouts/${scoutId}/stats`, {
                    method: "PUT",
                    headers: { 
                        "Content-Type": "application/json" 
                    },
                    body: JSON.stringify(statsData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    updateStatsModal.style.display = "none";
                    showMessage("Scout performance updated successfully");
                    loadScouts(); // Refresh the list
                    loadStatistics(); // Refresh statistics
                } else {
                    throw new Error(result.error);
                }
            } catch (err) {
                console.error("Error updating scout stats:", err);
                showMessage("Failed to update scout performance: " + err.message, "#f59e0b");
            }
        });

        // Initial load
        loadScouts();
        loadStatistics();
        loadStatuses();
        loadClubs();

        // Sidebar toggle
        const sidebar = document.querySelector('.sidebar');
        document.querySelector('.sidebar-toggle').addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });

        // Light/Dark mode toggle
        const themeBtn = document.querySelector('.theme-toggle');
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark');
            if (document.body.classList.contains('dark')) {
                themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
            }
        });
    </script>
</body>
</html>  hold this and hook it up to the crud operations in this from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import os
from pymongo.mongo_client import MongoClient
from pymongo import ASCENDING, DESCENDING
import certifi
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow all origins (adjust for production)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# -----------------------
# CONFIG
# -----------------------
MONGO_URI = os.getenv("MONGO_URI")  # Set in Render secrets
DB_NAME = "Players"

# -----------------------
# CONNECT TO MONGO
# -----------------------
try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]

    # Collections
    players_collection = db["Players"]
    scouts_collection = db["Scouts"]
    clubs_collection = db["Clubs"]

    # Safely create indexes for players
    def ensure_index(collection, field, direction=ASCENDING):
        try:
            collection.create_index([(field, direction)])
        except Exception as e:
            # Ignore if index exists with different name
            if "IndexOptionsConflict" in str(e):
                print(f"⚠️ Index on '{field}' already exists, skipping.")
            else:
                raise e

    ensure_index(players_collection, "name")
    ensure_index(players_collection, "position")
    ensure_index(players_collection, "rating", DESCENDING)

    ensure_index(scouts_collection, "name")
    ensure_index(clubs_collection, "name")

    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise e

# -----------------------
# UTIL FUNCTIONS
# -----------------------
def generate_age():
    return random.randint(16, 40)  # footballer age

def generate_height():
    return random.randint(160, 200)  # cm

def generate_weight():
    return random.randint(55, 95)  # kg

def generate_experience():
    return random.randint(1, 25)  # scout years of experience

def generate_capacity():
    return random.randint(5000, 90000)  # stadium capacity

def generate_founded_year():
    return random.randint(1850, 2020)  # club foundation year

def transform_player(p):
    """Efficient player transformation function"""
    # --- Age ---
    age = p.get("age")
    if not age and p.get("Date"):
        try:
            year = int(str(p["Date"]).split("-")[0])
            age = datetime.now().year - year
        except Exception:
            age = generate_age()
    elif not age:
        age = generate_age()

    # --- Height & Weight ---
    height = p.get("height") or generate_height()
    weight = p.get("weight") or generate_weight()

    # --- Position ---
    position = p.get("position", "N/A")

    # --- Rating ---
    rating = (
        p.get("rating") or
        p.get("Rating") or
        p.get("Original Rating") or
        p.get("Alternative Rating")
    )
    try:
        rating = float(rating) if rating else 0
    except (TypeError, ValueError):
        rating = 0  # Default to 0 for frontend

    # --- Club & Nationality ---
    club = p.get("club") or p.get("Team Name") or "N/A"
    nationality = p.get("nationality", "N/A")
    notes = p.get("notes", "")

    return {
        "name": p.get("name", "N/A"),
        "age": age,
        "height": height,
        "weight": weight,
        "position": position,
        "rating": rating,
        "club": club,
        "nationality": nationality,
        "notes": notes
    }

# -----------------------
# FLASK ROUTES
# -----------------------
@app.route("/")
def home():
    return "⚽ Players, Scouts & Clubs Flask App is running!"

# ==================================================
# PLAYERS ROUTES (OPTIMIZED)
# ==================================================
@app.route("/players", methods=["GET"])
@cache.cached(timeout=60, query_string=True)  # Cache for 60 seconds
def get_players():
    # Get query parameters with defaults
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    name_filter = request.args.get("name")
    position_filter = request.args.get("position")
    
    # Calculate skip value for pagination
    skip = (page - 1) * per_page

    # Build query
    query = {}
    if name_filter:
        query["name"] = {"$regex": name_filter, "$options": "i"}
    if position_filter:
        query["position"] = position_filter

    try:
        # Get total count for pagination info
        total_players = players_collection.count_documents(query)
        
        # Fetch only the required page of players
        raw_players_cursor = players_collection.find(query, {"_id": 0}).skip(skip).limit(per_page)
        
        # Use list comprehension for faster transformation
        players = [transform_player(p) for p in raw_players_cursor]

        return jsonify({
            "total_players": total_players,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_players + per_page - 1) // per_page,
            "players": players
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/players/<player_name>", methods=["GET"])
@cache.cached(timeout=300)  # Cache individual player for 5 minutes
def get_player(player_name):
    player = players_collection.find_one({"name": player_name}, {"_id": 0})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    
    transformed_player = transform_player(player)
    return jsonify(transformed_player)

@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    if not data.get("name") or not data.get("position"):
        return jsonify({"error": "Name and position are required"}), 400
    if players_collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Player with this name already exists"}), 400

    # Auto-generate if missing
    data.setdefault("age", generate_age())
    data.setdefault("height", generate_height())
    data.setdefault("weight", generate_weight())

    players_collection.insert_one(data)
    
    # Clear cache for players list
    cache.delete_memoized(get_players)
    return jsonify({"message": "Player added successfully"}), 201

@app.route("/players/<player_name>", methods=["PUT"])
def update_player(player_name):
    data = request.json
    player = players_collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_collection.update_one({"name": player_name}, {"$set": data})
    
    # Clear relevant caches
    cache.delete_memoized(get_players)
    cache.delete_memoized(get_player, player_name)
    return jsonify({"message": "Player updated successfully"})

@app.route("/players/<player_name>", methods=["DELETE"])
def delete_player(player_name):
    player = players_collection.find_one({"name": player_name})
    if not player:
        return jsonify({"error": "Player not found"}), 404
    players_collection.delete_one({"name": player_name})
    
    # Clear relevant caches
    cache.delete_memoized(get_players)
    cache.delete_memoized(get_player, player_name)
    return jsonify({"message": f"{player_name} deleted successfully"})

@app.route("/player-reports", methods=["GET"])
@cache.cached(timeout=300)  # Cache reports for 5 minutes
def player_reports():
    # Use aggregation for faster processing
    pipeline = [
        {"$group": {
            "_id": "$position",
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$project": {
            "position": "$_id",
            "count": 1,
            "avg_rating": {"$round": ["$avg_rating", 1]},
            "_id": 0
        }}
    ]
    
    positions_stats = list(players_collection.aggregate(pipeline))
    
    # Get top 10 players by rating
    top_players = list(players_collection.find(
        {}, 
        {"_id": 0, "name": 1, "position": 1, "rating": 1}
    ).sort("rating", -1).limit(10))
    
    # Ensure ratings are numbers
    for p in top_players:
        if "rating" not in p:
            p["rating"] = round(5 + 5 * random.random(), 1)
        elif isinstance(p["rating"], str):
            try:
                p["rating"] = float(p["rating"])
            except ValueError:
                p["rating"] = round(5 + 5 * random.random(), 1)

    return jsonify({
        "positions_stats": positions_stats,
        "top_players": top_players
    })

# ==================================================
# SCOUTS ROUTES
# ==================================================
@app.route("/scouts", methods=["GET"])
@cache.cached(timeout=300)
def get_scouts():
    scouts = list(scouts_collection.find({}, {"_id": 0}))
    for s in scouts:
        s["experience"] = s.get("experience", generate_experience())
    return jsonify(scouts)

@app.route("/scouts/<scout_name>", methods=["GET"])
@cache.cached(timeout=300)
def get_scout(scout_name):
    scout = scouts_collection.find_one({"name": scout_name}, {"_id": 0})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scout["experience"] = scout.get("experience", generate_experience())
    return jsonify(scout)

@app.route("/scouts", methods=["POST"])
def add_scout():
    data = request.json
    if not data.get("name") or not data.get("region"):
        return jsonify({"error": "Scout name and region are required"}), 400
    if scouts_collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Scout with this name already exists"}), 400

    data.setdefault("experience", generate_experience())
    scouts_collection.insert_one(data)
    
    # Clear scouts cache
    cache.delete_memoized(get_scouts)
    return jsonify({"message": "Scout added successfully"}), 201

@app.route("/scouts/<scout_name>", methods=["PUT"])
def update_scout(scout_name):
    data = request.json
    scout = scouts_collection.find_one({"name": scout_name})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_collection.update_one({"name": scout_name}, {"$set": data})
    
    # Clear relevant caches
    cache.delete_memoized(get_scouts)
    cache.delete_memoized(get_scout, scout_name)
    return jsonify({"message": "Scout updated successfully"})

@app.route("/scouts/<scout_name>", methods=["DELETE"])
def delete_scout(scout_name):
    scout = scouts_collection.find_one({"name": scout_name})
    if not scout:
        return jsonify({"error": "Scout not found"}), 404
    scouts_collection.delete_one({"name": scout_name})
    
    # Clear relevant caches
    cache.delete_memoized(get_scouts)
    cache.delete_memoized(get_scout, scout_name)
    return jsonify({"message": f"{scout_name} deleted successfully"})

# ==================================================
# CLUBS ROUTES
# ==================================================
@app.route("/clubs", methods=["GET"])
@cache.cached(timeout=300)
def get_clubs():
    clubs = list(clubs_collection.find({}, {"_id": 0}))
    for c in clubs:
        c["capacity"] = c.get("capacity", generate_capacity())
        c["founded"] = c.get("founded", generate_founded_year())
    return jsonify(clubs)

@app.route("/clubs/<club_name>", methods=["GET"])
@cache.cached(timeout=300)
def get_club(club_name):
    club = clubs_collection.find_one({"name": club_name}, {"_id": 0})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    club["capacity"] = club.get("capacity", generate_capacity())
    club["founded"] = club.get("founded", generate_founded_year())
    return jsonify(club)

@app.route("/clubs", methods=["POST"])
def add_club():
    data = request.json
    if not data.get("name") or not data.get("league"):
        return jsonify({"error": "Club name and league are required"}), 400
    if clubs_collection.find_one({"name": data["name"]}):
        return jsonify({"error": "Club with this name already exists"}), 400

    data.setdefault("capacity", generate_capacity())
    data.setdefault("founded", generate_founded_year())

    clubs_collection.insert_one(data)
    
    # Clear clubs cache
    cache.delete_memoized(get_clubs)
    return jsonify({"message": "Club added successfully"}), 201

@app.route("/clubs/<club_name>", methods=["PUT"])
def update_club(club_name):
    data = request.json
    club = clubs_collection.find_one({"name": club_name})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    clubs_collection.update_one({"name": club_name}, {"$set": data})
    
    # Clear relevant caches
    cache.delete_memoized(get_clubs)
    cache.delete_memoized(get_club, club_name)
    return jsonify({"message": "Club updated successfully"})

@app.route("/clubs/<club_name>", methods=["DELETE"])
def delete_club(club_name):
    club = clubs_collection.find_one({"name": club_name})
    if not club:
        return jsonify({"error": "Club not found"}), 404
    clubs_collection.delete_one({"name": club_name})
    
    # Clear relevant caches
    cache.delete_memoized(get_clubs)
    cache.delete_memoized(get_club, club_name)
    return jsonify({"message": f"{club_name} deleted successfully"})

# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
