document.addEventListener("DOMContentLoaded", async () => {
  const userInfo = document.getElementById("user-info");
  const simplehistInfo = document.getElementById("simplehist-info");
  const jobhistInfo = document.getElementById("jobhist-info");
  const portraitInfo = document.getElementById("portrait-info");

  const user = await (await fetch("/api/user")).json();
  const simplehist = await (await fetch("/api/simplehist")).json();
  const jobhist = await (await fetch("/api/jobhist")).json();
  const portrait = await (await fetch("/api/portrait")).json();

  if (
    Object.keys(user).length === 0 &&
    simplehist.length === 0 &&
    jobhist.length === 0
  ) {
    userInfo.innerHTML = "<p>データなし</p>";
    return;
  }

  userInfo.innerHTML = `
    <div class="user-image">
      <img src="/image.jpg" alt="User">
    </div>
    <p><label>名前</label><span class="user-name">${user.usr_name} (${
    user.usr_name_kana
  })</span>
    </p>
    <p><label>住所</label>${user.usr_addr}</p>
    <div class="personal-block">
      <p><label>電話番号</label>${user.usr_phone || "なし"}</p>
      <p><label>携帯電話番号</label>${user.usr_mobile}</p>
      <p><label>メールアドレス</label>${user.usr_email}</p>
    </div>
    <div class="personal-block">
      <p><label>生年月日</label>${user.usr_birthday}</p>
      <p><label>年齢</label>満${user.usr_age}歳</p>
      <p><label>性別</label>${user.usr_gender === "1" ? "女" : "男"}</p>
      <p><label>扶養家族</label>${user.usr_family === "1" ? "あり" : "なし"}</p>
    </div>
    <p><label>免許・資格</label>${user.usr_licenses.replace(
      /<br>/g,
      "<br>"
    )}</p>
    <p><label>特技</label>${user.usr_skill.replace(/<br>/g, "<br>")}</p>
    <p><label>志望動機</label>${user.usr_siboudouki.replace(
      /<br>/g,
      "<br>"
    )}</p>
    <p><label>通勤時間</label>${user.usr_access}</p>
    <p><label>趣味</label>${user.usr_hobby.replace(/<br>/g, "<br>")}</p>
  `;

  simplehistInfo.innerHTML = `
    <h2>学歴・職歴</h2>
    <ul>
      ${simplehist
        .map(
          (h) => `<li>${h.hist_datetime} ${h.hist_status}: ${h.hist_name}</li>`
        )
        .join("")}
    </ul>
  `;

  jobhistInfo.innerHTML = `
    <h2>職務経歴</h2>
    ${jobhist
      .map(
        (j) => `
          <h4>${j.job_name}</h4>
          <p>${j.job_description.replace(/<br>/g, "<br>")}</p>
        `
      )
      .join("")}
  `;

  portraitInfo.innerHTML = `
    <h2>ポートレイト</h2>
    ${portrait
      .map(
        (p) => `
          <h5>${p.portrait_url}</h5>
          <p>${p.portrait_summary.replace(/<br>/g, "<br>")}</p>
        `
      )
      .join("")}
  `;
});

function isInAdminNetwork(ip) {
  // IPアドレスを数値に変換
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

// 現在のページのホスト名/IPアドレスをチェック
function checkServerNetwork() {
  const currentHost = window.location.hostname;

  console.log("現在のホスト:", currentHost);

  // IPアドレスの正規表現パターン
  const ipPattern =
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

  if (ipPattern.test(currentHost)) {
    // 直接IPアドレスでアクセスしている場合
    if (isInAdminNetwork(currentHost)) {
      console.log("✓ 管理者ネットワークのサーバーにアクセス中");
      toggleAdminElements(true);
      return true;
    } else {
      console.log("✗ 管理者ネットワーク外のサーバーにアクセス中");
      toggleAdminElements(false);
      return false;
    }
  } else {
    // ホスト名でアクセスしている場合
    console.log("ホスト名でアクセス中:", currentHost);

    // 特定のホスト名パターンをチェック（必要に応じて）
    const adminHostPatterns = [/^192\.168\.11\.\d+$/];

    const isAdminHost = adminHostPatterns.some((pattern) => {
      if (pattern instanceof RegExp) {
        return pattern.test(currentHost);
      }
      return currentHost === pattern;
    });

    if (isAdminHost) {
      console.log("✓ 管理者ホスト名でアクセス中");
      toggleAdminElements(true);
      return true;
    } else {
      console.log("✗ 一般ホスト名でアクセス中");
      toggleAdminElements(false);
      return false;
    }
  }
}

// ページロード時に実行
document.addEventListener("DOMContentLoaded", function () {
  console.log("サーバーネットワーク判定を開始...");

  const isAdminAccess = checkServerNetwork();

  // デバッグ情報の表示
  const debugInfo = document.getElementById("debug-info");
  if (debugInfo) {
    debugInfo.innerHTML = `
      <p>現在のホスト: ${window.location.hostname}</p>
      <p>フルURL: ${window.location.href}</p>
      <p>管理者アクセス: ${isAdminAccess ? "有効" : "無効"}</p>
    `;
  }

  const notification = document.getElementById("admin-notification");
  if (notification) {
    if (isAdminAccess) {
      notification.textContent = "管理者ネットワークからアクセス中";
      notification.style.color = "green";
      notification.style.display = "block";
    } else {
      notification.textContent = "一般ネットワークからアクセス中";
      notification.style.color = "orange";
      notification.style.display = "block";
    }
  }
});

function recheckServerNetwork() {
  return checkServerNetwork();
}
