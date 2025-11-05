<script>
	import { page } from '$app/state';
	import logo from '$lib/images/svelte-logo.svg';
	import github from '$lib/images/github.svg';
</script>
<nav class="navbar">
        <div class="navbar-brand">
            <div class="logo">E</div>
            <span class="brand-name">Learn.py</span>
        </div>
        
        <ul class="navbar-nav">
            <li class="nav-item">
                <a href="/" class="nav-link">Home</a>
            </li>
            <li class="nav-item">
                <a href="/about" class="nav-link">About</a>
            </li>
            <li class="nav-item">
                <a href="/sverdle" class="nav-link">Sverdle</a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">Tareas</a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">Calificaciones</a>
            </li>
        </ul>
        
        <div class="navbar-actions">
            <div class="icon-button">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
                </svg>
            </div>
            <div class="icon-button">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.37 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.64 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
                </svg>
            </div>
            <div class="user-profile">
                <div class="avatar">JD</div>
                <span class="username">Juan Díaz</span>
            </div>
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
<style>
        :root {
            --primary-color: #1a73e8;
            --primary-dark: #0d47a1;
            --text-color: #202124;
            --text-light: #5f6368;
            --background: #ffffff;
            --background-hover: #f8f9fa;
            --border-color: #dadce0;
            --shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }

        body {
            background-color: #f8f9fa;
            color: var(--text-color);
            padding: 20px;
        }

        .navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: var(--background);
            padding: 0 16px;
            height: 64px;
            box-shadow: var(--shadow);
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: var(--primary-color);
            color: white;
            border-radius: 6px;
            font-weight: bold;
            font-size: 18px;
        }

        .brand-name {
            font-size: 20px;
            font-weight: 500;
            color: var(--text-color);
        }

        .navbar-nav {
            display: flex;
            align-items: center;
            list-style: none;
            height: 100%;
        }

        .nav-item {
            position: relative;
            height: 100%;
            display: flex;
            align-items: center;
        }

        .nav-link {
            display: flex;
            align-items: center;
            height: 100%;
            padding: 0 16px;
            color: var(--text-light);
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s ease;
            position: relative;
        }

        .nav-link:hover {
            color: var(--primary-color);
            background-color: var(--background-hover);
        }

        .nav-link.active {
            color: var(--primary-color);
        }

        .nav-link.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: var(--primary-color);
            border-radius: 3px 3px 0 0;
        }

        .navbar-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .user-profile {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .user-profile:hover {
            background-color: var(--background-hover);
        }

        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background-color: var(--primary-color);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 500;
            font-size: 14px;
        }

        .username {
            font-size: 14px;
            color: var(--text-color);
        }

        .icon-button {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background-color 0.2s;
            color: var(--text-light);
        }

        .icon-button:hover {
            background-color: var(--background-hover);
            color: var(--primary-color);
        }

        .demo-content {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        h1 {
            margin-bottom: 16px;
            color: var(--text-color);
        }

        p {
            line-height: 1.6;
            color: var(--text-light);
            margin-bottom: 16px;
        }

        @media (max-width: 768px) {
            .navbar {
                padding: 0 12px;
            }
            
            .brand-name {
                display: none;
            }
            
            .nav-link {
                padding: 0 12px;
                font-size: 13px;
            }
            
            .username {
                display: none;
            }
        }
    </style>
