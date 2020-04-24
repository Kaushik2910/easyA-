
var userID = document.getElementById("userID");

if (userID.value == "user" || userID.value == "admin" || userID.value == "banned") {
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

function validateTranslate(post) {
  var translation = document.getElementById(post).getElementsByClassName("translation")[0];
  if (translation.textContent == null || translation.textContent == "") {
    return true;
  }
  $(translation).toggle();
  return false;
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
    var text_search = document.getElementById("text_search").value.toLowerCase();
    var review_body = reviews[i].getElementsByClassName("review-body")[0].innerText.toLowerCase();
    var text_check = review_body.includes(text_search);

    if (prof_filter && tags_filter && text_check) {
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

document.getElementById("text_search").addEventListener( 'input', filter_reviews);

var sort_btns = document.getElementsByClassName("sort_btn");
var sort_input = document.getElementById("sort_input");
var sort_form = document.getElementById("sort_form");
for (var i = 0; i < sort_btns.length; i++) {
  sort_btns[i].onclick = function(){
    sort_input.value = this.id;
    sort_form.submit();
  };
}

var votes = document.getElementsByClassName("review-votes");

for (var i = 0; i < votes.length; i++) {
  votes[i].onclick = function(){
    var user_group = document.getElementById("userID").value;
    if (user_group == "banned" || user_group == "guest") {
      return;
    }
    var num = this.innerText;
    if (this.classList.contains("voted")) {
      num--;
    } else {
      num++;
    }
    var form = this.parentElement;
    var other_vote = null;
    if (this.classList.contains("upvote")) {
      this.innerHTML = "<i class='fas fa-arrow-up'></i> " + num;
      form.action = "/upvote";

      other_vote = form.getElementsByClassName("downvote")[0];

      if (other_vote.classList.contains("voted")) {
        var num_next = other_vote.innerText;
        num_next--;
        other_vote.innerHTML = "<i class='fas fa-arrow-down'></i> " + num_next;
        other_vote.classList.remove("voted");
      }
    } else {
      this.innerHTML = "<i class='fas fa-arrow-down'></i> " + num;
      form.action = "/downvote";
      other_vote = form.getElementsByClassName("upvote")[0];
      if (other_vote.classList.contains("voted")) {
        var num_next = other_vote.innerText;
        num_next--;
        other_vote.innerHTML = "<i class='fas fa-arrow-up'></i> " + num_next;
        other_vote.classList.remove("voted");
      }
    }

    this.classList.toggle("voted");

    form.addEventListener('submit', function(){
      event.preventDefault();
      var vote_input = form.getElementsByClassName("vote_input")[0];
      var sort_input = form.getElementsByClassName("sort_input")[0];
      $.ajax({
        data:{
          post_ID: vote_input.value,
          sort: sort_input.value
        },
        type: "POST",
        url: form.action,
      });

    });
    if (other_vote != null) {
      other_vote.setAttribute('disabled', 'disabled');
      setTimeout(function(){other_vote[i].removeAttribute('disabled');}, 500);
    }
    votes[i].setAttribute('disabled', 'disabled');
    setTimeout(function(){votes[i].removeAttribute('disabled');}, 500);
  }
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
  search_bar_form.action = course;

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
        search_bar_form.action = disp_sugs[i].getElementsByTagName("p")[0].innerText;
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


// var rating_link = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=Purdue+University+-+West+Lafayette&schoolID=783&query="
// var profs_divs = document.getElementsByClassName("professor_div");
// var prof_name;
// for (var i = 0; i < profs_divs.length; i++) {
//   prof_name = profs_divs[i].getElementsByClassName("review-professor")[0].innerText.replace("Professor: ","");
//   prof_name = prof_name.replace(/ /g,"+");
//   profs_divs[i].getElementsByTagName("a")[0].href = rating_link + prof_name;
// }

var year;
var month;
var day;
var date = $(".review-date");
for (var i = 0; i < date.length; i++) {
  year = date[i].innerText.substring(0, 4);
  switch (parseInt(date[i].innerText.substring(5, 7))) {
    case 1:
    month = "January";
    break;
    case 2:
    month = "February";
    break;
    case 3:
    month = "March";
    break;
    case 4:
    month = "April";
    break;
    case 5:
    month = "May";
    break;
    case 6:
    month = "June";
    break;
    case 7:
    month = "July";
    break;
    case 8:
    month = "August";
    break;
    case 9:
    month = "September";
    break;
    case 10:
    month = "October";
    break;
    case 11:
    month = "November";
    break;
    case 12:
    month = "December";
    break;
  }
  day = date[i].innerText.substring(8, 10);
  switch (parseInt(day) % 10) {
    case 1:
      day += "<sup>st</sup>";
      break;
    case 2:
      day += "<sup>nd</sup>";
      break;
    case 3:
      day += "<sup>rd</sup>";
      break;
    default:
    day += "<sup>th</sup>";
  }
  date[i].innerHTML = month + ' ' + day + ', ' + year;
}

function myPost() {
  var btn = document.getElementById("my_post_btn");
  var reviews = document.getElementsByClassName("review_li");
  for (var i = 0; i < reviews.length; i++) {
    if (reviews[i].getElementsByClassName("my_post").length == 1) {
      reviews[i].style.display = "block";
    } else {
      reviews[i].style.display = "none";
    }
  }
  $("#all_reviews").show();
  $("#filter").hide();
  $("#text_search").hide();
}

function allPosts() {
  $("#all_reviews").hide();
  $(".review_li").show();
  $("#filter").show();
  $("#text_search").show();
}

function newReview(course_id){
  if (document.getElementsByClassName("my_post").length == 0) {
    window.location.href = '/course/' + course_id + '/new_review';
  } else {
    $('#review_modal').modal('toggle');
    if (document.getElementById("my_post_btn").innerText == "My Review") {
      myPost();
    }
  }
}

window.onresize = function() {
  $("#reviews_ul").css("marginTop", $("#class-header").height() * 1.02 + "px");
}

window.onscroll = function() {
  if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
    $(".scroll_hide").hide();
    $("#logo").css("fontSize", "2rem");
    $("#text_search").hide();
    $("#review_button").css("width", "auto");
    $("#review_button").css("padding", "2px 3px");

    if (screen.width < 600) {
      $("#row2 h1").css("fontSize", "2rem");
      $("#review_button").css("fontSize", "0.8rem");
    } else {
      $("#row2 h1").css("fontSize", "2.5rem");
    }


  } else {
    $(".scroll_hide").show();
    $("#text_search").show();
    $("#logo").css("fontSize", "3rem");
    $("#review_button").css("width", "80%");
    $("#review_button").css("padding", "");

    if (screen.width < 600) {
      $("#row2 h1").css("fontSize", "3rem");
      $("#review_button").css("fontSize", "1rem");
    } else {
      $("#row2 h1").css("fontSize", "6rem");
    }
  }
};

function shareable() {
  var query = document.URL.split('?',2)[1];
  if (query == null || query =="") {
    $("#all_reviews").hide();
    return;
  }

  if (document.getElementById(query) != null) {
    var reviews = document.getElementsByClassName("review_li");
    for (var i = 0; i < reviews.length; i++) {
      if (reviews[i].id == query) {
        reviews[i].style.display = "block";
      } else {
        reviews[i].style.display = "none";
      }
    }
    $("#filter").hide();
    $("#text_search").hide();
  }

}

window.addEventListener('load', function () {
  shareable();
  show_suggestions();
  $(".translation").hide();
  $("#reviews_ul").css("marginTop", $("#class-header").height() * 1.02 + "px");
})

function copyLinkHelper(course_id, post_id) {
  var shareLink = document.getElementById("shareLink");
  var url = document.URL.split('course',2)[0];
  url = url + 'course/' + course_id + '?' + post_id;
  shareLink.innerText = url;
}

function clipboard(){
  var shareLink = document.getElementById("shareLink");
  var tempInput = document.createElement("input");
  tempInput.value = shareLink.innerText;
  document.body.appendChild(tempInput);
  tempInput.select();
  document.execCommand("copy");
  document.body.removeChild(tempInput);
}

function speakLoud(postID) {
    var text = document.getElementById(postID + "-text");
    speechSynthesis.speak(new SpeechSynthesisUtterance(text.innerHTML));
}

function checkEmail(){
  var u_email = document.getElementById("u_email");
  let regex = new RegExp("[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+");
  if (u_email.value.match(regex) == null) {
    u_email.value += "@purdue.edu"
  }
}
