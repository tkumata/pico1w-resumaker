let simplehistData = [];

async function loadSimplehist() {
  try {
    console.log("Fetching simplehist data from /api/simplehist");
    const response = await fetch("/api/simplehist");
    if (!response.ok) {
      console.error(
        "Failed to fetch simplehist data:",
        response.status,
        response.statusText
      );
      return;
    }
    simplehistData = await response.json();
    console.log("Simplehist data loaded:", simplehistData);
    renderSimplehist();
  } catch (error) {
    console.error("Error loading simplehist data:", error);
  }
}

function renderSimplehist() {
  const container = document.getElementById("simplehist-form");
  if (!container) {
    console.error("simplehist-form element not found");
    return;
  }
  container.innerHTML = simplehistData
    .map(
      (entry, index) => `
        <div class="entry">
            <label>日付: <input type="date" value="${
              entry.hist_datetime || ""
            }" onchange="updateSimplehist(${index}, 'hist_datetime', this.value)"></label>
            <label>状態: <select onchange="updateSimplehist(${index}, 'hist_status', this.value)">
                <option value="入学" ${
                  entry.hist_status === "入学" ? "selected" : ""
                }>入学</option>
                <option value="卒業" ${
                  entry.hist_status === "卒業" ? "selected" : ""
                }>卒業</option>
                <option value="入社" ${
                  entry.hist_status === "入社" ? "selected" : ""
                }>入社</option>
                <option value="退社" ${
                  entry.hist_status === "退社" ? "selected" : ""
                }>退社</option>
            </select></label>
            <label>名称: <input type="text" value="${
              entry.hist_name || ""
            }" onchange="updateSimplehist(${index}, 'hist_name', this.value)"></label>
            <button onclick="removeSimplehist(${index})">削除</button>
        </div>
    `
    )
    .join("");
  console.log(
    "Rendered simplehist form with",
    simplehistData.length,
    "entries"
  );
}

function updateSimplehist(index, key, value) {
  simplehistData[index][key] = value;
  console.log(`Updated simplehist entry ${index}:`, simplehistData[index]);
}

function addSimplehist() {
  simplehistData.push({
    hist_no: simplehistData.length + 1,
    hist_datetime: "",
    hist_status: "入学",
    hist_name: "",
  });
  console.log("Added new simplehist entry:", simplehistData);
  renderSimplehist();
}

function removeSimplehist(index) {
  simplehistData.splice(index, 1);
  simplehistData.forEach((entry, i) => (entry.hist_no = i + 1));
  console.log(
    "Removed simplehist entry at index",
    index,
    "New data:",
    simplehistData
  );
  renderSimplehist();
}

async function saveSimplehist() {
  try {
    console.log("Saving simplehist data:", simplehistData);
    const response = await fetch("/admin/simplehist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(simplehistData),
    });
    if (!response.ok) {
      console.error(
        "Failed to save simplehist data:",
        response.status,
        response.statusText
      );
      alert("保存に失敗しました");
      return;
    }
    alert("保存しました");
  } catch (error) {
    console.error("Error saving simplehist data:", error);
    alert("保存中にエラーが発生しました");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("simplehist.js loaded");
  loadSimplehist();
});
