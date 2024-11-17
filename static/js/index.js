
function fetchState() {
  fetch("/get_state")
    .then((response) => response.json())
    .then((data) => {
      const toggleSwitch = document.getElementById("toggle-switch");
      const volumeSlider = document.getElementById("myRange");
      const videoFeed = document.getElementById("video_feed");

      if (toggleSwitch) {
        toggleSwitch.checked = data.system_status;
      }
      if (videoFeed) {
        videoFeed.src = data.system_status ? "/video_feed" : "";
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
      })
        .then(() => {
          // Update the video feed based on the new system status
          const videoFeed = document.getElementById("video_feed");
          videoFeed.src = systemStatus ? "/video_feed" : "";
        })
        .catch((error) => console.error("Error updating state:", error));
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
    // playSoundButton.addEventListener("click", function () {
    //   updateCounts()
    //   const audio = new Audio("../sound/test_sound.aac");
    //   audio.volume = document.getElementById("myRange").value / 100;
    //   audio.play();
    // });
    playSoundButton.addEventListener("click", function () {
      updateCounts();

      // Send a request to the server to play the sound
      fetch("/play_sound")
        .then(response => response.json())
        .then(data => {
          if (data.message) {
            console.log(data.message);  // Log the success message (optional)
          }
        })
        .catch(error => {
          console.error("Error playing sound:", error);
        });
    });
  }
};

function updateCounts() {
  fetch('/get_counts')
    .then(response => response.json())
    .then(data => {
      document.getElementById('totalBirds').innerText = data.total;
      document.getElementById('flyingBirds').innerText = data.flying;
      document.getElementById('standingBirds').innerText = data.standing;
      //if (data.standing != 0) {
        //console.log("Yess")
        //fetch("/play_sound")
         // .then(response => response.json())
        //  .then(data => {
         //   if (data.message) {
       //       console.log(data.message);  
     //       }
   //       })
    //      .catch(error => {
    //        console.error("Error playing sound:", error);
    //      });
    //  }
    })
    .catch(err => console.error('Error fetching counts:', err));
}

setInterval(updateCounts, 500);

