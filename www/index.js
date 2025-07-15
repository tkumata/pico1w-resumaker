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
        <div class="personal-block">
          <p><label>名前</label>${user.usr_name}</p>
          <p><label>ふりがな</label>${user.usr_name_kana}</p>
          <p><label>性別</label>${user.usr_gender === "1" ? "女" : "男"}</p>
          <p><label>生年月日</label>${user.usr_birthday}</p>
          <p><label>年齢</label>${user.usr_age}</p>
        </div>
        <p><label>趣味</label>${user.usr_hobby.replace(/<br>/g, "<br>")}</p>
        <p><label>特技</label>${user.usr_skill.replace(/<br>/g, "<br>")}</p>
        <p><label>志望動機</label>${user.usr_siboudouki.replace(
          /<br>/g,
          "<br>"
        )}</p>
        <p><label>住所</label>${user.usr_addr}</p>
        <div class="personal-block">
          <p><label>電話番号</label>${user.usr_phone || "なし"}</p>
          <p><label>携帯電話番号</label>${user.usr_mobile}</p>
          <p><label>メールアドレス</label>${user.usr_email}</p>
        </div>
        <p><label>扶養家族</label>${
          user.usr_family === "1" ? "あり" : "なし"
        }</p>
        <p><label>免許・資格</label>${user.usr_licenses.replace(
          /<br>/g,
          "<br>"
        )}</p>
        <p><label>通勤時間</label>${user.usr_access}</p>
    `;

  simplehistInfo.innerHTML = `
        <h2>学歴・職歴</h2>
        <ul>
            ${simplehist
              .map(
                (h) =>
                  `<li>${h.hist_datetime} ${h.hist_status}: ${h.hist_name}</li>`
              )
              .join("")}
        </ul>
    `;

  jobhistInfo.innerHTML = `
    <h2>職務経歴</h2>
    <p>
        ${jobhist
          .map(
            (j) => `
              <h4>${j.job_name}</h4>
              <p>${j.job_description.replace(/<br>/g, "<br>")}</p>
            `
          )
          .join("")}
    </p>
  `;

  portraitInfo.innerHTML = `
    <h2>ポートレイト</h2>
    <ul>
      ${portrait
        .map(
          (p) => `
            <li>
                ${p.portrait_url} 
                <p>${p.portrait_summary.replace(/<br>/g, "<br>")}</p>
            </li>
          `
        )
        .join("")}
    </ul>
  `;
});
