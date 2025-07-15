let jobhistData = [];

async function loadJobhist() {
  try {
    console.log("Fetching jobhist data from /api/jobhist");
    const response = await fetch("/api/jobhist");
    if (!response.ok) {
      console.error(
        "Failed to fetch jobhist data:",
        response.status,
        response.statusText
      );
      return;
    }
    jobhistData = await response.json();
    console.log("Jobhist data loaded:", jobhistData);
    renderJobhist();
  } catch (error) {
    console.error("Error loading jobhist data:", error);
  }
}

function renderJobhist() {
  const container = document.getElementById("jobhist-form");
  if (!container) {
    console.error("jobhist-form element not found");
    return;
  }
  container.innerHTML = jobhistData
    .map(
      (entry, index) => `
      <div class="entry">
          <label>企業名: <input type="text" value="${
            entry.job_name || ""
          }" onchange="updateJobhist(${index}, 'job_name', this.value)"></label>
          <label>業務内容: <textarea onchange="updateJobhist(${index}, 'job_description', this.value)">${(
        entry.job_description || ""
      ).replace(/<br>/g, "\n")}</textarea></label>
          <button onclick="removeJobhist(${index})">削除</button>
      </div>
      `
    )
    .join("");
  console.log("Rendered jobhist form with", jobhistData.length, "entries");
}

function updateJobhist(index, key, value) {
  jobhistData[index][key] = value;
  console.log(`Updated jobhist entry ${index}:`, jobhistData[index]);
}

function addJobhist() {
  jobhistData.push({
    job_no: jobhistData.length + 1,
    job_name: "",
    job_description: "",
  });
  console.log("Added new jobhist entry:", jobhistData);
  renderJobhist();
}

function removeJobhist(index) {
  jobhistData.splice(index, 1);
  jobhistData.forEach((entry, i) => (entry.job_no = i + 1));
  console.log(
    "Removed jobhist entry at index",
    index,
    "New data:",
    jobhistData
  );
  renderJobhist();
}

async function saveJobhist() {
  try {
    console.log("Saving jobhist data:", jobhistData);
    const response = await fetch("/admin/jobhist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(jobhistData),
    });
    if (!response.ok) {
      console.error(
        "Failed to save jobhist data:",
        response.status,
        response.statusText
      );
      alert("保存に失敗しました");
      return;
    }
    alert("保存しました");
  } catch (error) {
    console.error("Error saving jobhist data:", error);
    alert("保存中にエラーが発生しました");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("jobhist.js loaded");
  loadJobhist();
});
