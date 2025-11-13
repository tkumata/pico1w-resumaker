// CrudBase を使用した学歴・職歴管理
const simplehistManager = new CrudBase({
  apiEndpoint: "/api/simplehist",
  adminEndpoint: "/admin/simplehist",
  containerId: "simplehist-form",
  dataKey: "simplehistData",
  itemNumberKey: "hist_no",
  renderItem: (entry, index) => {
    const escapedDatetime = simplehistManager.escapeHtml(entry.hist_datetime || "");
    const escapedName = simplehistManager.escapeHtml(entry.hist_name || "");
    const status = entry.hist_status || "入学";
    return `
      <div class="entry">
        <label>日付: <input type="date" value="${escapedDatetime}" onchange="updateSimplehist(${index}, 'hist_datetime', this.value)"></label>
        <label>状態: <select onchange="updateSimplehist(${index}, 'hist_status', this.value)">
          <option value="入学" ${status === "入学" ? "selected" : ""}>入学</option>
          <option value="卒業" ${status === "卒業" ? "selected" : ""}>卒業</option>
          <option value="入社" ${status === "入社" ? "selected" : ""}>入社</option>
          <option value="退社" ${status === "退社" ? "selected" : ""}>退社</option>
        </select></label>
        <label>名称: <input type="text" value="${escapedName}" onchange="updateSimplehist(${index}, 'hist_name', this.value)"></label>
        <button onclick="removeSimplehist(${index})">削除</button>
      </div>
    `;
  },
});

function loadSimplehist() {
  return simplehistManager.load();
}

function updateSimplehist(index, key, value) {
  simplehistManager.update(index, key, value);
}

function addSimplehist() {
  simplehistManager.add({
    hist_datetime: "",
    hist_status: "入学",
    hist_name: "",
  });
}

function removeSimplehist(index) {
  simplehistManager.remove(index);
}

function saveSimplehist() {
  return simplehistManager.save();
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("simplehist.js loaded");
  loadSimplehist();
});
