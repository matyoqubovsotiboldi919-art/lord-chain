console.log("LORD UI BUILD 20260227c");

(() => {
  const API = window.API_BASE || "";

  // ===== Elements =====
  const toast = document.getElementById("toast");

  const authRoot = document.getElementById("authRoot");
  const appRoot  = document.getElementById("appRoot");

  const tabLogin = document.getElementById("tabLogin");
  const tabRegister = document.getElementById("tabRegister");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  const loginEmail = document.getElementById("loginEmail");
  const loginPassword = document.getElementById("loginPassword");
  const regEmail = document.getElementById("regEmail");
  const regPassword = document.getElementById("regPassword");

  const loginBtn = document.getElementById("loginBtn");
  const regBtn = document.getElementById("regBtn");

  const meEmail = document.getElementById("meEmail");
  const meEmail2 = document.getElementById("meEmail2");
  const meAddress = document.getElementById("meAddress");
  const meBalance = document.getElementById("meBalance");

  const logoutBtn = document.getElementById("logoutBtn");
  const refreshBtn = document.getElementById("refreshBtn");
  const pageTitle = document.getElementById("pageTitle");
  const menuBtn = document.getElementById("menuBtn");
  const sidebar = document.querySelector(".sidebar");

  const loadMeBtn = document.getElementById("loadMeBtn");
  const verifyChainBtn = document.getElementById("verifyChainBtn");
  const chainVerifyOut = document.getElementById("chainVerifyOut");
  const chainStatusChip = document.getElementById("chainStatusChip");

  const txTo = document.getElementById("txTo");
  const txAmount = document.getElementById("txAmount");
  const createTxBtn = document.getElementById("createTxBtn");
  const loadHistoryBtn = document.getElementById("loadHistoryBtn");
  const historyBody = document.getElementById("historyBody");

  const expTxHash = document.getElementById("expTxHash");
  const expAddr = document.getElementById("expAddr");
  const expTxBtn = document.getElementById("expTxBtn");
  const expAddrBtn = document.getElementById("expAddrBtn");
  const explorerOut = document.getElementById("explorerOut");

  const adminPassword = document.getElementById("adminPassword");
  const adminLoginBtn = document.getElementById("adminLoginBtn");
  const adminTokenHint = document.getElementById("adminTokenHint");
  const freezeEmail = document.getElementById("freezeEmail");
  const freezeBtn = document.getElementById("freezeBtn");
  const unfreezeBtn = document.getElementById("unfreezeBtn");
  const loadAuditBtn = document.getElementById("loadAuditBtn");
  const auditBody = document.getElementById("auditBody");
  const adminOut = document.getElementById("adminOut");

  const viewMap = {
    dashboard: document.getElementById("view-dashboard"),
    transactions: document.getElementById("view-transactions"),
    explorer: document.getElementById("view-explorer"),
    admin: document.getElementById("view-admin"),
  };

  let adminToken = "";

  // ===== Helpers =====
  function showToast(msg, type="inf") {
    if (!toast) return;
    toast.textContent = msg;
    toast.className = `toast show ${type}`;
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => { toast.className = "toast"; }, 3200);
  }

  function setBusy(btn, busy) {
    if (!btn) return;
    btn.disabled = !!busy;
    if (!btn.dataset.old) btn.dataset.old = btn.textContent;
    btn.textContent = busy ? "Please wait..." : btn.dataset.old;
  }

  function getToken() { return localStorage.getItem("token") || ""; }
  function setToken(t) { localStorage.setItem("token", t); }
  function clearToken() { localStorage.removeItem("token"); }

  async function http(method, path, body, extraHeaders = {}) {
    const headers = { "Content-Type": "application/json", ...extraHeaders };
    const t = getToken();
    if (t) headers["Authorization"] = `Bearer ${t}`;

    const res = await fetch(`${API}${path}`, {
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

  function errMsg(r) {
    const d = r?.data;
    if (!d) return `Error (${r?.status || "?"})`;
    if (typeof d === "string") return d;
    if (d.detail) {
      if (Array.isArray(d.detail)) return d.detail.map(x => x?.msg || "Invalid").join(", ");
      return d.detail;
    }
    return `Error (${r?.status || "?"})`;
  }

  function switchAuth(tab) {
    const isLogin = tab === "login";
    tabLogin?.classList.toggle("active", isLogin);
    tabRegister?.classList.toggle("active", !isLogin);
    loginForm?.classList.toggle("hidden", !isLogin);
    registerForm?.classList.toggle("hidden", isLogin);
  }

  function showAuth() {
    authRoot?.classList.remove("hidden");
    appRoot?.classList.add("hidden");
    switchAuth("login");
  }

  function showApp() {
    authRoot?.classList.add("hidden");
    appRoot?.classList.remove("hidden");
    switchView("dashboard");
  }

  function switchView(name) {
    Object.entries(viewMap).forEach(([k, el]) => el?.classList.toggle("hidden", k !== name));
    document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.view === name));
    if (pageTitle) pageTitle.textContent = name[0].toUpperCase() + name.slice(1);
    sidebar?.classList.remove("open");
  }

  function setMe(u) {
    const email = u?.email || "—";
    if (meEmail) meEmail.textContent = email;
    if (meEmail2) meEmail2.textContent = email;
    if (meAddress) meAddress.textContent = u?.address || "—";
    if (meBalance) meBalance.textContent = (u?.balance ?? "—");
  }

  async function loadMe() {
    const r = await http("GET", "/api/v1/users/me");
    if (!r.ok) throw new Error(errMsg(r));
    setMe(r.data);
    return r.data;
  }

  async function verifyChain() {
    const r = await http("GET", "/api/v1/explorer/verify-chain");
    if (!r.ok) throw new Error(errMsg(r));
    const ok = (typeof r.data === "object") ? (r.data.ok ?? r.data.valid ?? null) : null;
    const text = ok === true ? "VALID ✅" : ok === false ? "INVALID ❌" : "OK ✅";
    if (chainVerifyOut) chainVerifyOut.textContent = text;
    if (chainStatusChip) chainStatusChip.textContent = `Chain: ${text.replace(/\s/g, "")}`;
    return r.data;
  }

  function renderHistory(rows) {
    if (!historyBody) return;
    if (!rows || !rows.length) {
      historyBody.innerHTML = `<tr><td colspan="5" class="muted">No transactions</td></tr>`;
      return;
    }
    historyBody.innerHTML = rows.map((r, idx) => `
      <tr>
        <td>${idx + 1}</td>
        <td class="mono">${r.from_address ?? "—"}</td>
        <td class="mono">${r.to_address ?? "—"}</td>
        <td class="right">${r.amount ?? "—"}</td>
        <td class="mono">${r.block_hash ?? "—"}</td>
      </tr>
    `).join("");
  }

  function renderAudit(rows) {
    if (!auditBody) return;
    if (!rows || !rows.length) {
      auditBody.innerHTML = `<tr><td colspan="4" class="muted">No logs</td></tr>`;
      return;
    }
    auditBody.innerHTML = rows.map(r => `
      <tr>
        <td class="mono">${(r.created_at || "").slice(0,19).replace("T"," ")}</td>
        <td class="mono">${r.actor ?? "—"}</td>
        <td>${r.action ?? "—"}</td>
        <td class="mono">${r.entity ?? "—"}</td>
      </tr>
    `).join("");
  }

  // ===== Events =====
  tabLogin?.addEventListener("click", () => switchAuth("login"));
  tabRegister?.addEventListener("click", () => switchAuth("register"));

  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    setBusy(loginBtn, true);
    try {
      const payload = {
        email: (loginEmail?.value || "").trim(),
        password: loginPassword?.value || "",
      };
      const r = await http("POST", "/api/v1/auth/login", payload);
      if (!r.ok) throw new Error(errMsg(r));

      const t = r.data?.access_token;
      if (!t) throw new Error("Token not returned");
      setToken(t);

      showToast("Login successful", "ok");

      // validate token immediately
      await loadMe();
      showApp();
      await verifyChain().catch(() => {});
    } catch (err) {
      showToast(String(err.message || err), "err");
    } finally {
      setBusy(loginBtn, false);
    }
  });

  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    setBusy(regBtn, true);
    try {
      const payload = {
        email: (regEmail?.value || "").trim(),
        password: regPassword?.value || "",
      };
      const r = await http("POST", "/api/v1/auth/register", payload);
      if (!r.ok) throw new Error(errMsg(r));

      showToast("Registered. Now sign in.", "ok");
      switchAuth("login");
      if (loginEmail) loginEmail.value = payload.email;
      if (loginPassword) loginPassword.value = payload.password;
    } catch (err) {
      showToast(String(err.message || err), "err");
    } finally {
      setBusy(regBtn, false);
    }
  });

  document.querySelectorAll(".nav-item").forEach(btn =>
    btn.addEventListener("click", () => switchView(btn.dataset.view))
  );

  logoutBtn?.addEventListener("click", () => {
    clearToken();
    adminToken = "";
    if (adminTokenHint) adminTokenHint.textContent = "X-Admin-Token: —";
    showToast("Logged out", "inf");
    showAuth();
  });

  refreshBtn?.addEventListener("click", async () => {
    try {
      await loadMe();
      await verifyChain();
      showToast("Refreshed", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  menuBtn?.addEventListener("click", () => sidebar?.classList.toggle("open"));

  loadMeBtn?.addEventListener("click", async () => {
    setBusy(loadMeBtn, true);
    try { await loadMe(); showToast("Profile loaded", "ok"); }
    catch (err) { showToast(String(err.message || err), "err"); }
    finally { setBusy(loadMeBtn, false); }
  });

  verifyChainBtn?.addEventListener("click", async () => {
    setBusy(verifyChainBtn, true);
    try { await verifyChain(); showToast("Chain verified", "ok"); }
    catch (err) { showToast(String(err.message || err), "err"); }
    finally { setBusy(verifyChainBtn, false); }
  });

  // Minimal: tx / explorer / admin buttons (so UI doesn't break)
  createTxBtn?.addEventListener("click", async () => {
    try {
      const to_address = (txTo?.value || "").trim();
      const amount = (txAmount?.value || "").trim();
      if (!to_address || !amount) { showToast("Fill to + amount", "err"); return; }
      const r = await http("POST", "/api/v1/transactions", { to_address, amount });
      if (!r.ok) throw new Error(errMsg(r));
      showToast("Transaction sent", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  loadHistoryBtn?.addEventListener("click", async () => {
    try {
      const r = await http("GET", "/api/v1/transactions/my");
      if (!r.ok) throw new Error(errMsg(r));
      renderHistory(Array.isArray(r.data) ? r.data : (r.data?.items || []));
      showToast("History loaded", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  expTxBtn?.addEventListener("click", async () => {
    try {
      const h = (expTxHash?.value || "").trim();
      if (!h) { showToast("Enter tx hash", "err"); return; }
      const r = await http("GET", `/api/v1/explorer/tx/${encodeURIComponent(h)}`);
      if (!r.ok) throw new Error(errMsg(r));
      if (explorerOut) explorerOut.textContent = JSON.stringify(r.data, null, 2);
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  expAddrBtn?.addEventListener("click", async () => {
    try {
      const a = (expAddr?.value || "").trim();
      if (!a) { showToast("Enter address", "err"); return; }
      const r = await http("GET", `/api/v1/explorer/address/${encodeURIComponent(a)}`);
      if (!r.ok) throw new Error(errMsg(r));
      if (explorerOut) explorerOut.textContent = JSON.stringify(r.data, null, 2);
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  adminLoginBtn?.addEventListener("click", async () => {
    setBusy(adminLoginBtn, true);
    try {
      const password = adminPassword?.value || "";
      const r = await http("POST", "/api/v1/admin/login", { password });
      if (!r.ok) throw new Error(errMsg(r));
      adminToken = r.data?.token || "";
      if (adminTokenHint) adminTokenHint.textContent = `X-Admin-Token: ${adminToken || "—"}`;
      showToast("Admin token received", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    } finally {
      setBusy(adminLoginBtn, false);
    }
  });

  freezeBtn?.addEventListener("click", async () => {
    try {
      if (!adminToken) { showToast("Admin token required", "err"); return; }
      const email = (freezeEmail?.value || "").trim();
      const r = await http("POST", "/api/v1/admin/freeze", { email }, { "X-Admin-Token": adminToken });
      if (!r.ok) throw new Error(errMsg(r));
      if (adminOut) adminOut.textContent = JSON.stringify(r.data, null, 2);
      showToast("User frozen", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  unfreezeBtn?.addEventListener("click", async () => {
    try {
      if (!adminToken) { showToast("Admin token required", "err"); return; }
      const email = (freezeEmail?.value || "").trim();
      const r = await http("POST", "/api/v1/admin/unfreeze", { email }, { "X-Admin-Token": adminToken });
      if (!r.ok) throw new Error(errMsg(r));
      if (adminOut) adminOut.textContent = JSON.stringify(r.data, null, 2);
      showToast("User unfrozen", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  loadAuditBtn?.addEventListener("click", async () => {
    try {
      if (!adminToken) { showToast("Admin token required", "err"); return; }
      const r = await http("GET", "/api/v1/admin/audit", null, { "X-Admin-Token": adminToken });
      if (!r.ok) throw new Error(errMsg(r));
      const rows = Array.isArray(r.data) ? r.data : (r.data?.items || []);
      renderAudit(rows);
      showToast("Audit loaded", "ok");
    } catch (err) {
      showToast(String(err.message || err), "err");
    }
  });

  // ===== BOOT (STRICT) =====
  (async () => {
    showAuth(); // always show auth first

    const t = getToken();
    if (!t || t.trim().length < 10) {
      clearToken();
      return;
    }

    try {
      await loadMe();     // validate token
      showApp();
      await verifyChain().catch(() => {});
    } catch {
      clearToken();
      showAuth();
      showToast("Token invalid. Please sign in again.", "err");
    }
  })();
})();

