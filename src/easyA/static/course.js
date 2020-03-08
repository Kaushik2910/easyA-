var user = document.getElementById("user");
var fixed_user = user.innerHTML;
user.innerHTML =  fixed_user.replace("@purdue.edu", "");

function validateSearch() {
  var search_bar = document.getElementById("search_bar");
  search_bar_form = document.getElementById("search_bar_form");
  var course = search_bar.value.toUpperCase().replace(/ /g,"");

  var num = 0;
  var i = 0;
  for (; i < course.length; i++) {
    if(!isNaN(course.charAt(i))){
      num++;
    } else if (num > 0) {
      break;
    }
  }

  var temp = course.slice(i, course.length);
  course = course.slice(0, i);
  var padding = 5 - num;
  for (var j = 0; j < padding; j++) {
    course += "0";
  }
  course += temp;
  search_bar_form.action = "course/" + course;

  if (course == "CS18000" || course == "CS25200") {
    return true;
  }
  alert("Sorry we could not find the class you are looking for.\nCheck out CS 180 or CS252");
  return false;
}
