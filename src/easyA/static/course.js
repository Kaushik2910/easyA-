var user = document.getElementById("user");
var fixed_user = user.innerHTML;
user.innerHTML =  fixed_user.replace("@purdue.edu", "");

function validateSearch() {
  var search_bar = document.getElementById("search_bar");
  search_bar_form = document.getElementById("search_bar_form");
  var regex = new RegExp("^[C|c][S|s]\s?1800{0,3}$");
  if (search_bar.value.match(regex) != null) {
    search_bar_form.action = "CS18000"
    return true;
  }
  regex = new RegExp("^[C|c][S|s]\s?2520{0,3}$");
  if (search_bar.value.match(regex) != null) {
    search_bar_form.action = "CS25200"
    return true;
  }
  alert("Sorry we could not find the class you are looking for.\nCheck out CS 180 or CS252");
  return false;
}
