/* LORD Frontend (Vanilla JS SPA) */

const API_BASE = (window.APP_CONFIG && window.APP_CONFIG.API_BASE) || "http://127.0.0.1:8000";

/** ====== State / Storage ====== **/
const store = {
  get token(){ return localStorage.getItem("lord_token") || ""; },
  set token(v){ v ? localStorage.setItem("lord_token", v) : localStorage.removeItem("lord_token"); },
  get email(){ return localStorage.getItem("lord_email") || ""; },
  set email(v){ v ? localStorage.setItem("lord_email", v) : localStorage.removeItem("lord_email"); },
  get address(){ return localStorage.getItem("lord_address") || ""; },
  set address(v){ v ? localStorage.setItem("lord_address", v) : localStorage.removeItem("lord_address"); },
  get balance(){ return localStorage.getItem("lord_balance") || ""; },
  set balance(v){ v ? localStorage.setItem("lord_balance", v) : localStorage.removeItem("lord_balance"); },

  get adminToken(){ return localStorage.getItem("lord_admin_token") || ""; },
  set adminToken(v){ v ? localStorage.setItem("lord_admin_token", v) : localStorage.removeItem("lord_admin_token"); },
};

const el = (id) => document.getElementById(id);

function toast(title, desc){
  el("toastTitle").textContent = title;
  el("toastDesc").textContent = desc || "";
  const t = el("toast");
  t.classList.add("show");
  setTimeout(()=>t.classList.remove("show"), 3800);
}

/** ====== API Helpers ====== **/
async function api(path, { method="GET", token="", body=null, admin=false } = {}){
  const headers = { "accept":"application/json" };
  if (body !== null) headers["Content-Type"] = "application/json";

  const authToken = admin ? store.adminToken : (token || store.token);
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== null ? JSON.stringify(body) : null
  });

  const text = await res.text();
  let data = null;
  try{ data = text ? JSON.parse(text) : null; } catch(e){ data = text; }

  if (!res.ok){
    const msg = (data && (data.detail || data.message)) ? (data.detail || data.message) : `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

/** ====== Routing ====== **/
const routes = {
  "#/": viewHome,
  "#/auth": viewAuth,
  "#/wallet": viewWallet,
  "#/send": viewSend,
  "#/explorer": viewExplorer,
  "#/admin": viewAdmin,
};

function go(hash){
  location.hash = hash;
}

window.addEventListener("hashchange", render);
window.addEventListener("load", () => {
  if (!location.hash) location.hash = "#/";
  render();
});

function render(){
  const hash = location.hash.split("?")[0];
  const fn = routes[hash] || viewHome;
  renderNav(hash);
  fn().catch(err => {
    toast("Xatolik", err.message || String(err));
  });
}

/** ====== Nav ====== **/
function renderNav(active){
  const nav = el("nav");
  const items = [
    ["#/","Home"],
    ["#/auth","Auth"],
    ["#/wallet","Wallet"],
    ["#/send","Send TX"],
    ["#/explorer","Explorer"],
    ["#/admin","Admin"],
  ];
  nav.innerHTML = items.map(([h,label]) => {
    const cls = `pill ${active===h ? "active":""}`;
    return `<a class="${cls}" href="${h}">${label}</a>`;
  }).join("");
}

/** ====== Views ====== **/
function setCards(mainHtml, sideHtml){
  el("mainCard").innerHTML = mainHtml;
  el("sideCard").innerHTML = sideHtml;
}

/** Home **/
async function viewHome(){
  setCards(
`<h2>Holat</h2>
<p>Bu UI backend’ingizdagi /api/v1 endpointlar bilan ishlaydi. Avval Auth qiling, keyin Wallet/Send/Explorer ishlaydi.</p>

<div class="kv">
  <div class="k">API Base</div><div class="mono">${API_BASE}</div>
  <div class="k">User Token</div><div class="mono">${store.token ? "BOR ✅" : "YO‘Q ❌"}</div>
  <div class="k">Admin Token</div><div class="mono">${store.adminToken ? "BOR ✅" : "YO‘Q ❌"}</div>
  <div class="k">Email</div><div class="mono">${store.email || "-"}</div>
  <div class="k">Address</div><div class="mono">${store.address || "-"}</div>
  <div class="k">Balance</div><div class="mono">${store.balance || "-"}</div>
</div>

<div class="btns">
  <button class="btn primary" id="btnAuth">Auth ga o‘tish</button>
  <button class="btn" id="btnExplorer">Explorer</button>
  <button class="btn danger" id="btnLogout">Logout</button>
</div>
`,
`<h2>Tez tekshiruv</h2>
<p class="small">1) Auth → Register  ✅<br/>2) Auth → Login → OTP → Verify ✅<br/>3) Wallet → Profile/Balance ✅<br/>4) Send TX → Create TX ✅<br/>5) Explorer → Address/Blocks ✅</p>
<hr class="sep"/>
<div class="badge">Eslatma</div>
<p class="small">Agar qaysidir endpoint nomi sizda biroz boshqacha bo‘lsa, <span class="mono">app.js</span> ichidagi yo‘llarni moslab qo‘yamiz.</p>`
  );

  el("btnAuth").onclick = ()=>go("#/auth");
  el("btnExplorer").onclick = ()=>go("#/explorer");
  el("btnLogout").onclick = ()=>{
    store.token = "";
    store.email = "";
    store.address = "";
    store.balance = "";
    toast("OK", "User session tozalandi");
    render();
  };
}

/** Auth **/
async function viewAuth(){
  setCards(
`<h2>Auth</h2>
<p>Register → Login → OTP Verify → Token olinadi.</p>

