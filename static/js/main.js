function togglePassword() {
    const passwordInput = document.getElementById("password");
    const icon = document.querySelector(".toggle-password");

    if (!passwordInput || !icon) return;

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        icon.textContent = "🙈";
    } else {
        passwordInput.type = "password";
        icon.textContent = "👁️";
    }
}





