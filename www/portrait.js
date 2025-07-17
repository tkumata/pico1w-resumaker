let portraitData = [];

async function loadPortrait() {
  try {
    console.log("Fetching portrait data from /api/portrait");
    const response = await fetch("/api/portrait");
    if (!response.ok) {
      console.error(
        "Failed to fetch portrait data:",
        response.status,
        response.statusText
      );
      return;
    }
    portraitData = await response.json();
    console.log("Portrait data loaded:", portraitData);
    renderPortrait();
  } catch (error) {
    console.error("Error loading portrait data:", error);
  }
}

function renderPortrait() {
  const container = document.getElementById("portrait-form");
  if (!container) {
    console.error("portrait-form element not found");
    return;
  }
  container.innerHTML = portraitData
    .map(
      (entry, index) => `
        <div class="entry">
          <label>URL: <input type="text" value="${
            entry.portrait_url || ""
          }" onchange="updatePortrait(${index}, 'portrait_url', this.value)"></label>
          <label>概要: <textarea onchange="updatePortrait(${index}, 'portrait_summary', this.value)">${(
        entry.portrait_summary || ""
      ).replace(/<br>/g, "\n")}</textarea></label>
          <button onclick="removePortrait(${index})">削除</button>
        </div>
      `
    )
    .join("");
  console.log("Rendered portrait form with", portraitData.length, "entries");
}

function updatePortrait(index, key, value) {
  portraitData[index][key] = value;
  console.log(`Updated portrait entry ${index}:`, portraitData[index]);
}

function addPortrait() {
  portraitData.push({
    portrait_no: portraitData.length + 1,
    portrait_url: "",
    portrait_summary: "",
  });
  console.log("Added new portrait entry:", portraitData);
  renderPortrait();
}

function removePortrait(index) {
  portraitData.splice(index, 1);
  portraitData.forEach((entry, i) => (entry.portrait_no = i + 1));
  console.log(
    "Removed portrait entry at index",
    index,
    "New data:",
    portraitData
  );
  renderPortrait();
}

async function savePortrait() {
  try {
    console.log("Saving portrait data:", portraitData);
    const response = await fetch("/admin/portrait", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(portraitData),
    });
    if (!response.ok) {
      console.error(
        "Failed to save portrait data:",
        response.status,
        response.statusText
      );
      alert("保存に失敗しました");
      return;
    }
    alert("保存しました");
  } catch (error) {
    console.error("Error saving portrait data:", error);
    alert("保存中にエラーが発生しました");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("portrait.js loaded");
  loadPortrait();
});
