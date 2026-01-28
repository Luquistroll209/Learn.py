<script>
	import Header from './navbar.svelte';
	import '../app.css';
	import '$lib/style/footer.css';

	/** @type {{children: import('svelte').Snippet}} */
	let { children } = $props();
</script>

<div class="app">
	<Header />

	<main>
		{@render children()}
	</main>
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
	<footer class="page-footer">
	<div class="footer-content">
		<div class="footer-section">
		<h3 class="footer-title">Learn.py</h3>
		<p class="footer-tagline">Organizarse y aprender digitalmente</p>
		</div>
		
		<div class="footer-section">
		<h4 class="footer-subtitle">Enlaces rápidos</h4>
		<div class="footer-links">
			<a href="/privacidad">Privacidad</a>
			<a href="/tos">Términos</a>
			<a href="/soporte">Soporte</a>

		</div>
		</div>
		
		<div class="footer-section">
		<h4 class="footer-subtitle">Síguenos</h4>
		<div class="social-links">
			<a href="https://github.com/Luquistroll209/Learn.py" target="_blank" rel="noopener" aria-label="GitHub">
			<i class="fab fa-github"></i>
			</a>
			<a href="https://twitter.com" target="_blank" rel="noopener" aria-label="Twitter">
			<i class="fab fa-twitter"></i>
			</a>
			<a href="https://instagram.com" target="_blank" rel="noopener" aria-label="Instagram">
			<i class="fab fa-instagram"></i>
			</a>
			<a href="https://youtube.com" target="_blank" rel="noopener" aria-label="YouTube">
			<i class="fab fa-youtube"></i>
			</a>
			<a href="https://linkedin.com" target="_blank" rel="noopener" aria-label="LinkedIn">
			<i class="fab fa-linkedin"></i>
			</a>
		</div>
		</div>
		
		<div class="footer-section">
		<h4 class="footer-subtitle">Contacto</h4>
		<p class="contact-info">
			<i class="fas fa-envelope"></i> luquistroll@gmail.com<br>
		</p>
		</div>
	</div>
	
	<div class="footer-bottom">
		<p>© 2026 Learn.py - Todos los derechos reservados</p>
		<p class="footer-copyright">Hecho con <i class="fas fa-heart"></i> para la comunidad</p>
	</div>
	</footer>
</div>

