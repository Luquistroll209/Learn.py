<script lang="ts">
    import { onMount } from "svelte";
    import { browser } from "$app/environment";
    import { urlip } from "$lib/config";
    import { showAlert } from "$lib/store/alertStore.js";
    import { fetchWithRateLimit } from "$lib/utils/fetchWithRateLimit";

    onMount(() => {
        // Verificar si ya está logueado
        const token = localStorage.getItem("token");
        if (token) {
            window.location.href = "/";
        }
    });

    async function handleAuthSubmit(event: Event): Promise<void> {
        event.preventDefault();
        const form = event.target as HTMLFormElement;

        const name = (form.querySelector("#register-name") as HTMLInputElement)
            .value;
        const lastName = (
            form.querySelector("#register-last-name") as HTMLInputElement
        ).value;
        const email = (
            form.querySelector("#register-email") as HTMLInputElement
        ).value;
        const password = (
            form.querySelector("#register-password") as HTMLInputElement
        ).value;
        const confirm = (
            form.querySelector("#register-confirm") as HTMLInputElement
        ).value;

        if (password != confirm) {
            showAlert("Error", "Las contraseñas no coinciden", "red");
            return;
        }

        try {
            const response = await fetchWithRateLimit(
                `${urlip}users/register/`,
                {
                    method: "post",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                    },
                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password,
                        last_name: lastName,
                    }),
                },
            );
            const data = await response.json();

            if (response.ok) {
                const userInfo = {
                    name,
                    last_name: lastName,
                };
                localStorage.setItem("token", data.token || "");
                localStorage.setItem("userData", JSON.stringify(userInfo));
                localStorage.setItem("islogged", "true");

                showAlert("Éxito", "Cuenta creada correctamente", "blue");
                setTimeout(() => {
                    window.location.href = "/clases/";
                }, 1000);
            } else {
                // Extraer mensajes de error del backend
                let errorMessage = "No se pudo crear la cuenta";
                if (data.detail) {
                    errorMessage = data.detail;
                } else if (typeof data === "object") {
                    // Recorrer los campos del error (ej. email, password, name, last_name)
                    const errors = [];
                    for (const [field, messages] of Object.entries(data)) {
                        if (Array.isArray(messages)) {
                            errors.push(`${field}: ${messages.join(", ")}`);
                        } else if (typeof messages === "string") {
                            errors.push(`${field}: ${messages}`);
                        } else {
                            errors.push(JSON.stringify(messages));
                        }
                    }
                    if (errors.length > 0) {
                        errorMessage = errors.join("; ");
                    } else {
                        errorMessage = JSON.stringify(data);
                    }
                }
                showAlert("Error", errorMessage, "red");
            }
        } catch (error) {
            console.error(error);
            showAlert("Error", "Error de conexión con el servidor", "red");
        }
    }
</script>

<svelte:head>
    <title>Registrarse - Learn.py</title>
</svelte:head>

<div class="auth-header">
    <a href="/" class="back-home">← Volver al inicio</a>
    <h1 class="auth-title">Crear Cuenta</h1>
    <p class="auth-subtitle">Únete a la comunidad de Learn.py</p>
</div>

<form class="auth-form" on:submit={handleAuthSubmit}>
    <div class="form-group">
        <label for="register-name" class="form-label">Nombre</label>
        <input
            id="register-name"
            type="text"
            class="form-input"
            placeholder="Ej: Juan"
            required
        />
    </div>
    <div class="form-group">
        <label for="register-last-name" class="form-label">Apellido</label>
        <input
            id="register-last-name"
            type="text"
            class="form-input"
            placeholder="Ej: Pérez"
            required
        />
    </div>
    <div class="form-group">
        <label for="register-email" class="form-label">Email</label>
        <input
            id="register-email"
            type="email"
            class="form-input"
            placeholder="Ej: tu@email.com"
            required
        />
    </div>

    <div class="form-group">
        <label for="register-password" class="form-label">Contraseña</label>
        <input
            id="register-password"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
        />
    </div>

    <div class="form-group">
        <label for="register-confirm" class="form-label"
            >Confirmar Contraseña</label
        >
        <input
            id="register-confirm"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
        />
    </div>

    <div class="form-options">
        <label class="remember-me">
            <input type="checkbox" required />
            <a class="auth-switch-link" href="/tos"
                >Acepto los términos y condiciones</a
            >
        </label>
    </div>

    <button type="submit" class="btn-submit">Crear Cuenta</button>

    <div class="auth-switch">
        <span class="auth-switch-text">¿Ya tienes una cuenta? </span>
        <a href="/auth/login" class="auth-switch-link"> Inicia sesión aquí </a>
    </div>
</form>
