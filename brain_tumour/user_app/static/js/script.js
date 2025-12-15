function validatePassword() {
 
    var email = document.getElementById("id_email").value;
    var password = document.getElementById("id_password").value;
    var phone = document.getElementById("id_phone").value;
    var confirmPassword = document.getElementById("id_confirm_password").value;
    var image = document.getElementById("id_image").files[0];
  
    // Email validation
    var requiredLetters = /[gmail]/i;
    if (!requiredLetters.test(email)) {
      alert("Email must contain at least one of the following letters: 'g','m', 'a', 'i', 'l'");
      return false; // Prevent form submission
    }
  
    // Phone number validation (e.g., 10 digits)
    var phonePattern = /^\d{10}$/;
    if (!phonePattern.test(phone)) {
      alert("Invalid phone number format! Must be 10 digits.");
      return false; // Prevent form submission
    }
  
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return false; // Prevent form submission
    }
  
    // Image file validation
    if (!image) {
      alert("Please upload an image.");
      return false; // Prevent form submission
    }
  
    return true; // Allow form submission
  }
  

//   toggle
function togglePassword() {
    var passwordField = document.querySelector('.pswd');
    var passwordFieldType = passwordField.getAttribute('type');
    var toggleIcon = document.getElementById('togglePasswordIcon');
    if (passwordFieldType === 'password') {
        passwordField.setAttribute('type', 'text');
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordField.setAttribute('type', 'password');
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

function toggleConfirmPassword() {
    var confirmPasswordField = document.getElementById('id_confirm_password');
    var confirmPasswordFieldType = confirmPasswordField.getAttribute('type');
    var toggleIcon = document.getElementById('toggleConfirmPasswordIcon');
    if (confirmPasswordFieldType === 'password') {
        confirmPasswordField.setAttribute('type', 'text');
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        confirmPasswordField.setAttribute('type', 'password');
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}