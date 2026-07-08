// ================= LOGIN =================
async function loginUser() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            alert("Invalid username or password ❌");
        }

    } catch (err) {
        alert("Server error ❌");
    }
}

// ================= LOGOUT =================
function logout() {
    window.location.href = "/logout";
}

// ================= TOGGLE PASSWORD =================
function togglePassword() {
    const pass = document.getElementById("password");
    pass.type = pass.type === "password" ? "text" : "password";
}

// ================= SCAN FUNCTION =================
function scan() {

    let input = document.getElementById("inputText").value;

    if (!input) {
        alert("Enter URL first!");
        return;
    }

    fetch('/api/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({input: input, type: 'url'})
    })
    .then(res => res.json())
    .then(data => {

        console.log("SCAN RESULT:", data);

        let score = Math.round(data.risk_score || 0);

        drawSpeedometer(0);

        let current = 0;

        let interval = setInterval(() => {

            if (current >= score) {
                clearInterval(interval);

                let status = document.getElementById("statusText");

                if (score <= 30) {
                    status.innerHTML = "🟢 Legitimate (" + score + "%)";
                    status.className = "green";
                } 
                else if (score <= 70) {
                    status.innerHTML = "🟡 Suspicious (" + score + "%)";
                    status.className = "yellow";
                } 
                else {
                    status.innerHTML = "🔴 Phishing (" + score + "%)";
                    status.className = "red";
                }

            } else {
                current++;
                drawSpeedometer(current);
            }

        }, 20);

    })
    .catch(err => {
        console.log(err);
        alert("Scan failed 😨");
    });
}


// ================= ADMIN: LOAD USERS =================
async function loadUsers() {
    try {
        const res = await fetch('/api/users');
        const data = await res.json();

        const container = document.getElementById("users");
        if (!container) return;

        container.innerHTML = "";

        data.forEach(user => {
            container.innerHTML += `
                <div class="card">
                    <h3>${user.username}</h3>
                    <p>Role: ${user.role}</p>
                </div>
            `;
        });

    } catch (err) {
        console.log("Error loading users");
    }
}


// ================= ADMIN: LOAD SCANS =================
async function loadScans() {
    try {
        const res = await fetch('/api/scans');
        const data = await res.json();

        const container = document.getElementById("scans");
        if (!container) return;

        container.innerHTML = "";

        data.forEach(scan => {
            container.innerHTML += `
                <div class="card">
                    <p><b>Input:</b> ${scan.input}</p>
                    <p><b>Type:</b> ${scan.type}</p>
                    <p><b>Risk:</b> ${scan.risk_score}%</p>
                    <p>${scan.time}</p>
                </div>
            `;
        });

    } catch (err) {
        console.log("Error loading scans");
    }
}


// ================= AUTO LOAD =================
window.onload = function () {
    loadUsers();
    loadScans();
};


// 🔥 SIDEBAR
function toggleMenu() {
    let sidebar = document.getElementById("sidebar");
    sidebar.style.left = sidebar.style.left === "0px" ? "-200px" : "0px";
}


// 🔥 SECTION SWITCH
function showSection(section) {
    document.querySelectorAll(".section").forEach(sec => sec.classList.remove("active"));
    document.getElementById(section).classList.add("active");
}


// 🔥 GAUGE
function drawSpeedometer(score) {
    const needle = document.getElementById("needle");
    const scoreText = document.getElementById("score");

    if (!needle) return;

    let degree = (score / 100) * 180;

    needle.style.transform = `rotate(${degree}deg)`;

    if (scoreText) {
        scoreText.innerText = score + "%";
    }
}