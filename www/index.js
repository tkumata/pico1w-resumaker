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
    <p><label>特技</label>${escapeHTML(user.usr_skill).replace(/\n/g, "<br>")}</p>
    <p><label>志望動機</label>${escapeHTML(user.usr_siboudouki).replace(
      /\n/g,
      "<br>"
    )}</p>
    <p><label>通勤時間</label>${escapeHTML(user.usr_access)}</p>
    <p><label>趣味</label>${escapeHTML(user.usr_hobby).replace(/\n/g, "<br>")}</p>
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
          <p>${escapeHTML(j.job_description).replace(/\n/g, "<br>")}</p>
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
          <p>${escapeHTML(p.portrait_summary).replace(/\n/g, "<br>")}</p>
        `
      )
      .join("")}
  `;
});

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

function isInAdminNetwork(ip) {
  const ipToNum = (ip) => {
    return ip
      .split(".")
      .reduce((acc, octet) => (acc << 8) + parseInt(octet), 0);
  };

  const targetIp = ipToNum(ip);
  const networkBase = ipToNum("192.168.11.0");
  const subnetMask = 0xffffff00;

  return (targetIp & subnetMask) === networkBase;
}

// admin クラスの要素を表示/非表示にする関数
function toggleAdminElements(show) {
  const adminElements = document.querySelectorAll(".admin");
  adminElements.forEach((element) => {
    element.style.display = show ? "block" : "none";
  });
}

function checkServerNetwork() {
  const currentHost = window.location.hostname;
  const ipPattern =
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

  if (ipPattern.test(currentHost)) {
    if (isInAdminNetwork(currentHost)) {
      toggleAdminElements(true);
      return true;
    } else {
      toggleAdminElements(false);
      return false;
    }
  } else {
    const adminHostPatterns = [/^192\.168\.11\.\d+$/];

    const isAdminHost = adminHostPatterns.some((pattern) => {
      if (pattern instanceof RegExp) {
        return pattern.test(currentHost);
      }
      return currentHost === pattern;
    });

    if (isAdminHost) {
      toggleAdminElements(true);
      return true;
    } else {
      toggleAdminElements(false);
      return false;
    }
  }
}

// ページロード時に実行
document.addEventListener("DOMContentLoaded", function () {
  const isAdminAccess = checkServerNetwork();
  const notification = document.getElementById("admin-notification");
});

function recheckServerNetwork() {
  return checkServerNetwork();
}
