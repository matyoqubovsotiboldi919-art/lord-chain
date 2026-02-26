// backend/frontend/app.js
(() => {
  const API = window.API_BASE || "";

  // ===== DOM =====
  const topbar = document.getElementById("topbar");
  const app = document.getElementById("app");
  const authWrapper = document.getElementById("authWrapper");
  const toast = document.getElementById("toast");

  const meEmail = document.getElementById("meEmail");
  const logoutBtn = document.getElementById("logoutBtn");

  const registerBtn = document.getElementById("registerBtn");
  const loginBtn = document.getElementById("loginBtn");
  const mobileRegisterBtn = document.getElementById("mobileRegisterBtn");
  const mobileLoginBtn = document.getElementById("mobileLoginBtn");

  const registerForm = document.getElementById("registerForm");
  const loginForm = document.getElementById("loginForm");

  const regEmail = document.getElementById("reg-email");
  const regPassword = document.getElementById("reg-password");
  const regSubmitBtn = document.getElementById("regSubmitBtn");

  const loginEmail = document.getElementById("login-email");
  const loginPassword = document.getElementById("login-password");
  const loginSubmitBtn = document.getElementById("loginSubmitBtn");

  // views
  const views = {
    dashboard: document.getElementById("view-dashboard"),
    tx: document.getElementById("view-tx"),
    explorer: document.getElementById("view-explorer"),
    admin: document.getElementById("view-admin"),
  };

  // dashboard widgets
  const balanceBox = document.getElementById("balanceBox");
  const addressBox = document.getElementById("addressBox");
  const loadBalanceBtn = document.getElementById("loadBalanceBtn");
  const loadMeBtn = document.getElementById("loadMeBtn");

  // tx widgets
  const txTo = document.getElementById("tx-to");
  const txAmount = document.getElementById("tx-amount");
  const sendTxBtn = document.getElementById("sendTxBtn");
  const loadTxBtn = document.getElementById("loadTxBtn");
  const txList = document.getElementById("txList");

  // explorer widgets
  const q = document.getElementById("q");
  const searchBtn = document.getElementById("searchBtn");
  const explorerOut = document.getElementById("explorerOut");

  // admin widgets
  const loadAdminBtn = document.getElementById("loadAdminBtn");
  const adminOut = document.getElementById("adminOut");

  // ===== Helpers =====
  function token() {
    return localStorage.getItem("token") || "";
  }

  function setPanel(panel) {
    if (!authWrapper) return;
    if (panel === "register") authWrapper.classList.add("panel-active");
    else authWrapper.classList.remove("panel-active");
  }

  function showToast(message, type = "info") {
    if (!toast) return alert(message);
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => { toast.className = "toast"; }, 3500);
  }

  function setBusy(btn, busy) {
    if (!btn) return;
    btn.disabled = !!busy;
    if (!btn.dataset._old) btn.dataset._old = btn.textContent;
    btn.textContent = busy ? "Please wait..." : btn.dataset._old;
  }

  async function request(method, url, body) {
    const headers = { "Content-Type": "application/json" };
    const t = token();
    if (t) headers["Authorization"] = `Bearer ${t}`;

    const res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    const raw = await res.text();
    let data = null;
    try { data = raw ? JSON.parse(raw) : null; }
    catch { data = { detail: raw }; }

    return { ok: res.ok, status: res.status, data };
  }

  function extractToken(data) {
    if (!data || typeof data !== "object") return null;
    return data.access_token || data.token || null;
  }

  function getErrorMessage(data) {
    if (!data) return "Request failed";
    if (typeof data === "string") return data;
    if (data.detail) {
      if (Array.isArray(data.detail)) return data.detail.map(x => x?.msg || "Invalid input").join(", ");
      return data.detail;
    }
    if (data.message) return data.message;
    return "Request failed";
  }

  function showAuth() {
    topbar.style.display = "none";
    app.style.display = "none";
    authWrapper.style.display = "block";
    setPanel("login");
  }

  function showApp() {
    authWrapper.style.display = "none";
    topbar.style.display = "flex";
    app.style.display = "block";
    switchView("dashboard");
  }

  function switchView(name) {
    Object.entries(views).forEach(([k, el]) => {
      if (!el) return;
      el.classList.toggle("active", k === name);
    });

    document.querySelectorAll(".nav-btn[data-view]").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.view === name);
    });
  }

  // ===== Nav events =====
  document.querySelectorAll(".nav-btn[data-view]").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });

  logoutBtn?.addEventListener("click", () => {
    localStorage.removeItem("token");
    showToast("Logged out", "info");
    showAuth();
  });

  // ===== Auth events =====
  registerBtn?.addEventListener("click", () => setPanel("register"));
  loginBtn?.addEventListener("click", () => setPanel("login"));
  mobileRegisterBtn?.addEventListener("click", () => setPanel("register"));
  mobileLoginBtn?.addEventListener("click", () => setPanel("login"));

  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (regEmail?.value || "").trim();
    const password = regPassword?.value || "";
    if (!email || !password) return showToast("Email and password are required", "error");

    setBusy(regSubmitBtn, true);
    try {
      const r = await request("POST", `${API}/api/v1/auth/register`, { email, password });
      if (!r.ok) return showToast(getErrorMessage(r.data), "error");

      const t = extractToken(r.data);
      if (t) {
        localStorage.setItem("token", t);
        meEmail.textContent = email;
        showToast("Registered & logged in", "success");
        return showApp();
      }

      // token bo'lmasa: shunchaki login qilsin
      showToast("Registered. Please sign in.", "success");
      setPanel("login");
    } catch (err) {
      showToast(String(err?.message || err), "error");
    } finally {
      setBusy(regSubmitBtn, false);
    }
  });

  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (loginEmail?.value || "").trim();
    const password = loginPassword?.value || "";
    if (!email || !password) return showToast("Email and password are required", "error");

    setBusy(loginSubmitBtn, true);
    try {
      const r = await request("POST", `${API}/api/v1/auth/login`, { email, password });
      if (!r.ok) return showToast(getErrorMessage(r.data), "error");

      const t = extractToken(r.data);
      if (!t) return showToast("Login ok, but token not returned by backend", "error");

      localStorage.setItem("token", t);
      meEmail.textContent = email;
      showToast("Login successful", "success");
      showApp();
    } catch (err) {
      showToast(String(err?.message || err), "error");
    } finally {
      setBusy(loginSubmitBtn, false);
    }
  });

  // ===== App actions (safe calls) =====
  loadMeBtn?.addEventListener("click", async () => {
    setBusy(loadMeBtn, true);
    try {
      // If you have /me or profile endpoint, add it here later.
      // For now we only show: token exists
      addressBox.textContent = "(profile endpoint not wired yet)";
      showToast("Profile loaded (placeholder)", "info");
    } finally {
      setBusy(loadMeBtn, false);
    }
  });

  loadBalanceBtn?.addEventListener("click", async () => {
    setBusy(loadBalanceBtn, true);
    try {
      // If you have /balance endpoint, wire it here later without breaking UI.
      balanceBox.textContent = "(balance endpoint not wired yet)";
      showToast("Balance loaded (placeholder)", "info");
    } finally {
      setBusy(loadBalanceBtn, false);
    }
  });

  sendTxBtn?.addEventListener("click", async () => {
    const to = (txTo?.value || "").trim();
    const amount = (txAmount?.value || "").trim();
    if (!to || !amount) return showToast("To address and amount required", "error");

    setBusy(sendTxBtn, true);
    try {
      // Attempt common tx endpoint (won't break if missing)
      const r = await request("POST", `${API}/api/v1/tx/send`, { to_address: to, amount });
      if (!r.ok) return showToast(getErrorMessage(r.data), "error");
      showToast("Transaction sent", "success");
      txList.textContent = JSON.stringify(r.data, null, 2);
    } catch (err) {
      showToast("Tx endpoint not available or failed", "error");
    } finally {
      setBusy(sendTxBtn, false);
    }
  });

  loadTxBtn?.addEventListener("click", async () => {
    setBusy(loadTxBtn, true);
    try {
      const r = await request("GET", `${API}/api/v1/tx/history`);
      if (!r.ok) return showToast(getErrorMessage(r.data), "error");
      txList.textContent = JSON.stringify(r.data, null, 2);
      showToast("History loaded", "success");
    } catch {
      showToast("History endpoint not available", "error");
    } finally {
      setBusy(loadTxBtn, false);
    }
  });

  searchBtn?.addEventListener("click", async () => {
    const query = (q?.value || "").trim();
    if (!query) return showToast("Enter address or tx hash", "error");

    setBusy(searchBtn, true);
    try {
      const r = await request("GET", `${API}/api/v1/explorer/search?q=${encodeURIComponent(query)}`);
      if (!r.ok) return showToast(getErrorMessage(r.data), "error");
      explorerOut.textContent = JSON.stringify(r.data, null, 2);
      showToast("Search done", "success");
    } catch {
      showToast("Explorer endpoint not available", "error");
    } finally {
      setBusy(searchBtn, false);
    }
  });

  loadAdminBtn?.addEventListener("click", async () => {
    setBusy(loadAdminBtn, true);
    try {
      const r = await request("GET", `${API}/api/v1/admin/status`);
      if (!r.ok) return showToast(getErrorMessage(r.data), "error");
      adminOut.textContent = JSON.stringify(r.data, null, 2);
      showToast("Admin loaded", "success");
    } catch {
      showToast("Admin endpoint not available", "error");
    } finally {
      setBusy(loadAdminBtn, false);
    }
  });

  // ===== Boot =====
  if (token()) {
    meEmail.textContent = "logged-in";
    showApp();
  } else {
    showAuth();
  }
})();