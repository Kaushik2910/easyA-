var user = document.getElementById("user");
if (user != null) {
  user.innerHTML =  user.innerHTML.replace("@purdue.edu", "");
}


function validateSearch() {
  var search_bar = document.getElementById("search_bar");
  search_bar_form = document.getElementById("search_bar_form");
  var course = search_bar.value.toUpperCase().replace(/ /g,"");
  var sugs = document.getElementsByClassName("suggestion");
  course = sugs[0].getElementsByTagName("p")[0].innerText;
  for (var i = 1; i < sugs.length; i++) {
    if (sugs[i].classList.contains("selected")) {
      course = sugs[i].getElementsByTagName("p")[0].innerText;
      break;
    }
  }

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
  var search_str = document.getElementById("search_bar").value.toUpperCase().replace(/ /g, "");
  if (search_str == null) {
      search_str = "";
  }

  var error_btn = document.getElementById("no_class");
  var error_str = error_btn.innerText.toUpperCase();

  var sug_number = 0;

  for (var i = 0; i < sugs.length; i++) {
    var sug_text = sugs[i].getElementsByTagName("p")[0].innerText;
    if (!sug_text.includes(search_str) || sug_number >= 6 || search_str == "") {
      sugs[i].classList.remove("selected");
      sugs[i].setAttribute('style', 'display:none !important');
    } else if (!sugs[i].innerText.includes(error_str)) {
      sugs[i].style.display = "";
      sug_number++;
    }
  }

  var sbar = document.getElementById("cover");
  var sug_hr = document.getElementById("sug_hr");

  if (search_str == "") {
    error_btn.style.display = "none";
    sug_hr.style.display = "none";
  } else if (sug_number == 0) {
    error_btn.style.display = "";
    sug_hr.style.display = "none";
  } else {
    error_btn.style.display = "none";
    sug_hr.style.display = "";
  }
}

document.getElementById("search_bar").addEventListener("input", show_suggestions);


document.addEventListener("keydown",function(e){
  if (e.which != 40 && e.which != 38 && e.which != 13) {
    return;
  }
  var all_sugs = document.getElementsByClassName("suggestion");
  var disp_sugs = [];
  for (var i = 0; i < all_sugs.length; i++) {
    if (all_sugs[i].style.display == "") {
      disp_sugs.push(all_sugs[i]);
    }
  }
  if (disp_sugs.length == 0) {
    return;
  }
  if (e.which == 13) {
    for (var i = 0; i < disp_sugs.length; i++) {
      if (disp_sugs[i].classList.contains("selected")) {
        var search_bar_form = document.getElementById("search_bar_form");
        search_bar_form.action = "course/" + disp_sugs[i].getElementsByTagName("p")[0].innerText;
        search_bar_form.submit();
      }
    }

  } else if (e.which == 40) {
    for (var i = 0; i < disp_sugs.length; i++) {
      if (disp_sugs[i].classList.contains("selected")) {
        disp_sugs[i].classList.remove("selected");
        disp_sugs[(i + 1) % disp_sugs.length].classList.add("selected");
        return;
      }
    }
    disp_sugs[0].classList.add("selected");
  } else {
    for (var i = disp_sugs.length - 1; i >= 0; i--) {
      if (disp_sugs[i].classList.contains("selected")) {
        disp_sugs[i].classList.remove("selected");
        disp_sugs[(i - 1 + disp_sugs.length) % disp_sugs.length].classList.add("selected");
        return;
      }
    }
    disp_sugs[disp_sugs.length - 1].classList.add("selected");
  }
})

function checkEmail(){
  var u_email = document.getElementById("u_email");
  let regex = new RegExp("[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+");
  if (u_email.value.match(regex) == null) {
    u_email.value += "@purdue.edu"
  }
}
