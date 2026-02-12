
const getJson = (url) => fetch(url).then((response) => response.json());
const postJson = (url, payload) =>
  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

function fetchState() {
  getJson("/get_state")
    .then((data) => {
      const toggleSwitch = document.getElementById("toggle-switch");
      const volumeSlider = document.getElementById("myRange");
      const videoFeed = document.getElementById("video_feed");

      if (toggleSwitch) toggleSwitch.checked = data.system_status;
      if (videoFeed) videoFeed.src = data.system_status ? "/video_feed" : "";
      if (volumeSlider) volumeSlider.value = data.volume;
    })
    .catch((error) => console.error("Error fetching state:", error));
}

function updateCounts() {
  getJson("/get_counts")
    .then((data) => {
      document.getElementById("totalBirds").innerText = data.total;
      document.getElementById("flyingBirds").innerText = data.flying;
      document.getElementById("standingBirds").innerText = data.standing;
    })
    .catch((err) => console.error("Error fetching counts:", err));
}

window.onload = () => {
  fetchState();

  const toggleSwitch = document.getElementById("toggle-switch");
  if (toggleSwitch) {
    toggleSwitch.addEventListener("change", (event) => {
      const systemStatus = event.target.checked;
      postJson("/update_state", { system_status: systemStatus })
        .then(() => {
          const videoFeed = document.getElementById("video_feed");
          if (videoFeed) videoFeed.src = systemStatus ? "/video_feed" : "";
        })
        .catch((error) => console.error("Error updating state:", error));
    });
  }

  const volumeSlider = document.getElementById("myRange");
  if (volumeSlider) {
    volumeSlider.addEventListener("input", (event) => {
      const volume = event.target.value;
      postJson("/update_state", { volume }).catch((error) =>
        console.error("Error updating volume:", error)
      );
    });
  }

  const playSoundButton = document.getElementById("playSoundButton");
  if (playSoundButton) {
    playSoundButton.addEventListener("click", () => {
      updateCounts();
      getJson("/play_sound")
        .then((data) => {
          if (data.message) console.log(data.message);
        })
        .catch((error) => console.error("Error playing sound:", error));
    });
  }
};

setInterval(updateCounts, 500);
