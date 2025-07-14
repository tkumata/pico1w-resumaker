document.addEventListener("DOMContentLoaded", async () => {
  const userInfo = document.getElementById("user-info");
  const simplehistInfo = document.getElementById("simplehist-info");
  const jobhistInfo = document.getElementById("jobhist-info");

  const user = await (await fetch("/api/user")).json();
  const simplehist = await (await fetch("/api/simplehist")).json();
  const jobhist = await (await fetch("/api/jobhist")).json();

  if (
    Object.keys(user).length === 0 &&
    simplehist.length === 0 &&
    jobhist.length === 0
  ) {
    userInfo.innerHTML = "<p>データなし</p>";
    return;
  }

  userInfo.innerHTML = `
        <h2>基本情報</h2>
        <p>名前: ${user.usr_name}</p>
        <p>生年月日: ${user.usr_birthday}</p>
        <p>住所: ${user.usr_addr}</p>
        <p>電話番号: ${user.usr_phone || "なし"}</p>
        <p>携帯電話番号: ${user.usr_mobile}</p>
        <p>メールアドレス: ${user.usr_email}</p>
        <p>扶養家族: ${user.usr_family === "1" ? "あり" : "なし"}</p>
        <p>免許・資格: ${user.usr_licenses.replace(/<br>/g, "<br>")}</p>
        <p>志望動機: ${user.usr_siboudouki.replace(/<br>/g, "<br>")}</p>
        <p>出社時間: ${user.usr_access}</p>
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
        <h2>詳細職歴</h2>
        <ul>
            ${jobhist
              .map(
                (j) => `
                <li>
                    ${j.job_name} 
                    <p>${j.job_description.replace(/<br>/g, "<br>")}</p>
                </li>
            `
              )
              .join("")}
        </ul>
    `;
});
