var user = document.getElementById("user");
var fixed_user = user.innerHTML;
user.innerHTML =  fixed_user.replace("@purdue.edu", "");

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
