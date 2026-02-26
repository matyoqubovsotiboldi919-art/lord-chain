const API = window.API_BASE || "";

// ---------- helpers ----------
function qs(id) { return document.getElementById(id); }

function setMsg(id, text, type = "info") {
  const el = qs(id);
  if (!el) return;
  el.className = `msg ${type}`;
  el.textContent = text || "";
}

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

async function apiFetch(path, { method = "GET", body = null, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null
  });

  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    try { data = await res.json(); } catch { data = null; }
  } else {
    try { data = await res.text(); } catch { data = null; }
  }

  return { res, data };
}

// ---------- UI actions ----------
async function doRegister() {
  setMsg("reg-msg", "");
  const email = (qs("reg-email")?.value || "").trim();
  const password = qs("reg-password")?.value || "";

  if (!email || !password) {
    setMsg("reg-msg", "Email va password kiriting.", "err");
    return;
  }

  const { res, data } = await apiFetch("/api/v1/auth/register", {
    method: "POST",
    body: { email, password }
  });

  if (res.ok) {
    setMsg("reg-msg", "Registered ✅ Endi login qiling.", "ok");
  } else {
    const msg = (data && data.detail) ? data.detail : "Registration failed";
    setMsg("reg-msg", msg, "err");
  }
}

async function doLogin() {
  setMsg("login-msg", "");
  const email = (qs("login-email")?.value || "").trim();
  const password = qs("login-password")?.value || "";

  if (!email || !password) {
    setMsg("login-msg", "Email va password kiriting.", "err");
    return;
  }

  const { res, data } = await apiFetch("/api/v1/auth/login", {
    method: "POST",
    body: { email, password }
  });

  if (res.ok && data && data.access_token) {
    setToken(data.access_token);
    setMsg("login-msg", "Login ✅", "ok");
    await loadMe();
  } else {
    const msg = (data && data.detail) ? data.detail : "Login failed";
    setMsg("login-msg", msg, "err");
  }
}

async function loadMe() {
  const dash = qs("dashboard");
  const btnLogout = qs("btn-logout");

  const token = getToken();
  if (!token) {
    if (btnLogout) btnLogout.classList.add("hidden");
    if (dash) dash.innerHTML = `<div class="muted">Not logged in.</div>`;
    return;
  }

  // ✅ MUHIM: auth=true bo‘lgani uchun Authorization: Bearer <token> yuboriladi
  const { res, data } = await apiFetch("/api/v1/users/me", { auth: true });

  if (!res.ok) {
    // token noto‘g‘ri/eskirgan bo‘lsa
    clearToken();
    if (btnLogout) btnLogout.classList.add("hidden");

    const msg = (data && data.detail) ? data.detail : "Unauthorized (401)";
    if (dash) dash.innerHTML = `<div class="msg err">${msg}</div>`;
    return;
  }

  if (btnLogout) btnLogout.classList.remove("hidden");

  const email = data?.email ?? "-";
  const balance = data?.balance ?? "-";

  if (dash) {
    dash.innerHTML = `
      <div class="row"><span class="k">Email</span><span class="v">${email}</span></div>
      <div class="row"><span class="k">Balance</span><span class="v">${balance}</span></div>
      <div class="hint muted">Agar avval 401 bo‘lgan bo‘lsa, endi ketishi kerak.</div>
    `;
  }
}

function doLogout() {
  clearToken();
  setMsg("login-msg", "Logout ✅", "ok");
  loadMe();
}

// ---------- wire up ----------
window.addEventListener("DOMContentLoaded", () => {
  qs("btn-register")?.addEventListener("click", doRegister);
  qs("btn-login")?.addEventListener("click", doLogin);
  qs("btn-logout")?.addEventListener("click", doLogout);

  // auto load profile if token exists
  loadMe();
});