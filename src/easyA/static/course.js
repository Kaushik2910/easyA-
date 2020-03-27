if (userID.value == "user") {
  var user = document.getElementById("user");
  var fixed_user = user.innerHTML;
  user.innerHTML =  fixed_user.replace("@purdue.edu", "");
}

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
  search_bar_form.action = course;

  return true;
}

function validateRequest() {
  var user = document.getElementById("userID");
  if (userID.value == "guest") {
    alert("You have to log in first");
    return false;
  }
  return true;
}

function filter_reviews() {
  var prof_checks = document.getElementsByClassName("prof_check");
  var profs = [];
  for (var i = 0; i < prof_checks.length; i++) {
    if (prof_checks[i].checked) {
      profs.push(prof_checks[i].value);
    }
  }
  var tag_checks = document.getElementsByClassName("tag_check");
  var tags = [];
  for (var i = 0; i < tag_checks.length; i++) {
    if (tag_checks[i].checked) {
      tags.push(tag_checks[i].value);
    }
  }
  var reviews = document.getElementsByClassName("review_li");
  for (var i = 0; i < reviews.length; i++) {
    var review_prof = reviews[i].getElementsByClassName("review-professor")[0].innerText.replace("Professor: ", "");
    var prof_filter = profs.length == 0 || profs.includes(review_prof);

    var review_tags_obj = reviews[i].getElementsByClassName("review_tag");
    var review_tags = [];
    for (var j = 0; j < review_tags_obj.length; j++) {
      review_tags.push(review_tags_obj[j].innerText);
    }

    var tags_filter = false;
    if (tags.length == 0) {
      tags_filter = true;
    } else {
      for (var j = 0; j < review_tags.length; j++) {
        tags_filter = tags_filter || tags.includes(review_tags[j]);
      }
    }

    if (prof_filter && tags_filter) {
      reviews[i].style.display = "block";
    } else {
      reviews[i].style.display = "none";
    }
  }
}

var checkboxes = document.getElementsByClassName("filter_check");

for (var i = 0; i < checkboxes.length; i++) {
  checkboxes[i].addEventListener( 'change', filter_reviews);
}
