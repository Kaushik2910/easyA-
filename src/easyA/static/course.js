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
    var num = this.innerText;
    if (this.classList.contains("voted")) {
      num--;
    } else {
      num++;
    }
    var form = this.parentElement;
    if (this.classList.contains("upvote")) {
      this.innerHTML = "<i class='fas fa-arrow-up'></i> " + num;
      form.action = "/upvote";

      var other_vote = form.getElementsByClassName("downvote")[0];

      if (other_vote.classList.contains("voted")) {
        var num_next = other_vote.innerText;
        num_next--;
        other_vote.innerHTML = "<i class='fas fa-arrow-down'></i> " + num_next;
        other_vote.classList.toggle("voted");
      }
    } else {
      this.innerHTML = "<i class='fas fa-arrow-down'></i> " + num;
      form.action = "/downvote";
      var other_vote = form.getElementsByClassName("upvote")[0];
      if (other_vote.classList.contains("voted")) {
        var num_next = other_vote.innerText;
        num_next--;
        other_vote.innerHTML = "<i class='fas fa-arrow-up'></i> " + num_next;
        other_vote.classList.toggle("voted");
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
  }


}
