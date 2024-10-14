function fetchState() {
  fetch("/get_state")
    .then((response) => response.json())
    .then((data) => {
      const toggleSwitch = document.getElementById("toggle-switch");
      const volumeSlider = document.getElementById("myRange");
      if (toggleSwitch) {
        toggleSwitch.checked = data.system_status;
        if (data.system_status) {
          const videoFeed = document.getElementById("video_feed");
          videoFeed.src = "/video_feed";
        }
      }
      if (volumeSlider) {
        volumeSlider.value = data.volume;
      }
    })
    .catch((error) => console.error("Error fetching state:", error));
}

window.onload = function () {
  fetchState();

  const toggleSwitch = document.getElementById("toggle-switch");
  if (toggleSwitch) {
    toggleSwitch.addEventListener("change", function (event) {
      const systemStatus = event.target.checked;
      fetch("/update_state", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ system_status: systemStatus }),
      }).catch((error) => console.error("Error updating state:", error));
    });
  }

  const volumeSlider = document.getElementById("myRange");
  if (volumeSlider) {
    volumeSlider.addEventListener("input", function (event) {
      const volume = event.target.value;
      fetch("/update_state", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ volume: volume }),
      }).catch((error) => console.error("Error updating volume:", error));
    });
  }

  const playSoundButton = document.getElementById("playSoundButton");
  if (playSoundButton) {
    playSoundButton.addEventListener("click", function () {
      const audio = new Audio("{{ url_for('play_sound') }}");
      audio.volume = document.getElementById("myRange").value / 100;
      audio.play();
    });
  }
};
