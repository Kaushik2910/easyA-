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
