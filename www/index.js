document.addEventListener("DOMContentLoaded", async () => {
  const dateTime = document.getElementById("datetime");
  const userInfo = document.getElementById("user-info");
  const simplehistInfo = document.getElementById("simplehist-info");
  const jobhistInfo = document.getElementById("jobhist-info");
  const portraitInfo = document.getElementById("portrait-info");

  const user = await (await fetch("/api/user")).json();
  const simplehist = await (await fetch("/api/simplehist")).json();

  if (Object.keys(user).length === 0 && simplehist.length === 0) {
    userInfo.innerHTML = "<p>データなし</p>";
    return;
  }

  dateTime.innerHTML = getTodayFormatted();

  userInfo.innerHTML = `
    <div class="user-image">
      <img src="/image.jpg" alt="User" loading="lazy">
    </div>
    <p><label>名前</label><span class="user-name">${escapeHTML(user.usr_name)} (${escapeHTML(
    user.usr_name_kana
  )})</span>
    </p>
    <p><label>住所</label>${escapeHTML(user.usr_addr)}</p>
    <div class="personal-block">
      <p><label>電話番号</label>${escapeHTML(user.usr_phone || "なし")}</p>
      <p><label>携帯番号</label>${escapeHTML(user.usr_mobile)}</p>
      <p><label>E メール</label>${escapeHTML(user.usr_email)}</p>
    </div>
    <div class="personal-block">
      <p><label>生年月日</label>${escapeHTML(user.usr_birthday)}</p>
      <p><label>年齢</label>満${escapeHTML(user.usr_age)}歳</p>
      <p><label>性別</label>${user.usr_gender === "1" ? "女" : "男"}</p>
      <p><label>扶養家族</label>${user.usr_family === "1" ? "あり" : "なし"}</p>
    </div>
    <p><label>免許・資格</label>${escapeHTML(user.usr_licenses).replace(
      /\n/g,
      "<br>"
    )}</p>
    <div><label>特技</label>${parseMarkdown(user.usr_skill)}</div>
    <div><label>志望動機</label>${parseMarkdown(user.usr_siboudouki)}</div>
    <p><label>通勤時間</label>${escapeHTML(user.usr_access)}</p>
    <div><label>趣味</label>${parseMarkdown(user.usr_hobby)}</div>
  `;

  simplehistInfo.innerHTML = `
    <h2>学歴・職歴</h2>
    <ul>
      ${simplehist
        .map(
          (h) => `<li>${escapeHTML(h.hist_datetime)} ${escapeHTML(h.hist_status)}: ${escapeHTML(h.hist_name)}</li>`
        )
        .join("")}
    </ul>
  `;

  const jobhist = await (await fetch("/api/jobhist")).json();
  jobhistInfo.innerHTML = `
    <h2>職務経歴</h2>
    ${jobhist
      .map(
        (j) => `
          <h4>${escapeHTML(j.job_name)}</h4>
          <div>${parseMarkdown(j.job_description)}</div>
        `
      )
      .join("")}
  `;

  const portrait = await (await fetch("/api/portrait")).json();
  portraitInfo.innerHTML = `
    <h2>ポートレイト</h2>
    ${portrait
      .map(
        (p) => `
          <h5>${escapeHTML(p.portrait_url)}</h5>
          <div>${parseMarkdown(p.portrait_summary)}</div>
        `
      )
      .join("")}
  `;
});

function parseMarkdown(text) {
  if (!text) return "";
  if (typeof marked !== "undefined" && marked.parse) {
    return marked.parse(text);
  }
  return escapeHTML(text).replace(/\n/g, "<br>");
}

function escapeHTML(text) {
  if (!text) return "";
  return text.replace(/[&<>"']/g, function(match) {
    const escape = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    };
    return escape[match];
  });
}

function getTodayFormatted() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}年${month}月${day}日 現在`;
}

function ipToNum(ip) {
  return ip
    .split(".")
    .reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0;
}

// admin クラスの要素を表示/非表示にする関数
function toggleAdminElements(show) {
  const adminElements = document.querySelectorAll(".admin");
  adminElements.forEach((element) => {
    element.style.display = show ? "block" : "none";
  });
}

async function checkServerNetwork() {
  const currentHost = window.location.hostname;
  const adminNetworks = [];

  // Default AP network
  adminNetworks.push({
    base: ipToNum("192.168.4.0"),
    mask: ipToNum("255.255.255.0")
  });

  try {
    const res = await fetch("/api/network");
    if (res.ok) {
      const info = await res.json();
      if (info.sta && info.sta.ip) {
        const staIp = ipToNum(info.sta.ip);
        const staMask = ipToNum(info.sta.netmask);
        const staBase = staIp & staMask;
        adminNetworks.push({
          base: staBase,
          mask: staMask
        });
      }
    }
  } catch (e) {
    console.warn("Failed to fetch network info", e);
  }

  const isIp = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(currentHost);

  let isAdmin = false;

  if (isIp) {
    const hostNum = ipToNum(currentHost);
    isAdmin = adminNetworks.some(net => (hostNum & net.mask) === net.base);
  }

  toggleAdminElements(isAdmin);
  return isAdmin;
}

// ページロード時に実行
document.addEventListener("DOMContentLoaded", function() {
  checkServerNetwork();
});

function recheckServerNetwork() {
  return checkServerNetwork();
}