<div class="row">
  <div>
    <h3 style="margin:6px 0 0; font-size:15px;">1) Register</h3>
    <div class="field">
      <div class="label">Email</div>
      <input class="input" id="regEmail" placeholder="test1@mail.com" value="${store.email || ""}"/>
    </div>
    <div class="field">
      <div class="label">Password</div>
      <input class="input" id="regPass" type="password" placeholder="Test12345!"/>
    </div>
    <div class="btns">
      <button class="btn primary" id="btnRegister">Register</button>
    </div>
  </div>

  <div>
    <h3 style="margin:6px 0 0; font-size:15px;">2) Login (OTP yuboradi)</h3>
    <div class="field">
      <div class="label">Email</div>
      <input class="input" id="logEmail" placeholder="test1@mail.com" value="${store.email || ""}"/>
    </div>
    <div class="field">
      <div class="label">Password</div>
      <input class="input" id="logPass" type="password" placeholder="Test12345!"/>
    </div>
    <div class="btns">
      <button class="btn good" id="btnLogin">Login (OTP)</button>
    </div>

    <hr class="sep"/>

    <h3 style="margin:6px 0 0; font-size:15px;">3) Verify OTP → Token</h3>
    <div class="field">
      <div class="label">OTP Code</div>
      <input class="input" id="otpCode" placeholder="123456"/>
    </div>
    <div class="btns">
      <button class="btn primary" id="btnVerify">Verify → Token</button>
    </div>
  </div>
</div>

<hr class="sep"/>

<div class="btns">
  <button class="btn" id="btnMe">Profile (me)</button>
  <button class="btn danger" id="btnClear">Clear Tokens</button>
</div>
`,
`<h2>Token holati</h2>
<div class="kv">
  <div class="k">User Token</div><div class="mono">${store.token ? store.token.slice(0, 22) + "..." : "-"}</div>
  <div class="k">Email</div><div class="mono">${store.email || "-"}</div>
</div>

