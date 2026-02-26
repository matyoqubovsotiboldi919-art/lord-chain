(() => {
  const API = window.API_BASE || "";

  const authWrapper = document.getElementById("authWrapper");

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

  const toast = document.getElementById("toast");

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

  async function postJson(url, payload) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
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

  function saveToken(token) {
    localStorage.setItem("token", token);
  }

  function afterAuth() {
    // Sizda dashboard qaysi sahifa bo‘lsa keyin moslaymiz.
    // Hozircha eng xavfsiz: reload.
    window.location.reload();
  }

  // Switch buttons
  registerBtn?.addEventListener("click", () => setPanel("register"));
  loginBtn?.addEventListener("click", () => setPanel("login"));
  mobileRegisterBtn?.addEventListener("click", () => setPanel("register"));
  mobileLoginBtn?.addEventListener("click", () => setPanel("login"));

  // Register
  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (regEmail?.value || "").trim();
    const password = regPassword?.value || "";

    if (!email || !password) return showToast("Email and password are required", "error");

    setBusy(regSubmitBtn, true);
    try {
      const r = await postJson(`${API}/api/v1/auth/register`, { email, password });

      if (r.ok) {
        const token = extractToken(r.data);
        if (token) {
          saveToken(token);
          showToast("Registered successfully!", "success");
          afterAuth();
          return;
        }
        showToast("Registered. Now sign in.", "success");
        setPanel("login");
        return;
      }

      showToast(getErrorMessage(r.data), "error");
    } catch (err) {
      showToast(String(err?.message || err), "error");
    } finally {
      setBusy(regSubmitBtn, false);
    }
  });

  // Login
  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (loginEmail?.value || "").trim();
    const password = loginPassword?.value || "";

    if (!email || !password) return showToast("Email and password are required", "error");

    setBusy(loginSubmitBtn, true);
    try {
      const r = await postJson(`${API}/api/v1/auth/login`, { email, password });

      if (r.ok) {
        const token = extractToken(r.data);
        if (token) {
          saveToken(token);
          showToast("Login successful!", "success");
          afterAuth();
          return;
        }
        showToast("Login successful.", "success");
        afterAuth();
        return;
      }

      showToast(getErrorMessage(r.data), "error");
    } catch (err) {
      showToast(String(err?.message || err), "error");
    } finally {
      setBusy(loginSubmitBtn, false);
    }
  });

  setPanel("login");
})();