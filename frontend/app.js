(() => {
  const API = window.API_BASE || "";

  // ===== DOM =====
  const toast = document.getElementById("toast");

  // auth
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

  // shell
  const meEmail = document.getElementById("meEmail");
  const meEmail2 = document.getElementById("meEmail2");
  const meAddress = document.getElementById("meAddress");
  const meBalance = document.getElementById("meBalance");
  const logoutBtn = document.getElementById("logoutBtn");
  const refreshBtn = document.getElementById("refreshBtn");
  const pageTitle = document.getElementById("pageTitle");
  const menuBtn = document.getElementById("menuBtn");
  const sidebar = document.querySelector(".sidebar");

  // dashboard
  const loadMeBtn = document.getElementById("loadMeBtn");
  const verifyChainBtn = document.getElementById("verifyChainBtn");
  const chainVerifyOut = document.getElementById("chainVerifyOut");
  const chainStatusChip = document.getElementById("chainStatusChip");

  // tx
  const txTo = document.getElementById("txTo");
  const txAmount = document.getElementById("txAmount");
  const createTxBtn = document.getElementById("createTxBtn");
  const loadHistoryBtn = document.getElementById("loadHistoryBtn");
  const historyBody = document.getElementById("historyBody");

  // explorer
  const expTxHash = document.getElementById("expTxHash");
  const expAddr = document.getElementById("expAddr");
  const expTxBtn = document.getElementById("expTxBtn");
  const expAddrBtn = document.getElementById("expAddrBtn");
  const explorerOut = document.getElementById("explorerOut");

  // admin
  const adminPassword = document.getElementById("adminPassword");
  const adminLoginBtn = document.getElementById("adminLoginBtn");
  const adminTokenHint = document.getElementById("adminTokenHint");
  const freezeEmail = document.getElementById("freezeEmail");
  const freezeBtn = document.getElementById("freezeBtn");
  const unfreezeBtn = document.getElementById("unfreezeBtn");
  const loadAuditBtn = document.getElementById("loadAuditBtn");
  const auditBody = document.getElementById("auditBody");
  const adminOut = document.getElementById("adminOut");

  // views
  const viewMap = {
    dashboard: document.getElementById("view-dashboard"),
    transactions: document.getElementById("view-transactions"),
    explorer: document.getElementById("view-explorer"),
    admin: document.getElementById("view-admin"),
  };

  // ===== State =====
  let adminToken = ""; // X-Admin-Token
  let currentView = "dashboard";

  // ===== Utils =====
  function showToast(msg, type="inf"){
    toast.textContent = msg;
    toast.className = `toast show ${type}`;
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.className = "toast", 3200);
  }

  function setBusy(btn, busy){
    if(!btn) return;
    btn.disabled = !!busy;
    if(!btn.dataset.old) btn.dataset.old = btn.textContent;
    btn.textContent = busy ? "Please wait..." : btn.dataset.old;
  }

  function getToken(){ return localStorage.getItem("token") || ""; }
  function setToken(t){ localStorage.setItem("token", t); }
  function clearToken(){ localStorage.removeItem("token"); }

  async function http(method, path, body, extraHeaders={}){
    const headers = { "Content-Type": "application/json", ...extraHeaders };
    const t = getToken();
    if(t) headers["Authorization"] = `Bearer ${t}`;

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

  function errMsg(r){
    const d = r?.data;
    if(!d) return `Error (${r?.status || "?"})`;
    if(typeof d === "string") return d;
    if(d.detail){
      if(Array.isArray(d.detail)) return d.detail.map(x => x?.msg || "Invalid").join(", ");
      return d.detail;
    }
    return `Error (${r?.status || "?"})`;
  }

  function switchAuth(tab){
    const isLogin = tab === "login";
    tabLogin.classList.toggle("active", isLogin);
    tabRegister.classList.toggle("active", !isLogin);
    loginForm.classList.toggle("hidden", !isLogin);
    registerForm.classList.toggle("hidden", isLogin);
  }

  function showAuth(){
    authRoot.classList.remove("hidden");
    appRoot.classList.add("hidden");
    switchAuth("login");
  }

  function showApp(){
    authRoot.classList.add("hidden");
    appRoot.classList.remove("hidden");
    switchView("dashboard");
  }

  function switchView(name){
    currentView = name;
    Object.entries(viewMap).forEach(([k, el]) => el.classList.toggle("hidden", k !== name));
    document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.view === name));
    pageTitle.textContent = name[0].toUpperCase() + name.slice(1);
    if(sidebar) sidebar.classList.remove("open");
  }

  function setMe(u){
    const email = u?.email || "—";
    meEmail.textContent = email;
    meEmail2.textContent = email;
    meAddress.textContent = u?.address || "—";
    meBalance.textContent = (u?.balance ?? "—");
  }

  // ===== API actions (REAL endpoints) =====
  async function loadMe(){
    const r = await http("GET", "/api/v1/users/me");
    if(!r.ok) throw new Error(errMsg(r));
    setMe(r.data);
    return r.data;
  }

  async function verifyChain(){
    const r = await http("GET", "/api/v1/explorer/verify-chain");
    if(!r.ok) throw new Error(errMsg(r));
    // r.data whatever backend returns; show nicely
    const ok = (typeof r.data === "object") ? (r.data.ok ?? r.data.valid ?? null) : null;
    const text = ok === true ? "VALID ✅" : ok === false ? "INVALID ❌" : "OK ✅";
    chainVerifyOut.textContent = text;
    chainStatusChip.textContent = `Chain: ${text.replace(/\s/g,"")}`;
    return r.data;
  }

  async function createTx(to_address, amount){
    const r = await http("POST", "/api/v1/tx/create", { to_address, amount: Number(amount) });
    if(!r.ok) throw new Error(errMsg(r));
    return r.data;
  }

  async function loadHistory(){
    const r = await http("GET", "/api/v1/tx/history");
    if(!r.ok) throw new Error(errMsg(r));
    return Array.isArray(r.data) ? r.data : [];
  }

  async function explorerTx(block_hash){
    const r = await http("GET", `/api/v1/explorer/tx/${encodeURIComponent(block_hash)}`);
    if(!r.ok) throw new Error(errMsg(r));
    return r.data;
  }

  async function explorerAddress(address){
    const r = await http("GET", `/api/v1/explorer/address/${encodeURIComponent(address)}`);
    if(!r.ok) throw new Error(errMsg(r));
    return r.data;
  }

  async function adminLogin(password){
    // FastAPI: simple param -> query string
    const r = await http("POST", `/api/v1/admin/login?password=${encodeURIComponent(password)}`);
    if(!r.ok) throw new Error(errMsg(r));
    adminToken = r.data?.admin_token || "";
    if(!adminToken) throw new Error("Admin token not returned");
    adminTokenHint.textContent = `X-Admin-Token: ${adminToken}`;
    return adminToken;
  }

  async function adminFreeze(email){
    const r = await http("POST", `/api/v1/admin/freeze/${encodeURIComponent(email)}`, null, {
      "X-Admin-Token": adminToken
    });
    if(!r.ok) throw new Error(errMsg(r));
    return r.data;
  }

  async function adminUnfreeze(email){
    const r = await http("POST", `/api/v1/admin/unfreeze/${encodeURIComponent(email)}`, null, {
      "X-Admin-Token": adminToken
    });
    if(!r.ok) throw new Error(errMsg(r));
    return r.data;
  }

  async function adminAudit(){
    const r = await http("GET", "/api/v1/admin/audit", null, {
      "X-Admin-Token": adminToken
    });
    if(!r.ok) throw new Error(errMsg(r));
    return Array.isArray(r.data) ? r.data : [];
  }

  // ===== Render helpers =====
  function renderHistory(rows){
    if(!rows.length){
      historyBody.innerHTML = `<tr><td colspan="5" class="muted">No transactions</td></tr>`;
      return;
    }
    historyBody.innerHTML = rows.map((r, idx) => `
      <tr>
        <td>${idx+1}</td>
        <td class="mono">${r.from_address}</td>
        <td class="mono">${r.to_address}</td>
        <td class="right">${r.amount}</td>
        <td class="mono">${r.block_hash}</td>
      </tr>
    `).join("");
  }

  function renderAudit(rows){
    if(!rows.length){
      auditBody.innerHTML = `<tr><td colspan="4" class="muted">No logs</td></tr>`;
      return;
    }
    auditBody.innerHTML = rows.map(r => `
      <tr>
        <td class="mono">${(r.created_at || "").slice(0,19).replace("T"," ")}</td>
        <td class="mono">${r.actor}</td>
        <td>${r.action}</td>
        <td class="mono">${r.entity}</td>
      </tr>
    `).join("");
  }

  // ===== Events =====
  tabLogin.addEventListener("click", () => switchAuth("login"));
  tabRegister.addEventListener("click", () => switchAuth("register"));

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    setBusy(loginBtn, true);
    try{
      const payload = {
        email: (loginEmail.value || "").trim(),
        password: loginPassword.value || ""
      };
      const r = await http("POST", "/api/v1/auth/login", payload);
      if(!r.ok) throw new Error(errMsg(r));
      const t = r.data?.access_token;
      if(!t) throw new Error("Token not returned");
      setToken(t);
      showToast("Login successful", "ok");
      showApp();
      await loadMe().catch(()=>{});
      await verifyChain().catch(()=>{});
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(loginBtn, false);
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    setBusy(regBtn, true);
    try{
      const payload = {
        email: (regEmail.value || "").trim(),
        password: regPassword.value || ""
      };
      const r = await http("POST", "/api/v1/auth/register", payload);
      if(!r.ok) throw new Error(errMsg(r));
      showToast("Registered. Now sign in.", "ok");
      switchAuth("login");
      loginEmail.value = payload.email;
      loginPassword.value = payload.password;
      loginPassword.focus();
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(regBtn, false);
    }
  });

  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });

  logoutBtn.addEventListener("click", () => {
    clearToken();
    adminToken = "";
    adminTokenHint.textContent = "X-Admin-Token: —";
    showToast("Logged out", "inf");
    showAuth();
  });

  refreshBtn.addEventListener("click", async () => {
    try{
      if(getToken()){
        await loadMe();
        await verifyChain();
        showToast("Refreshed", "ok");
      }
    }catch(err){
      showToast(String(err.message || err), "err");
    }
  });

  menuBtn.addEventListener("click", () => {
    if(sidebar) sidebar.classList.toggle("open");
  });

  loadMeBtn.addEventListener("click", async () => {
    setBusy(loadMeBtn, true);
    try{
      await loadMe();
      showToast("Profile loaded", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(loadMeBtn, false);
    }
  });

  verifyChainBtn.addEventListener("click", async () => {
    setBusy(verifyChainBtn, true);
    try{
      await verifyChain();
      showToast("Chain verified", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(verifyChainBtn, false);
    }
  });

  createTxBtn.addEventListener("click", async () => {
    const to = (txTo.value || "").trim();
    const amount = (txAmount.value || "").trim();
    if(!to || !amount) return showToast("To address va amount kiriting", "err");

    setBusy(createTxBtn, true);
    try{
      const out = await createTx(to, amount);
      showToast("Transaction created", "ok");
      // history refresh
      const rows = await loadHistory();
      renderHistory(rows);
      // explorerOut show last tx JSON
      explorerOut.textContent = JSON.stringify(out, null, 2);
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(createTxBtn, false);
    }
  });

  loadHistoryBtn.addEventListener("click", async () => {
    setBusy(loadHistoryBtn, true);
    try{
      const rows = await loadHistory();
      renderHistory(rows);
      showToast("History loaded", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(loadHistoryBtn, false);
    }
  });

  expTxBtn.addEventListener("click", async () => {
    const h = (expTxHash.value || "").trim();
    if(!h) return showToast("block_hash kiriting", "err");
    setBusy(expTxBtn, true);
    try{
      const out = await explorerTx(h);
      explorerOut.textContent = JSON.stringify(out, null, 2);
      showToast("TX found", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(expTxBtn, false);
    }
  });

  expAddrBtn.addEventListener("click", async () => {
    const a = (expAddr.value || "").trim();
    if(!a) return showToast("address kiriting", "err");
    setBusy(expAddrBtn, true);
    try{
      const out = await explorerAddress(a);
      explorerOut.textContent = JSON.stringify(out, null, 2);
      showToast("Address found", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(expAddrBtn, false);
    }
  });

  adminLoginBtn.addEventListener("click", async () => {
    const p = (adminPassword.value || "").trim();
    if(!p) return showToast("Admin password kiriting", "err");
    setBusy(adminLoginBtn, true);
    try{
      await adminLogin(p);
      showToast("Admin token ready", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(adminLoginBtn, false);
    }
  });

  freezeBtn.addEventListener("click", async () => {
    const email = (freezeEmail.value || "").trim();
    if(!adminToken) return showToast("Avval admin login qiling", "err");
    if(!email) return showToast("Email kiriting", "err");
    setBusy(freezeBtn, true);
    try{
      const out = await adminFreeze(email);
      adminOut.textContent = JSON.stringify(out, null, 2);
      showToast("User frozen", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(freezeBtn, false);
    }
  });

  unfreezeBtn.addEventListener("click", async () => {
    const email = (freezeEmail.value || "").trim();
    if(!adminToken) return showToast("Avval admin login qiling", "err");
    if(!email) return showToast("Email kiriting", "err");
    setBusy(unfreezeBtn, true);
    try{
      const out = await adminUnfreeze(email);
      adminOut.textContent = JSON.stringify(out, null, 2);
      showToast("User unfrozen", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(unfreezeBtn, false);
    }
  });

  loadAuditBtn.addEventListener("click", async () => {
    if(!adminToken) return showToast("Avval admin login qiling", "err");
    setBusy(loadAuditBtn, true);
    try{
      const rows = await adminAudit();
      renderAudit(rows);
      adminOut.textContent = JSON.stringify(rows.slice(0, 5), null, 2);
      showToast("Audit loaded", "ok");
    }catch(err){
      showToast(String(err.message || err), "err");
    }finally{
      setBusy(loadAuditBtn, false);
    }
  });

// ===== Boot =====
const token = getToken();

if (token && token.trim().length > 10) {
  showApp();
  loadMe().catch(()=>{});
  verifyChain().catch(()=>{});
} else {
  clearToken();
  showAuth();
}
})();