<hr class="sep"/>
<div class="badge">Agar login 500 bersa</div>
<p class="small">Backend logini ko‘ring (uvicorn konsol). Odatda DB schema mismatch yoki OTP endpoint nomi farqi bo‘ladi.</p>`
  );

  el("btnRegister").onclick = async () => {
    const email = el("regEmail").value.trim();
    const password = el("regPass").value;
    if (!email || !password) return toast("Stop", "Email va password kiriting");
    const out = await api("/api/v1/auth/register", { method:"POST", body:{ email, password } });
    store.email = out.email || email;
    store.address = out.address || store.address;
    store.balance = String(out.balance ?? store.balance);
    toast("Register OK", "Endi Login qiling");
    render();
  };

  el("btnLogin").onclick = async () => {
    const email = el("logEmail").value.trim();
    const password = el("logPass").value;
    if (!email || !password) return toast("Stop", "Email va password kiriting");
    store.email = email;

    // Sizning backend logicingizga mos: login OTP yuboradi
    await api("/api/v1/auth/login", { method:"POST", body:{ email, password } });
    toast("Login OK", "OTP keldi (emailda yoki backend logda). Verify qiling.");
  };

  el("btnVerify").onclick = async () => {
    const email = (store.email || el("logEmail").value.trim());
    const code = el("otpCode").value.trim();
    if (!email || !code) return toast("Stop", "Email va OTP code kerak");
    // Backend’ga mos: verify-otp token qaytaradi
    const out = await api("/api/v1/auth/verify-otp", { method:"POST", body:{ email, code } });
    // token format: { access_token, token_type } yoki { token }
    const token = out.access_token || out.token || "";
    if (!token) throw new Error("Token qaytmadi (verify-otp javobini tekshiring)");
    store.token = token;
    toast("Token OK", "Wallet bo‘limiga o‘ting");
    go("#/wallet");
  };

  el("btnMe").onclick = async () => {
    // Sizda /me bo‘lishi mumkin. Agar boshqa bo‘lsa, aytasiz moslab beraman.
    const out = await api("/api/v1/auth/me", { method:"GET" });
    store.address = out.address || store.address;
    store.balance = String(out.balance ?? store.balance);
    toast("ME OK", "Profil yangilandi");
    render();
  };

  el("btnClear").onclick = () => {
    store.token = "";
    store.adminToken = "";
    toast("OK", "Tokenlar tozalandi");
    render();
  };
}

/** Wallet **/
async function viewWallet(){
  setCards(
`<h2>Wallet</h2>
<p>Profil va balansni ko‘rasiz. Token bo‘lmasa Auth qiling.</p>

<div class="btns">
  <button class="btn primary" id="btnRefresh">Refresh Profile</button>
  <button class="btn" id="btnToSend">Send TX</button>
</div>

<div class="kv">
  <div class="k">Email</div><div class="mono">${store.email || "-"}</div>
  <div class="k">Address</div><div class="mono">${store.address || "-"}</div>
  <div class="k">Balance</div><div class="mono">${store.balance || "-"}</div>
</div>
`,
`<h2>Holat</h2>
<p class="small">Agar “401 Unauthorized” chiqsa — token yo‘q yoki eskirgan. Auth bo‘limiga qayting.</p>
<hr class="sep"/>
<div class="badge">Mint</div>
<p class="small">Boshlang‘ich balans backend tarafdan SYSTEM_MINT orqali beriladi.</p>`
  );

  el("btnRefresh").onclick = async () => {
    const out = await api("/api/v1/auth/me", { method:"GET" });
    store.address = out.address || store.address;
    store.balance = String(out.balance ?? store.balance);
    toast("OK", "Yangilandi");
    render();
  };
  el("btnToSend").onclick = ()=>go("#/send");
}

/** Send TX **/
async function viewSend(){
  setCards(
`<h2>Send Transaction</h2>
<p>1 tx = 1 block. Token kerak.</p>

<div class="field">
  <div class="label">To address</div>
  <input class="input" id="toAddr" placeholder="LORD_xxx..."/>
</div>
<div class="field">
  <div class="label">Amount</div>
  <input class="input" id="amount" placeholder="10.5"/>
</div>

<div class="btns">
  <button class="btn primary" id="btnSend">Create TX</button>
  <button class="btn" id="btnExplorer">Explorer</button>
</div>

<hr class="sep"/>
<div class="badge">Natija</div>
<div id="txResult" class="mono small" style="margin-top:10px;">-</div>
`,
`<h2>Maslahat</h2>
<p class="small">
Agar sizda transaction endpoint boshqacha nomlangan bo‘lsa, quyidagilarni moslab beramiz:
<br/>• <span class="mono">/api/v1/transactions</span> (POST)
<br/>• yoki <span class="mono">/api/v1/tx/create</span>
</p>`
  );

  el("btnSend").onclick = async () => {
    const to_address = el("toAddr").value.trim();
    const amountStr = el("amount").value.trim();
    if (!to_address || !amountStr) return toast("Stop", "To address va amount kiriting");

    // amountni number qilib yuboramiz, backend Decimal qabul qilsa ham JSONda number/string bo‘lishi mumkin
    const payload = { to_address, amount: amountStr };

    // Default: /api/v1/transactions
    const out = await api("/api/v1/transactions", { method:"POST", body: payload });

    el("txResult").textContent = JSON.stringify(out, null, 2);
    toast("TX OK", "Explorer’dan tekshiring");
  };

  el("btnExplorer").onclick = ()=>go("#/explorer");
}

/** Explorer **/
async function viewExplorer(){
  setCards(
`<h2>Explorer</h2>
<p>Address yoki block/tx qidirish.</p>

