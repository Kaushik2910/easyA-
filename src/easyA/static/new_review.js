var user = document.getElementById("user");
var fixed_user = user.innerHTML;
user.innerHTML =  fixed_user.replace("@purdue.edu", "");

$("#date_input")[0].max = new Date().getFullYear();

var tag_arr = document.getElementsByClassName('tag');
var tags_input = document.getElementById("tags");

for (var i = 0; i < tag_arr.length; i++) {
  tag_arr[i].addEventListener("click", function(){
    if (this.classList.contains("active")) {
      tags_input.value = tags_input.value.replace(this.innerText+",", "");
    } else {
      tags_input.value += this.innerText+",";
    }
    this.classList.toggle("active");
});
}

var star_btns = document.getElementsByClassName('star_btn');

for (var i = 0; i < star_btns.length; i++) {
  star_btns[i].addEventListener("click", function(){
    var stars = document.getElementsByClassName('star');
    for (var j = 0; j < stars.length; j++) {
      if (j < this.id) {
        stars[j].classList.remove("far");
        stars[j].classList.add("fas");
      } else {
        stars[j].classList.remove("fas");
        stars[j].classList.add("far");
      }
    }
    document.getElementById("rating").value = this.id;
});
}

function show_suggestions(){
  var sugs = document.getElementsByClassName("prof_suggestion");
  var sug_number = 0;
  var prof_input = document.getElementById("professor_input").value.toLowerCase();
  if (prof_input == null) {
      prof_input = "";
  }

  for (var i = 0; i < sugs.length; i++) {
    var sug_text = sugs[i].innerText.toLowerCase();
    if (prof_input == "" || sug_number >= 3 || !sug_text.includes(prof_input)  ) {
      sugs[i].classList.remove("selected");
      $(sugs[i]).hide();
    } else {
      $(sugs[i]).show();
      sug_number++;
    }
  }
}

var prof_input = document.getElementById("professor_input");
prof_input.addEventListener("input", show_suggestions);

var sugs = document.getElementsByClassName("prof_suggestion_div");
for (var i = 0; i < sugs.length; i++) {
  var prof_p = sugs[i].getElementsByClassName("prof_suggestion")[0];
  sugs[i].onclick = function(){
    prof_input.value = prof_p.textContent;
    $(".prof_suggestion").hide();
  };
}

document.addEventListener("keydown",function(e){
  if (e.which != 40 && e.which != 38 && e.which != 13) {
    return;
  }
  var all_sugs = document.getElementsByClassName("prof_suggestion");
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
    event.preventDefault();
    var professor_input = document.getElementById("professor_input");
    var done = false;
    for (var i = 0; i < disp_sugs.length; i++) {
      if (disp_sugs[i].classList.contains("selected")) {
        disp_sugs[i].classList.remove("selected")
        professor_input.value = disp_sugs[i].innerText;
        break;
      }
    }
    if (!done) {
      professor_input.value = disp_sugs[0].innerText;
    }
    $(disp_sugs).hide()

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
});

window.onscroll = function() {
  if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
    $("#name").addClass("text-center");
    $("#row2 h2").hide();

    if (window.screen.width < 601) {
      $("#row1").removeClass("my-3 ");
      $("#name").css("fontSize", "3rem");
    }


  } else {
    $("#name").removeClass("text-center");
    $("#row2 h2").show();
    $("#row1").addClass("my-3");
    $("#name").css("fontSize", "4rem");

  }
};

window.onresize = function() {
  if (window.screen.width > 600) {
    $("#row1").addClass("my-3");
    $("#name").css("fontSize", "4rem");
  }
}
