<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { urlip } from '$lib/config';
    import { showAlert } from '$lib/store/alertStore.js';
    

    onMount(() => {
        const token = localStorage.getItem('token');
        if (token) {
            window.location.href = '/';
        }
    });

    async function handleAuthSubmit(event: Event): Promise<void> {
        event.preventDefault();
        const form = event.target as HTMLFormElement;
        
        const email = (form.querySelector('#login-email') as HTMLInputElement).value;
        const password = (form.querySelector('#login-password') as HTMLInputElement).value;
        
        try{
            const respose = await fetch(`${urlip}users/login/`, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                })
            });

            const data = await respose.json();
            if (respose.ok){
                const userInfo = {
                    name: data.name || data.user?.name,
                    last_name: data.last_name || data.user?.last_name
                };
                localStorage.setItem('token', data.token || '');
                localStorage.setItem('userData', JSON.stringify(userInfo));
                localStorage.setItem('islogged', 'true');

                showAlert("Éxito", "Sesión iniciada correctamente", "blue");
                setTimeout(() => {
                    window.location.href = '/dashboard/';
                }, 1000);
            }else{
                showAlert("Error", "Credenciales erroneas", "red");
            }
        } catch(error){
            showAlert("Error", "No es posible conectarse con la base de datos", "red");
        }
    }
</script>

<svelte:head>
    <title>Iniciar Sesión - Learn.py</title>
</svelte:head>

<div class="auth-header">
    <a href="/" class="back-home">← Volver al inicio</a>
    <h1 class="auth-title">Iniciar Sesión</h1>
    <p class="auth-subtitle">Bienvenido de nuevo a Learn.py</p>
</div>

<form class="auth-form" on:submit={handleAuthSubmit}>
    <div class="form-group">
        <label for="login-email" class="form-label">Email</label>
        <input id="login-email" type="email" class="form-input" placeholder="Ej: tu@email.com" required/>
    </div>
    
    <div class="form-group">
        <label for="login-password" class="form-label">Contraseña</label>
        <input 
            id="login-password"
            type="password" 
            class="form-input" 
            placeholder="••••••••" 
            required
        />
    </div>
    
    <div class="form-options">
        <label class="remember-me">
            <input type="checkbox" /> Recordarme
        </label>
        <a href="#" class="forgot-password">¿Olvidaste tu contraseña?</a>
    </div>
    
    <button type="submit" class="btn-submit">Iniciar Sesión</button>
    
    <div class="auth-switch">
        <span class="auth-switch-text">¿No tienes una cuenta? </span>
        <a href="/auth/register" class="auth-switch-link">
            Regístrate aquí
        </a>
    </div>
</form>