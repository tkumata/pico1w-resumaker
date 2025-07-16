document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("user-form");
  const response = await fetch("/api/user");
  const user = await response.json();

  form.usr_name.value = user.usr_name || "";
  form.usr_name_kana.value = user.usr_name_kana || "";
  form.usr_gender.value = user.usr_gender || "1";
  form.usr_birthday.value = user.usr_birthday || "";
  form.usr_age.value = user.usr_age || "";
  form.usr_addr.value = user.usr_addr || "";
  form.usr_phone.value = user.usr_phone || "";
  form.usr_mobile.value = user.usr_mobile || "";
  form.usr_email.value = user.usr_email || "";
  form.usr_family.value = user.usr_family || "1";
  form.usr_licenses.value = user.usr_licenses.replace(/<br>/g, "\n") || "";
  form.usr_siboudouki.value = user.usr_siboudouki.replace(/<br>/g, "\n") || "";
  form.usr_hobby.value = user.usr_hobby.replace(/<br>/g, "\n") || "";
  form.usr_skill.value = user.usr_skill.replace(/<br>/g, "\n") || "";
  form.usr_access.value = user.usr_access || "";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
      usr_name: form.usr_name.value,
      usr_name_kana: form.usr_name_kana.value,
      usr_gender: form.usr_gender.value,
      usr_birthday: form.usr_birthday.value,
      usr_age: form.usr_age.value,
      usr_addr: form.usr_addr.value,
      usr_phone: form.usr_phone.value,
      usr_mobile: form.usr_mobile.value,
      usr_email: form.usr_email.value,
      usr_family: form.usr_family.value,
      usr_licenses: form.usr_licenses.value,
      usr_siboudouki: form.usr_siboudouki.value,
      usr_hobby: form.usr_hobby.value,
      usr_skill: form.usr_skill.value,
      usr_access: form.usr_access.value,
    };
    await fetch("/admin/user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    alert("保存しました");
  });
});

/**
 * 胸像写真のアップロードフロントエンド処理
 */
async function uploadImage() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  if (!file) {
    alert("画像を選択してください");
    return;
  }

  const chunkSize = 1024; // Pico W 向けに小さめ
  const totalChunks = Math.ceil(file.size / chunkSize);
  const filename = "tmp.jpg";

  for (let i = 0; i < totalChunks; i++) {
    const start = i * chunkSize;
    const end = Math.min(file.size, start + chunkSize);
    const chunk = file.slice(start, end);

    const isFinal = i === totalChunks - 1;

    const headers = new Headers();
    headers.append("X-Filename", filename);
    headers.append("X-Final", isFinal.toString());

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        headers,
        body: chunk,
      });

      const result = await response.json();
      console.log(`Chunk ${i + 1}/${totalChunks}:`, result);
    } catch (error) {
      console.error(`アップロード中にエラーが発生しました:`, error);
      break;
    }
  }

  alert("アップロード完了");
}
