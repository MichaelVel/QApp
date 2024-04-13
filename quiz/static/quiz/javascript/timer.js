const time = window.setInterval(changeTimer,1000);

function changeTimer() {
  const timerElem = document.getElementById("timer");
  let currSec = parseInt(timerElem.value);

  if (currSec <= 0) {
    clearInterval(time);
    document.getElementById("submit-btn").click();
  } else {
    timerElem.value = currSec-1;
  }
}

function submitVals() {
    document.getElementById("submit-btn").click();
}

