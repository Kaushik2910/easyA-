
function validateForm() {
  var form = document.getElementById("reset_pwd_form");
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
