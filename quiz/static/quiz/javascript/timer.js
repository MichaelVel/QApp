const time = window.setInterval(changeTimer,1000);

window.setTimeout(function myFunction() {
  clearInterval(time);
  document.getElementById("submit-btn").click();
},16000);

function changeTimer() {
  let currSec = document.getElementById("timer").value;
  document.getElementById("timer").value = currSec-1;
}

function submitVals() {
    document.getElementById("submit-btn").click();
}

