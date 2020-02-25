
function emailCheck(){
  var form = document.getElementById("signup_form");
  email = form.u_email.value;
  let regex = new RegExp("[^@ \t\r\n]+@purdue.edu");
  var emailHelp = document.getElementById("emailHelp");

  if (email.match(regex) == null) {
    if (email != "") {
      emailHelp.textContent = "You can only sign up with a Purdue email";
    } else {
      emailHelp.textContent = "Please enter your Purdue email";
    }
    form.u_email.classList.add("invalid_field");
    return false;
  }
  emailHelp.textContent = "";
  form.u_email.classList.remove("invalid_field");
  return true;
}

function passwordCheck() {
  var form = document.getElementById("signup_form");
  password1 = form.u_password.value;
  password2 = form.u_password2.value;

  var pwdHelp = document.getElementById("pwdHelp");

  form.u_password.classList.remove("invalid_field");
  form.u_password2.classList.remove("invalid_field");

  if (password1 == '') {
    pwdHelp.textContent = "Please enter a password";
    form.u_password.classList.add("invalid_field");
    return false;
  } else if (password1.length < 6) {
    pwdHelp.textContent = "Your password is too short";
    form.u_password.classList.add("invalid_field");
    return false;
  } else if (password2 == '') {
    pwdHelp.textContent = "Please confirm your password";
    form.u_password2.classList.add("invalid_field");
    return false;
  } else if (password1 != password2) {
    pwdHelp.textContent = "Password did not match: Please try again...";
    form.u_password1.classList.add("invalid_field");
    form.u_password2.classList.add("invalid_field");
    return false;
  }else{
    pwdHelp.textContent = "";
    return true;
  }
}

function validateForm(){
  var email = emailCheck()
  var pwd = passwordCheck()
  return email && pwd;
}

// var submit_btn = document.getElementById("signup_btn");
//
// submit_btn.addEventListener("click", function(){
//   var email = emailCheck()
//   var pwd = passwordCheck()
//   if (email && pwd) {
//     document.getElementById("signup_form").submit;
//   }
// });
