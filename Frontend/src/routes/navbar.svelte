<script lang="ts">
    import { browser } from '$app/environment';
	//import { page } from '$app/state';
	//import logo from '$lib/images/svelte-logo.svg';
	import github from '$lib/images/github.svg';
    import '$lib/style/navbar.css';
    import { urlip } from '$lib/config';
    import { onMount } from 'svelte';

    //modulos
    import AlertModule from './modules/alert.svelte';

    let islogged = false;
    let username = "";
    let userInitials = "";

    let authPanelOpen: boolean = false;
    let authType: 'login' | 'register' = 'login';


    function alerts(title, description, color) {
        if (!browser) return; // evita ejecución en el servidor

        const titleDiv = document.getElementById("ErrorTitle");
        const descDiv = document.getElementById("ErrorDescription");
        const AlertModule = document.getElementById("AlertModule");

        if (descDiv) {
            descDiv.innerHTML = description;
        }
        if (titleDiv && AlertModule) {
            titleDiv.innerHTML = title;
            switch (color){
                case "error":
                    AlertModule.style.borderLeftColor = "red"; 
                case "warning":
                    AlertModule.style.borderLeftColor = "yellow"; 
                case "anoucement":
                    AlertModule.style.borderLeftColor = "blue"; 

            }
            //NO FUNCA LOS COLORESSSS
            AlertModule.style.right = "60px";
        }



    }

    // ejemplo de uso Para el futuro
    alerts("Error", "Tomas fue baneado de la vida", "error");


    function checkAuthStatus(){
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('userData');

        islogged = !!token;
        
        if (userData){
            try{
                
                const user = JSON.parse(userData);
                username = `${user.name} ${user.last_name}`;
                userInitials = `${user.name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
            }catch(error){
                console.log("error: ", error)
            }
        }
    }
    
    onMount(() => {
        checkAuthStatus();
    });
    
    function openAuthPanel(type: 'login' | 'register'): void {
        authType = type;
        authPanelOpen = true;
        document.body.style.overflow = 'hidden';
    }
    
    function closeAuthPanel(): void {
        authPanelOpen = false;
        document.body.style.overflow = 'auto';
    }
    
    function switchAuthType(type: 'login' | 'register'): void {
        authType = type;
    }
    
    async function handleAuthSubmit(event: Event): Promise<void> {
        event.preventDefault();
        const form = event.target as HTMLFormElement;
        
        if (authType === 'login'){
            //Obetener el email y el password del panel de login
            //TENGO QUE REVISAR ESTO
            const email = (form.querySelector('#login-email') as HTMLInputElement).value;
            const password = (form.querySelector('#login-password') as HTMLInputElement).value;
            
            try{
                //el response (lo que le manda a la api el mensaje)
                const respose = await fetch(`${urlip}users/login/`, {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json' //cords
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password,
                    })
                });

                const data = await respose.json();
                if (respose.ok){
                    //Guardar cosas localmente en cache para que no tenga que hacer peticiones a la api
                    const userInfo = {
                        name: data.name || data.user?.name,
                        last_name: data.last_name || data.user?.last_name
                    };
                    localStorage.setItem('token', data.token || '');
                    localStorage.setItem('userData', JSON.stringify(userInfo));
                    localStorage.setItem('islogged', 'true');

                    username = `${userInfo.name} ${userInfo.last_name}`;
                    userInitials = `${userInfo.name.charAt(0)}${userInfo.last_name.charAt(0)}`.toUpperCase();
                    islogged = true;
                        
                    closeAuthPanel();
                }else{
                    console.error(`Error: ${data.detail || 'credenciales errorenas'}`)
                }
            } catch(error){
                console.error('error al conectarse con la API', error)
                //HACER MI PROPIO ALERT EN UN MODULO COMPARTIDO
            }
        } else {
            //declaración de las variables del formulario
            const name = (form.querySelector('#register-name') as HTMLInputElement).value;
            const lastName = (form.querySelector('#register-last-name') as HTMLInputElement).value;
            const email = (form.querySelector('#register-email') as HTMLInputElement).value;
            const password = (form.querySelector('#register-password') as HTMLInputElement).value;
            const confirm = (form.querySelector('#register-confirm') as HTMLInputElement).value;

            if (password != confirm){
                alert("Las contraseñas no coinciden");
                //hacer mi propio sistema de alertas
                return;
            }

            try{
                const response = await fetch(`${urlip}users/register/`, {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json' //cords
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
                    //Hacer propio sistema de alertas
                    alert('Cuenta creada correctamente');
                    switchAuthType('login');
                } else {
                    alert(`Error: ${data.detail || 'No se pudo crear la cuenta'}`);
                }
            } catch(error){
                console.error(error)
            }
        }
        
    }
    
    function handleKeydown(event: KeyboardEvent): void {
        if (event.key === 'Escape') {
            closeAuthPanel();
        }
    }
    
    function handleOverlayKeydown(event: KeyboardEvent): void {
        if (event.key === 'Enter' || event.key === ' ') {
            closeAuthPanel();
        }
    }
    
    function handleAuthLinkKeydown(event: KeyboardEvent, type: 'login' | 'register'): void {
        if (event.key === 'Enter' || event.key === ' ') {
            switchAuthType(type);
        }
    }
</script>

<svelte:head>
	<title>Learn.py</title>
	<meta name="description" content="Learn.py" />
</svelte:head>
<AlertModule />
<nav class="navbar">
    <!--<meta http-equiv="refresh" content="0; url=https://www.youtube.com/watch?v=xvFZjo5PgG0&list=RDxvFZjo5PgG0&start_radio=1">-->
        
        <div class="navbar-brand">
            <div class="logo">Learn.py</div>
            <a href="https://github.com/Luquistroll209/Learn.py"><img class="Github" src={github} alt="GitHub" /></a>
        </div>
        
        <ul class="navbar-nav">
            <li class="nav-item">
                <a href="/" class="nav-link active">Inicio</a>
            </li>
            <li class="nav-item">
                <a href="/about" class="nav-link">Sobre nosotros</a>
            </li>
            <li class="nav-item">
                <a href="/sverdle" class="nav-link">Entrar</a>
            </li>
        </ul>
        
        <div class="navbar-actions">
            <!--Comprueba si esta logeado o no para mostrar el login o el usuario-->
            {#if islogged}    
                <button 
                    type="button" 
                    class="icon-button"
                    aria-label="Buscar"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="">
                        <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
                    </svg>
                </button>
                <button 
                    type="button" 
                    class="icon-button"
                    aria-label="Notificaciones"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="">
                        <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.37 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.64 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
                    </svg>
                </button>
                <button 
                    type="button" 
                    class="user-profile"
                    aria-label="Perfil de usuario"
                >
                    <div class="avatar">{userInitials}</div>
                    <span class="username">{username}</span>
                </button>
            {:else}
                <div class="auth-buttons">
                <button type="button" class="auth-btn btn-login" 
                    on:click={() => openAuthPanel('login')}
                    on:keydown={(e) => e.key === 'Enter' && openAuthPanel('login')}>Iniciar Sesión</button>
                <button 
                    type="button" 
                    class="auth-btn btn-register" 
                    on:click={() => openAuthPanel('register')}
                    on:keydown={(e) => e.key === 'Enter' && openAuthPanel('register')}>Registrarse</button>
                </div>
            {/if}
        </div>
    </nav>

<!-- Panel de Login/Register -->
<div 
    class="auth-panel {authPanelOpen ? 'active' : ''}"
    role="dialog"
    aria-modal="true"
    aria-labelledby="auth-title"
    tabindex="0"
    on:keydown={handleKeydown}
>
    <div class="auth-container">
        <div class="auth-header">
            <h2 class="auth-title" id="auth-title">
                {authType === 'login' ? 'Iniciar Sesión' : 'Crear Cuenta'}
            </h2>
            <button 
                type="button"
                class="close-auth" 
                on:click={closeAuthPanel}
                on:keydown={(e) => e.key === 'Enter' && closeAuthPanel()}
                aria-label="Cerrar panel de autenticación"
            >
                ×
            </button>
        </div>
        
        <form class="auth-form" on:submit={handleAuthSubmit}>
            {#if authType === 'login'}
                <div>
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
                        <button 
                            type="button"
                            class="auth-switch-link" 
                            on:click={() => switchAuthType('register')}
                            on:keydown={(e) => handleAuthLinkKeydown(e, 'register')}
                        >
                            Regístrate aquí
                        </button>
                    </div>
                </div>
            {:else}
                <div>
                    <div class="form-group">
                        <label for="register-name" class="form-label">Nombre</label>
                        <input id="register-name" type="text" class="form-input" placeholder="Ej: Juan" required/>
                    </div>
                    <div class="form-group">
                        <label for="register-name" class="form-label">apellido</label>
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
                        <button 
                            type="button"
                            class="auth-switch-link" 
                            on:click={() => switchAuthType('login')}
                            on:keydown={(e) => handleAuthLinkKeydown(e, 'login')}
                        >
                            Inicia sesión aquí
                        </button>
                    </div>
                </div>
            {/if}
        </form>
    </div>
</div>

<div 
    class="auth-overlay {authPanelOpen ? 'active' : ''}" 
    on:click={closeAuthPanel}
    on:keydown={handleOverlayKeydown}
    role="button"
    tabindex="0"
    aria-label="Cerrar panel de autenticación"
></div>



<!--
<header>
	<div class="corner">
		<a href="https://svelte.dev/docs/kit">
			<img src={logo} alt="SvelteKit" />
		</a>
	</div>

	<nav>
		<svg viewBox="0 0 2 3" aria-hidden="true">
			<path d="M0,0 L1,2 C1.5,3 1.5,3 2,3 L2,0 Z" />
		</svg>
		<ul>
			<li aria-current={page.url.pathname === '/' ? 'page' : undefined}>
				<a href="/">Home</a>
			</li>
			<li aria-current={page.url.pathname === '/about' ? 'page' : undefined}>
				<a href="/about">About</a>
			</li>
			<li aria-current={page.url.pathname.startsWith('/sverdle') ? 'page' : undefined}>
				<a href="/sverdle">Sverdle</a>
			</li>
		</ul>
		<svg viewBox="0 0 2 3" aria-hidden="true">
			<path d="M0,0 L0,3 C0.5,3 0.5,3 1,2 L2,0 Z" />
		</svg>
	</nav>

	<div class="corner">
		<a href="https://github.com/sveltejs/kit">
			<img src={github} alt="GitHub" />
		</a>
	</div>
</header>
-->