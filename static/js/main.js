document.addEventListener("DOMContentLoaded", function() {
    const emailField = document.querySelector(".email-field");
    if(emailField.classList.contains("show")) {
        emailField.style.opacity = 0;
        setTimeout(() => {
            emailField.style.opacity = 1;
        }, 100);
    }
});
