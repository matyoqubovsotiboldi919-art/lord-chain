const API = window.API_BASE || "";

async function register() {
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    const res = await fetch(`${API}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
        alert("Registered successfully!");
    } else {
        alert(data.detail || "Registration failed");
    }
}

async function login() {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const res = await fetch(`${API}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
        localStorage.setItem("token", data.access_token);
        showDashboard(data.access_token);
    } else {
        alert(data.detail || "Login failed");
    }
}

function showDashboard(token) {
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("dashboard").style.display = "block";
    document.getElementById("token-display").innerText = token;
}

function logout() {
    localStorage.removeItem("token");
    location.reload();
}

window.onload = function () {
    const token = localStorage.getItem("token");
    if (token) {
        showDashboard(token);
    }
};