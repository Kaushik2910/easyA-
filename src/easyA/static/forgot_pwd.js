
function emailCheck(){
  var form = document.getElementById("forgot_pwd_form");
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
