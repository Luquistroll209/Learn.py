<script lang="ts">
    import { browser } from "$app/environment";
    import github from "$lib/images/github.svg";
    import logo from "$lib/images/LearnPy.png";
    import "$lib/style/navbar.css";
    import { onMount } from "svelte";
    import { urlip } from "$lib/config";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import { showAlert } from "$lib/store/alertStore.js";
    import Alert from "$lib/components/alert.svelte";
    import { fetchWithRateLimit } from "$lib/utils/fetchWithRateLimit";
    import { rateLimitStore } from "$lib/store/rateLimitStore";

    let islogged = false;
    let username = "";
    let userInitials = "";

    let mobileMenuOpen = false;
    let userMenuOpen = false;
    let notificationsMenuOpen = false;
    let isSmallscreen = false;
    let unreadNotifications = 0;
    let notifications: any[] = [];

    let currentPath = "";
    const unsubscribe = page.subscribe((value) => {
        currentPath = value.url.pathname;
    });

    if (browser) {
        isSmallscreen = window.innerWidth <= 1260;
    }

    onMount(() => {
        checkAuthStatus();
        checkNotification();
        if (browser) {
            window.addEventListener("resize", handleResize);
        }

        return () => {
            if (browser) {
                window.removeEventListener("resize", handleResize);
            }
            unsubscribe();
        };
    });

    function handleResize() {
        if (browser) {
            isSmallscreen = window.innerWidth <= 1260;
            if (window.innerWidth > 768) {
                mobileMenuOpen = false;
                document.body.style.overflow = "";
            }
        }
    }

    async function checkNotification() {
        const token = localStorage.getItem("token");
        if (!token) return;

        try {
            const response = await fetchWithRateLimit(
                `${urlip}notification/obtainNotifications/`,
                {
                    method: "get",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                        authorization: `${token}`,
                    },
                },
            );

            if (response.status === 429) return;

            const data = await response.json();
            notifications = data.notifications;
            unreadNotifications = notifications.filter(
                (n) => !n.is_read,
            ).length;
        } catch (error) {
            console.error("Error fetching notifications:", error);
        }
    }

    function checkAuthStatus() {
        const token = localStorage.getItem("token");
        const userData = localStorage.getItem("userData");
        islogged = !!token;

        if (userData) {
            try {
                const user = JSON.parse(userData);
                username = `${user.name} ${user.last_name}`;
                userInitials =
                    `${user.name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
            } catch (error) {
                console.log("error: ", error);
                localStorage.removeItem("userData");
                localStorage.removeItem("token");
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
            if (browser) document.body.style.overflow = "hidden";
        } else {
            if (browser) document.body.style.overflow = "";
        }
    }

    function closeMobileMenu(): void {
        mobileMenuOpen = false;
        if (browser) document.body.style.overflow = "";
    }

    function handleNavLinkClick(): void {
        closeMobileMenu();
    }

    function toggleUserMenu(): void {
        userMenuOpen = !userMenuOpen;
        if (userMenuOpen) {
            mobileMenuOpen = false;
            notificationsMenuOpen = false;
            if (browser) document.body.style.overflow = "";
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
            if (browser) document.body.style.overflow = "";
        }
    }

    function closeNotificationsMenu(): void {
        notificationsMenuOpen = false;
    }

    async function markAsRead(notificationId: number): Promise<void> {
        const notification = notifications.find((n) => n.id === notificationId);
        if (notification && !notification.is_read) {
            notification.is_read = true;
            unreadNotifications = notifications.filter(
                (n) => !n.is_read,
            ).length;
        }
    }

    async function openNotification(notification: any) {
        if (!notification.is_read) await markAsRead(notification.id);
        closeNotificationsMenu();
        goto(`/notifications/noti-${notification.id}`);
    }

    async function markAllAsRead(): Promise<void> {
        for (const n of notifications) {
            if (!n.is_read) await markAsRead(n.id);
        }
    }

    function formatRelativeTime(dateString: string): string {
        const date = new Date(dateString);
        const now = new Date();
        const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
        if (diffSeconds < 60) return "Hace un momento";
        const diffMinutes = Math.floor(diffSeconds / 60);
        if (diffMinutes < 60)
            return `Hace ${diffMinutes} minuto${diffMinutes !== 1 ? "s" : ""}`;
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24)
            return `Hace ${diffHours} hora${diffHours !== 1 ? "s" : ""}`;
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays < 7)
            return `Hace ${diffDays} día${diffDays !== 1 ? "s" : ""}`;
        return date.toLocaleDateString();
    }

    function goTo(Go) {
        window.location.href = Go;
    }
</script>

<svelte:head>
    <title>Learn.py</title>
    <meta name="description" content="Learn.py" />
</svelte:head>

<Alert />

{#if $rateLimitStore.visible}
    <div class="rate-limit-overlay" on:click={rateLimitStore.hide}>
        <div class="rate-limit-popup" on:click|stopPropagation>
            <div class="rate-limit-header">
                <h3>Límite de peticiones alcanzado</h3>
                <button class="rate-limit-close" on:click={rateLimitStore.hide}
                    >×</button
                >
            </div>
            <div class="rate-limit-content">
                <div class="rate-limit-icon">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <div class="rate-limit-message">{$rateLimitStore.message}</div>
                {#if $rateLimitStore.remainingSeconds > 0}
                    <div class="rate-limit-wait">
                        Intenta de nuevo en {$rateLimitStore.remainingSeconds} segundo{$rateLimitStore.remainingSeconds !==
                        1
                            ? "s"
                            : ""}
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}

<!-- Overlay para móvil -->
<div
    class="mobile-overlay {mobileMenuOpen ? 'active' : ''}"
    role="button"
    tabindex="0"
    on:keydown={closeMobileMenu}
    on:click={closeMobileMenu}
></div>

<nav class="navbar">
    <div class="navbar-brand">
        <a href="/" class="logo"><img src={logo} alt="Learn.py" /></a>
        <a
            href="https://github.com/Luquistroll209/Learn.py"
            class="github-link"
        >
            <img class="Github" src={github} alt="GitHub" />
        </a>
    </div>

    <ul class="navbar-nav {mobileMenuOpen ? 'active' : ''}">
        <li class="nav-item">
            <a
                href="/"
                class="nav-link {currentPath === '/' ? 'active' : ''}"
                on:click={handleNavLinkClick}>Inicio</a
            >
        </li>
        <li class="nav-item">
            <a
                href="/clases/"
                class="nav-link {currentPath.startsWith('/clases')
                    ? 'active'
                    : ''}"
                on:click={handleNavLinkClick}>Clases</a
            >
        </li>
        {#if islogged}
            <li class="nav-item">
                <a
                    href="/clases/tareas/"
                    class="nav-link {currentPath.startsWith('/clases/tareas')
                        ? 'active'
                        : ''}"
                    on:click={handleNavLinkClick}>Tareas</a
                >
            </li>
        {/if}
        <li class="nav-item">
            <a
                href="/soporte"
                class="nav-link {currentPath.startsWith('/soporte')
                    ? 'active'
                    : ''}"
                on:click={handleNavLinkClick}>Soporte</a
            >
        </li>
        {#if !islogged}
            <div class="auth-buttons mobile-auth">
                <a href="/auth/login" class="auth-btn btn-login"
                    >Iniciar Sesión</a
                >
                <a href="/auth/register" class="auth-btn btn-register"
                    >Registrarse</a
                >
            </div>
        {/if}
    </ul>

    <div class="navbar-actions">
        {#if islogged}
            <div class="notifications-container">
                <button
                    type="button"
                    class="icon-button"
                    aria-label="Notificaciones"
                    on:click={toggleNotificationsMenu}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path
                            d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.37 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.64 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z"
                            fill="currentColor"
                        />
                    </svg>
                    {#if unreadNotifications > 0}
                        <div class="notification-badge">
                            {unreadNotifications}
                        </div>
                    {/if}
                </button>

                {#if notificationsMenuOpen}
                    <div
                        class="notifications-menu"
                        role="menu"
                        tabindex="0"
                        on:mouseleave={closeNotificationsMenu}
                    >
                        <div class="notifications-header">
                            <h3>Notificaciones</h3>
                            {#if unreadNotifications > 0}
                                <button
                                    class="mark-all-read"
                                    on:click={markAllAsRead}
                                    >Marcar todas como leídas</button
                                >
                            {/if}
                        </div>
                        <button
                            on:click={() => goto("/notifications")}
                            class="RedactButton">Redactar</button
                        >
                        <div class="notifications-list">
                            {#each notifications as notification (notification.id)}
                                <div
                                    class="notification-item {notification.is_read
                                        ? 'read'
                                        : 'unread'}"
                                    role="button"
                                    tabindex="0"
                                    on:keydown={(e) =>
                                        e.key === "Enter" &&
                                        openNotification(notification)}
                                    on:click={() =>
                                        openNotification(notification)}
                                >
                                    <div class="notification-from">
                                        {notification.created_by_info
                                            ?.username || "Sistema"}
                                    </div>
                                    <div class="notification-subject">
                                        {notification.subject}
                                    </div>
                                    <div class="notification-message">
                                        {notification.message}
                                    </div>
                                    <div class="notification-time">
                                        {formatRelativeTime(
                                            notification.created_at,
                                        )}
                                    </div>
                                    {#if !notification.is_read}
                                        <div class="notification-dot"></div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                        {#if notifications.length === 0}
                            <div class="no-notifications">
                                No hay notificaciones
                            </div>
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
                <div
                    class="user-menu"
                    role="menu"
                    tabindex="0"
                    on:mouseleave={closeUserMenu}
                >
                    <a class="user-menu-item" href="/clases/">Mis clases</a>
                    <button
                        class="user-menu-item"
                        on:click={() => {
                            localStorage.clear();
                            islogged = false;
                            closeUserMenu();
                            window.location.reload();
                        }}>Cerrar sesión</button
                    >
                </div>
            {/if}
        {:else if isSmallscreen == false}
            <div class="auth-buttons desktop-only">
                <a href="/auth/login" class="auth-btn btn-login"
                    >Iniciar Sesión</a
                >
                <a href="/auth/register" class="auth-btn btn-register"
                    >Registrarse</a
                >
            </div>
        {/if}

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
