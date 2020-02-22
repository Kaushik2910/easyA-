
function emailCheck(){
  var form = document.getElementById("signup_form");
  email = form.u_email.value;
  let regex = new RegExp("[^@ \t\r\n]+@purdue.edu");
  var emailHelp = document.getElementById("emailHelp");

  if (email.match(regex) == null) {
    if (email != "") {
      emailHelp.textContent = "You can only sign up with a Purdue email";
      form.u_password.classList.add("invalid_field");
    }
    return false;
  }
  emailHelp.textContent = "";
  return true;
}

function passwordCheck() {
  var form = document.getElementById("signup_form");
  password1 = form.u_password.value;
  password2 = form.u_password2.value;

  var pwdHelp = document.getElementById("pwdHelp");

  if (password1 == '') {
    pwdHelp.textContent = "Please enter a password";
    return false;
  } else if (password1.length < 6) {
    pwdHelp.textContent = "Your password is too short";
    return false;
  } else if (password2 == '') {
    pwdHelp.textContent = "Please confirm your password";
    return false;
  } else if (password1 != password2) {
    pwdHelp.textContent = "Password did not match: Please try again...";
    return false;
  }else{
    pwdHelp.textContent = "";
    return true;
  }
}
var inputs = document.getElementsByTagName("input");

for (var i = 0; i < inputs.length; i++) {
  inputs[i].addEventListener("change", function(){
    if (emailCheck() && passwordCheck()) {
      document.getElementById("signup_btn").disabled = false;
    } else {
      document.getElementById("signup_btn").disabled = true;
    }
  });
}
