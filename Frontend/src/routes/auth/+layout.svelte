<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';
    import '$lib/style/auth.css';

    let islogged = false;

    onMount(() => {
        checkAuthStatus();
    });

    function checkAuthStatus() {
        if (!browser) return;
        
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('userData');
        islogged = !!token;

        if (islogged) {
            // Redirigir a home si ya está logueado
            window.location.href = '/';
        }
    }
</script>

<svelte:head>
    <title>Autenticación - Learn.py</title>
    <meta name="description" content="Inicia sesión o regístrate en Learn.py" />
</svelte:head>

<Alert />

<div class="auth-page">
    <div class="auth-container">
        <slot />
    </div>
</div>