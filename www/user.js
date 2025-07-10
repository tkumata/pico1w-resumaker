document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("user-form");
  const response = await fetch("/api/user");
  const user = await response.json();

  form.usr_name.value = user.usr_name || "";
  form.usr_birthday.value = user.usr_birthday || "";
  form.usr_addr.value = user.usr_addr || "";
  form.usr_phone.value = user.usr_phone || "";
  form.usr_mobile.value = user.usr_mobile || "";
  form.usr_email.value = user.usr_email || "";
  form.usr_family.value = user.usr_family || "0";
  form.usr_licenses.value = user.usr_licenses || "";
  form.usr_siboudouki.value = user.usr_siboudouki || "";
  form.usr_access.value = user.usr_access || "";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
      usr_name: form.usr_name.value,
      usr_birthday: form.usr_birthday.value,
      usr_addr: form.usr_addr.value,
      usr_phone: form.usr_phone.value,
      usr_mobile: form.usr_mobile.value,
      usr_email: form.usr_email.value,
      usr_family: form.usr_family.value,
      usr_licenses: form.usr_licenses.value,
      usr_siboudouki: form.usr_siboudouki.value,
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
