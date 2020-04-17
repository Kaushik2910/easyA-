function getPriority() {
  var priority = document.getElementById("priority");
  switch (document.getElementById("priority").value) {
    case "class":
    case "professor":
      priority.value = "high";
      break;
    case "bad_info":
      priority.value = "medium";
      break;
    default:
      priority.value = "low";
  }
}

function isAnonymous() {
  var anon_btn = document.getElementById("anon_btn");
  var email = document.getElementById("email");
  if (anon_btn.classList.contains("active")) {
    email.value = "";
  }
}

function validateForm() {
  getPriority();
  isAnonymous();
  return true;
}
