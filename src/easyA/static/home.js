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

  return true;
}

function show_suggestions(){
  var sugs = document.getElementsByClassName("suggestion");
  var sug_number = 0;
  var search_bar = document.getElementById("search_bar");
  var search_str = search_bar.value.toUpperCase().replace(/ /g, "");
  if (search_str == null) {
      search_str = "";
  }

  var error_btn = document.getElementById("no_class");
  var error_str = error_btn.innerText.toUpperCase();
  for (var i = 0; i < sugs.length; i++) {
    if (!sugs[i].innerText.includes(search_str) || i >= 6 || search_str == "") {
      sugs[i].style.display = "none";
    } else if (!sugs[i].innerText.includes(error_str)) {
      sugs[i].style.display = "";
      sug_number++;
    }
  }
  
  var sug_div = document.getElementById('suggestions');
  var sbar = document.getElementById("cover");
  
  if (search_str == "" && sug_number == 0) {
    sug_div.style.display = "none";
    error_btn.style.display = "none";
    sbar.style.marginTop = "-1rem"
  } else if (sug_number == 0) {
    error_btn.style.display = "";
    sug_div.style.display = "";
    sbar.style.marginTop = "-1rem"
  } else {
    error_btn.style.display = "none";
    sug_div.style.display = "";
    sbar.style.marginTop = "-"+sug_number+"rem"
  }
}
