<script>
	import Header from './navbar.svelte';
	import '../app.css';

	/** @type {{children: import('svelte').Snippet}} */
	let { children } = $props();
</script>

<div class="app">
	<Header />

	<main>
		{@render children()}
	</main>

	<div class="page-footer">
		<p>© 2024 Learn.py - Todos los derechos reservados</p>
		<div class="footer-links">
			<a href="/privacy">Privacidad</a>
			<a href="/terms">Términos</a>
			<a href="/">Sobre Nosotros</a>
		</div>
	</div>
</div>

<style>
	.page-footer {
		margin-top: 50px;
		padding-top: 20px;
		border-top: 1px solid var(--border-color);
		text-align: center;
		color: var(--text-light);
	}
	
	.footer-links {
		display: flex;
		justify-content: center;
		gap: 20px;
		margin-top: 15px;
		flex-wrap: wrap;
	}
	
	.footer-links a {
		color: var(--text-light);
		text-decoration: none;
		font-size: 0.9rem;
	}
	
	.footer-links a:hover {
		color: var(--primary-color);
		text-decoration: underline;
	}
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}
/*
	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}
*/
	footer {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 12px;
	}

	footer a {
		font-weight: bold;
	}

	@media (min-width: 480px) {
		footer {
			padding: 12px 0;
		}
	}
</style>
