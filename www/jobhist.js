// CrudBase を使用した職歴管理
const jobhistManager = new CrudBase({
  apiEndpoint: "/api/jobhist",
  adminEndpoint: "/admin/jobhist",
  containerId: "jobhist-form",
  dataKey: "jobhistData",
  itemNumberKey: "job_no",
  renderItem: (entry, index) => {
    const escapedName = jobhistManager.escapeHtml(entry.job_name || "");
    const escapedDesc = jobhistManager.escapeHtml(
      (entry.job_description || "").replace(/<br>/g, "\n")
    );
    return `
      <div class="entry">
        <label>企業名: <input type="text" value="${escapedName}" onchange="updateJobhist(${index}, 'job_name', this.value)"></label>
        <label>業務内容: <textarea onchange="updateJobhist(${index}, 'job_description', this.value)">${escapedDesc}</textarea></label>
        <button onclick="removeJobhist(${index})">削除</button>
      </div>
    `;
  },
});

function loadJobhist() {
  return jobhistManager.load();
}

function updateJobhist(index, key, value) {
  jobhistManager.update(index, key, value);
}

function addJobhist() {
  jobhistManager.add({
    job_name: "",
    job_description: "",
  });
}

function removeJobhist(index) {
  jobhistManager.remove(index);
}

function saveJobhist() {
  return jobhistManager.save();
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("jobhist.js loaded");
  loadJobhist();
});
