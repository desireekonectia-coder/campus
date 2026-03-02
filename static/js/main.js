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


// Usamos una comprobación de seguridad (if) para evitar errores
const fechaNac = document.querySelector('input[name="fecha_nacimiento"]');
const campoTutor = document.querySelector('input[name="email_tutor"]');

// Solo ejecutamos el código si AMBOS elementos existen en la página actual
if (fechaNac && campoTutor) {
    fechaNac.addEventListener('change', () => {
        const edad = calcularEdad(fechaNac.value);
        if (edad < 18) {
            campoTutor.required = true;
            campoTutor.placeholder = "Obligatorio (Menor de edad)";
            campoTutor.style.border = "2px solid red"; // Opcional: aviso visual
        } else {
            campoTutor.required = false;
            campoTutor.placeholder = "Opcional";
            campoTutor.style.border = "1px solid #ccc";
        }
    });
}

// Nota: Asegúrate de tener la función calcularEdad definida, o usa esta:
function calcularEdad(fecha) {
    const hoy = new Date();
    const cumple = new Date(fecha);
    let edad = hoy.getFullYear() - cumple.getFullYear();
    const m = hoy.getMonth() - cumple.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < cumple.getDate())) {
        edad--;
    }
    return edad;
}

