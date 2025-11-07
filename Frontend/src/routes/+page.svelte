<script>
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';
	import '$lib/style/PrincipalPage.css'
</script>

<svelte:head>
	<title>Learn.py</title>
	<meta name="description" content="Learn.py" />
</svelte:head>

<section class="welcome-container">
        <h1 class="welcome-title">Bienvenido a <span class="welcome-highlight">Learn.py</span></h1>
        
        <p class="welcome-subtitle">
            La plataforma educativa moderna que combina la potencia de Django y Svelte con una interfaz intuitiva 
            para revolucionar la experiencia de aprendizaje en escuelas.
        </p>
        
        <div class="welcome-features">
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3 class="feature-title">Gestión Inteligente</h3>
                <p class="feature-description">
                    Organiza clases, materiales y recursos educativos de forma eficiente con nuestro 
                    sistema basado en las mejores prácticas de Moodle y Classroom.
                </p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">Seguimiento Académico</h3>
                <p class="feature-description">
                    Sistema completo de tareas, calificaciones y seguimiento del progreso estudiantil 
                    con análisis detallados y reportes automáticos.
                </p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">🤝</div>
                <h3 class="feature-title">Comunicación Integrada</h3>
                <p class="feature-description">
                    Canal de comunicación directo entre profesores y estudiantes con notificaciones 
                    en tiempo real y transferencia segura de archivos.
                </p>
            </div>
        </div>
        
        <div class="cta-section">
            <h3 class="cta-title">¿Listo para comenzar?</h3>
            <p class="cta-description">
                Únete a la revolución educativa. Learn.py está diseñado para facilitar la enseñanza 
                y el aprendizaje tanto en modalidad presencial como a distancia.
            </p>
            
            <div class="cta-buttons">
                <a href="/login" class="btn btn-primary">Registrarse</a>
            </div>
        </div>
        
        <div class="tech-stack">
            <h4 class="tech-title">Desarrollado con tecnología moderna</h4>
            <div class="tech-icons">
                <div class="tech-icon">
                    <div class="icon">D</div>
                    <span>Django</span>
                </div>
                <div class="tech-icon">
                    <div class="icon">S</div>
                    <span>Svelte</span>
                </div>
                <div class="tech-icon">
                    <div class="icon">S</div>
                    <span>SQLite</span>
                </div>
                <div class="tech-icon">
                    <div class="icon">P</div>
                    <span>Python</span>
                </div>
            </div>
        </div>
    </section>

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 0.6;
	}

	h1 {
		width: 100%;
	}

	.welcome {
		display: block;
		position: relative;
		width: 100%;
		height: 0;
		padding: 0 0 calc(100% * 495 / 2048) 0;
	}

	.welcome img {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		display: block;
	}
</style>