<div class="field">
  <div class="label">Address</div>
  <input class="input" id="exAddr" placeholder="LORD_xxx..." value="${store.address || ""}"/>
</div>
<div class="btns">
  <button class="btn primary" id="btnAddr">Search Address</button>
  <button class="btn" id="btnLatest">Latest Blocks</button>
</div>

<hr class="sep"/>
<div id="exOut" class="mono small">-</div>
`,
`<h2>Endpointlar</h2>
<p class="small">
Default qilib shularni ishlatyapman:
<br/>• <span class="mono">GET /api/v1/explorer/address/{address}</span>
<br/>• <span class="mono">GET /api/v1/explorer/blocks?limit=10</span>
</p>`
  );

  el("btnAddr").onclick = async () => {
    const addr = el("exAddr").value.trim();
    if (!addr) return toast("Stop", "Address kiriting");
    const out = await api(`/api/v1/explorer/address/${encodeURIComponent(addr)}`, { method:"GET" });
    el("exOut").textContent = JSON.stringify(out, null, 2);
    toast("OK", "Address topildi");
  };

  el("btnLatest").onclick = async () => {
    const out = await api(`/api/v1/explorer/blocks?limit=10`, { method:"GET" });
    el("exOut").textContent = JSON.stringify(out, null, 2);
    toast("OK", "Latest blocks");
  };
}

/** Admin **/
async function viewAdmin(){
  setCards(
`<h2>Admin Panel</h2>
<p>Admin token alish (login) va audit/monitoring endpointlari.</p>

<h3 style="margin:6px 0 0; font-size:15px;">Admin Login</h3>
<div class="field">
  <div class="label">Admin password</div>
  <input class="input" id="adminPass" type="password" placeholder="admin parol..."/>
</div>
<div class="btns">
  <button class="btn primary" id="btnAdminLogin">Admin Login</button>
  <button class="btn danger" id="btnAdminLogout">Admin Logout</button>
</div>

<hr class="sep"/>

<h3 style="margin:6px 0 0; font-size:15px;">Audit logs</h3>
<div class="row">
  <div class="field">
    <div class="label">Limit</div>
    <input class="input" id="auditLimit" value="20"/>
  </div>
  <div class="field">
    <div class="label">Search (optional)</div>
    <input class="input" id="auditQ" placeholder="action/entity/address..."/>
  </div>
</div>
<div class="btns">
  <button class="btn good" id="btnAudit">Load Audit</button>
</div>

<hr class="sep"/>
<div id="adminOut" class="mono small">-</div>
`,
`<h2>Admin token</h2>
<div class="kv">
  <div class="k">Admin Token</div><div class="mono">${store.adminToken ? store.adminToken.slice(0,22)+"..." : "-"}</div>
</div>

<hr class="sep"/>
<div class="badge">Eslatma</div>
<p class="small">Agar admin endpoint nomlari sizda farq qilsa, logdan ko‘rib moslab beramiz.</p>`
  );

  el("btnAdminLogin").onclick = async () => {
    const password = el("adminPass").value;
    if (!password) return toast("Stop", "Admin parol kiriting");

    // Default: /api/v1/admin/login  -> { access_token }
    const out = await api("/api/v1/admin/login", { method:"POST", body:{ password }, admin:true });
    const token = out.access_token || out.token || "";
    if (!token) throw new Error("Admin token qaytmadi (admin login response tekshiring)");
    store.adminToken = token;
    toast("Admin OK", "Audit’ni yuklab ko‘ring");
    render();
  };

  el("btnAdminLogout").onclick = () => {
    store.adminToken = "";
    toast("OK", "Admin token tozalandi");
    render();
  };

  el("btnAudit").onclick = async () => {
    const limit = Number(el("auditLimit").value || 20);
    const q = (el("auditQ").value || "").trim();
    const qs = new URLSearchParams();
    qs.set("limit", String(isNaN(limit) ? 20 : limit));
    if (q) qs.set("q", q);

    // Default: /api/v1/admin/audit?limit=20&q=...
    const out = await api(`/api/v1/admin/audit?${qs.toString()}`, { method:"GET", admin:true });
    el("adminOut").textContent = JSON.stringify(out, null, 2);
    toast("OK", "Audit yuklandi");
  };
}
