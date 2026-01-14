<script lang="ts">
    import { browser } from '$app/environment';
	//import { page } from '$app/state';
	//import logo from '$lib/images/svelte-logo.svg';
	import github from '$lib/images/github.svg';
	import logo from '$lib/images/logo.webp';
    import '$lib/style/navbar.css';
    import { onMount } from 'svelte';
    import { urlip } from '$lib/config';

    //componentes
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';

    let islogged = false;
    let username = "";
    let userInitials = "";

    let mobileMenuOpen = false;
    let userMenuOpen = false;
    let notificationsMenuOpen = false;

    //Detectar si es un movil o no para ajustar toda la interfaz
    let isSmallscreen = false

    // Notificaciones (datos de ejemplo)
    let unreadNotifications = 0;
    
    /*
    let notifications = [
        {
            id: 1,
            from: "De",
            subject: "Subject",
            message: "mensaje",
            time: "Hace 2 horas",
            read: false
        },
    ];
    */
   let notifications: any[] = [];
    
    if (browser) {
        isSmallscreen = window.innerWidth <= 1260;
        //console.log('Es pantalla pequeña:', isSmallscreen);
    }

    onMount(() => {
        checkAuthStatus();
        checkNotification();
        // Agregar listener para resize
        if (browser) {
            window.addEventListener('resize', handleResize);
        }
        
        return () => {
            if (browser) {
                window.removeEventListener('resize', handleResize);
            }
        };
    });

    function handleResize() {
        if (browser) {
            isSmallscreen = window.innerWidth <= 1260;
            //console.log('Es pantalla pequeña:', isSmallscreen);
            
            // Cerrar menús al cambiar tamaño de pantalla
            if (window.innerWidth > 768) {
                mobileMenuOpen = false;
                document.body.style.overflow = '';
            }
        }
    }
    async function checkNotification(){
        const token = localStorage.getItem('token');
        //unreadNotifications
        
        const respose = await fetch(`${urlip}notification/obtainNotifications/`, {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
            });

            const data = await respose.json();
            notifications = data.notifications;
            console.log(notifications);
            unreadNotifications = data.notifications.length;
            
            if (respose.ok){
                //a
            }/*else{
                showAlert("Error", "Error", "red");
            }*/
    }
    function checkAuthStatus() {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('userData');

        islogged = !!token;
        
        if (userData) {
            try {
                const user = JSON.parse(userData);
                username = `${user.name} ${user.last_name}`;
                userInitials = `${user.name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
            } catch(error) {

                console.log("error: ", error);
                localStorage.removeItem('userData');
                localStorage.removeItem('token');
                islogged = false;
            }
        } else {
            islogged = false;
            username = "";
            userInitials = "";
        }
    }
    
    function toggleMobileMenu(): void {
        mobileMenuOpen = !mobileMenuOpen;
        if (mobileMenuOpen) {
            userMenuOpen = false;
            notificationsMenuOpen = false;
            if (browser) {
                document.body.style.overflow = 'hidden';
            }
        } else {
            if (browser) {
                document.body.style.overflow = '';
            }
        }
    }

    function closeMobileMenu(): void {
        mobileMenuOpen = false;
        if (browser) {
            document.body.style.overflow = '';
        }
    }
    
    function handleNavLinkClick(): void {
        closeMobileMenu();
    }
    
    function toggleUserMenu(): void {
        userMenuOpen = !userMenuOpen;
        if (userMenuOpen) {
            mobileMenuOpen = false;
            notificationsMenuOpen = false;
            if (browser) {
                document.body.style.overflow = '';
            }
        }
    }

    function closeUserMenu(): void {
        userMenuOpen = false;
    }

    function toggleNotificationsMenu(): void {
        notificationsMenuOpen = !notificationsMenuOpen;
        if (notificationsMenuOpen) {
            mobileMenuOpen = false;
            userMenuOpen = false;
            if (browser) {
                document.body.style.overflow = '';
            }
        }
    }

    function closeNotificationsMenu(): void {
        notificationsMenuOpen = false;
    }

    function markAsRead(notificationId: number): void {
        const notification = notifications.find(n => n.id === notificationId);
        if (notification && !notification.read) {
            notification.read = true;
            unreadNotifications = Math.max(0, unreadNotifications - 1);
        }
    }

    function markAllAsRead(): void {
        notifications.forEach(notification => {
            if (!notification.read) {
                notification.read = true;
            }
        });
        unreadNotifications = 0;
    }
</script>

<svelte:head>
	<title>Learn.py</title>
	<meta name="description" content="Learn.py" />
</svelte:head>

<Alert />

<!-- Overlay para móvil -->
<div class="mobile-overlay {mobileMenuOpen ? 'active' : ''}" role="button" tabindex="0" on:keydown={closeMobileMenu} on:click={closeMobileMenu}></div>

<nav class="navbar">
    <div class="navbar-brand">
        <a href="/" class="logo"><img src={logo} alt="Learn.py"></a>
        <a href="https://github.com/Luquistroll209/Learn.py" class="github-link">
            <img class="Github" src={github} alt="GitHub" />
        </a>
    </div>
    
    <ul class="navbar-nav {mobileMenuOpen ? 'active' : ''}">
        <li class="nav-item">
            <a href="/" class="nav-link active" on:click={handleNavLinkClick}>Inicio</a>
        </li>
        <li class="nav-item">
            <a href="/clases/" class="nav-link" on:click={handleNavLinkClick}>Clases</a>
        </li>
        {#if islogged} 
            <li class="nav-item">
                <a href="/clases/" class="nav-link" on:click={handleNavLinkClick}>Tareas</a>
            </li>
        {/if}
        <li class="nav-item">
            <a href="/soporte" class="nav-link" on:click={handleNavLinkClick}>Soporte</a>
        </li>
    </ul>
    
    <div class="navbar-actions">
        {#if islogged}    
            <button 
                type="button" 
                class="icon-button desktop-only"
                aria-label="Buscar"
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
                </svg>
            </button>
            
            <div class="notifications-container">
                <button 
                    type="button" 
                    class="icon-button desktop-only"
                    aria-label="Notificaciones"
                    on:click={toggleNotificationsMenu}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.37 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.64 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
                    </svg>
                    {#if unreadNotifications > 0}
                        <div class="notification-badge">{unreadNotifications}</div>
                    {/if}
                </button>
                
                {#if notificationsMenuOpen}
                    <div class="notifications-menu" role="menu" tabindex="0" on:mouseleave={closeNotificationsMenu}>
                        <div class="notifications-header">
                            <h3>Notificaciones</h3>
                            {#if unreadNotifications > 0}
                                <button class="mark-all-read" on:click={markAllAsRead}>Marcar todas como leídas</button>
                            {/if}

                        </div>
                        <a class="RedactButton" href="/notifications">Redactar</a>
                        <div class="notifications-list">
                            {#each notifications as notification (notification.id)}
                                <div class="notification-item {notification.read ? 'read' : 'unread'}" role="button" tabindex="0" on:keydown={() => markAsRead(notification.id)} on:click={() => markAsRead(notification.id)}>
                                    <div class="notification-from">{notification.from}</div> <!--Esto no funciona tengo que cambiar el backend-->
                                    <div class="notification-subject">{notification.subject}</div>
                                    <div class="notification-message">{notification.message}</div>
                                    <div class="notification-time">{notification.created_at}</div>
                                    {#if !notification.read}
                                        <div class="notification-dot"></div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                        {#if notifications.length === 0}
                            <div class="no-notifications">No hay notificaciones</div>
                        {/if}
                    </div>
                {/if}
            </div>
            
            <button 
                type="button" 
                class="user-profile"
                aria-label="Perfil de usuario"
                on:click={toggleUserMenu}
            >
                <div class="avatar">{userInitials}</div>
                <span class="username desktop-only">{username}</span>
            </button>
            
            {#if userMenuOpen}
                <div class="user-menu" role="menu" tabindex="0" on:mouseleave={closeUserMenu}>
                    <button class="user-menu-item">Ajustes de perfil</button>
                    <a class="user-menu-item" href="/clases/">Mis clases</a>
                    <button class="user-menu-item" on:click={() => {
                        localStorage.clear();
                        islogged = false;
                        closeUserMenu();
                        window.location.reload();
                    }}>Cerrar sesión</button>
                </div>
            {/if}
        {:else}
            {#if isSmallscreen == false}
                <div class="auth-buttons desktop-only">
                    <a href="/auth/login" class="auth-btn btn-login">
                        Iniciar Sesión
                    </a>
                    <a 
                        href="/auth/register"
                        class="auth-btn btn-register">
                        Registrarse
                    </a>
                </div>
            {/if}
        {/if}
        
        <!-- Botón hamburguesa -->
        <button 
            type="button"
            class="menu-toggle"
            class:active={mobileMenuOpen}
            on:click={toggleMobileMenu}
            aria-label="Menú"
            aria-expanded={mobileMenuOpen}
        >
            <span></span>
            <span></span>
            <span></span>
        </button>
    </div>
</nav>

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