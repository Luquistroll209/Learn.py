<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { urlip } from '$lib/config';
    import { showAlert } from '$lib/store/alertStore.js';

    onMount(() => {
        // Verificar si ya está logueado
        const token = localStorage.getItem('token');
        if (token) {
            window.location.href = '/';
        }
    });

    async function handleAuthSubmit(event: Event): Promise<void> {
        event.preventDefault();
        const form = event.target as HTMLFormElement;
        
        const name = (form.querySelector('#register-name') as HTMLInputElement).value;
        const lastName = (form.querySelector('#register-last-name') as HTMLInputElement).value;
        const email = (form.querySelector('#register-email') as HTMLInputElement).value;
        const password = (form.querySelector('#register-password') as HTMLInputElement).value;
        const confirm = (form.querySelector('#register-confirm') as HTMLInputElement).value;

        if (password != confirm){
            showAlert("Error", "Las contraseñas no coinciden", "red");
            return;
        }

        try{
            const response = await fetch(`${urlip}users/register/`, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password,
                    last_name: lastName
                })
            });
            const data = await response.json();

            if (response.ok) {
                showAlert("Exito", "Cuenta creada correctamente", "blue");
                // Redirigir al login después de crear la cuenta
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 1500);
            } else {
                showAlert("Error", `${data.detail || 'No se pudo crear la cuenta'}`, "red");
            }
        } catch(error){
            console.error(error)
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
        <input id="register-name" type="text" class="form-input" placeholder="Ej: Juan" required/>
    </div>
    <div class="form-group">
        <label for="register-last-name" class="form-label">Apellido</label>
        <input id="register-last-name" type="text" class="form-input" placeholder="Ej: Pérez" required/>
    </div>
    <div class="form-group">
        <label for="register-email" class="form-label">Email</label>
        <input  id="register-email" type="email"  class="form-input"  placeholder="Ej: tu@email.com" required/>
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
        <label for="register-confirm" class="form-label">Confirmar Contraseña</label>
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
            <input type="checkbox" required /> Acepto los términos y condiciones
        </label>
    </div>
    
    <button type="submit" class="btn-submit">Crear Cuenta</button>
    
    <div class="auth-switch">
        <span class="auth-switch-text">¿Ya tienes una cuenta? </span>
        <a href="/auth/login" class="auth-switch-link">
            Inicia sesión aquí
        </a>
    </div>
</form>