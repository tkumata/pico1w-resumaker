// CrudBase を使用したポートフォリオ管理
const portraitManager = new CrudBase({
  apiEndpoint: "/api/portrait",
  adminEndpoint: "/admin/portrait",
  containerId: "portrait-form",
  dataKey: "portraitData",
  itemNumberKey: "portrait_no",
  renderItem: (entry, index) => {
    const escapedUrl = portraitManager.escapeHtml(entry.portrait_url || "");
    const escapedSummary = portraitManager.escapeHtml(
      entry.portrait_summary || ""
    );
    return `
      <div class="entry">
        <label>URL: <input type="text" value="${escapedUrl}" onchange="updatePortrait(${index}, 'portrait_url', this.value)"></label>
        <label>概要: <textarea onchange="updatePortrait(${index}, 'portrait_summary', this.value)">${escapedSummary}</textarea></label>
        <button onclick="removePortrait(${index})">削除</button>
      </div>
    `;
  },
});

function loadPortrait() {
  return portraitManager.load();
}

function updatePortrait(index, key, value) {
  portraitManager.update(index, key, value);
}

function addPortrait() {
  portraitManager.add({
    portrait_url: "",
    portrait_summary: "",
  });
}

function removePortrait(index) {
  portraitManager.remove(index);
}

function savePortrait() {
  return portraitManager.save();
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("portrait.js loaded");
  loadPortrait();
});
