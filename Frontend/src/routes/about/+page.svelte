<script>
	import '$lib/style/PrincipalPage.css'
</script>

<svelte:head>
	<title>Sobre Nosotros - Learn.py</title>
	<meta name="description"content="Conoce nuestra misión, visión y el equipo detrás de Learn.py" />
</sveltehead>

<section class="welcome-container">
	<h1 class="welcome-title">Sobre <span class="welcome-highlight">Learn.py</span></h1>
	
	<p class="welcome-subtitle">
		Somos una empresa seria comprometida con revolucionar la educación digital, 
		creando puentes tecnológicos entre profesores y estudiantes para un aprendizaje 
		continuo, intuitivo y accesible 24/7.
	</p>
	
	<div class="welcome-features">
		<div class="feature-card">
			<div class="feature-icon">🎯</div>
			<h3 class="feature-title">Nuestra Misión</h3>
			<p class="feature-description">
				Facilitar la educación tanto presencial como a distancia mediante 
				una plataforma que centralice ejercicios, calificaciones y comunicación 
				en un solo lugar intuitivo y moderno.
			</p>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">🚀</div>
			<h3 class="feature-title">Nuestra Visión</h3>
			<p class="feature-description">
				Convertirnos en la plataforma educativa de referencia que conecte 
				profesores y estudiantes de forma eficiente, eliminando barreras 
				tecnológicas y geográficas en el proceso de aprendizaje.
			</p>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">❤️</div>
			<h3 class="feature-title">Nuestro Compromiso</h3>
			<p class="feature-description">
				Disponibilidad 24/7, interfaz intuitiva que no requiere capacitación 
				extensa, y un sistema robusto que garantiza la seguridad y privacidad 
				de todos los datos académicos.
			</p>
		</div>
	</div>
	
	<div class="cta-section">
		<h3 class="cta-title">¿Qué Hacemos Exactamente?</h3>
		<p class="cta-description">
			Desarrollamos una plataforma que integra lo mejor de Moodle y Classroom, 
			organizando clases, tareas y comunicaciones en una interfaz moderna. 
			Nuestro sistema permite:
		</p>
		
		<div class="welcome-features" style="margin-top: 20px; margin-bottom: 0;">
			<div class="feature-card" style="width: 100%; max-width: 350px;">
				<h3 class="feature-title">🎓 Gestión de Clases</h3>
				<p class="feature-description">
					Organización completa de materias, horarios y materiales educativos 
					en un entorno estructurado y fácil de navegar.
				</p>
			</div>
			
			<div class="feature-card" style="width: 100%; max-width: 350px;">
				<h3 class="feature-title">📝 Sistema de Tareas</h3>
				<p class="feature-description">
					Creación, entrega y calificación de ejercicios con fechas límite, 
					seguimiento automático y retroalimentación inmediata.
				</p>
			</div>
			
			<div class="feature-card" style="width: 100%; max-width: 350px;">
				<h3 class="feature-title">💬 Comunicación Directa</h3>
				<p class="feature-description">
					Canal de comunicación integrado con transferencia segura de archivos 
					y notificaciones en tiempo real para toda la comunidad educativa.
				</p>
			</div>
		</div>
	</div>
	
	<div class="cta-section" style="background: linear-gradient(135deg, #fff8e1, #ffecb3);">
		<h3 class="cta-title">Nuestro Enfoque Innovador</h3>
		<p class="cta-description">
			Learn.py nace de la necesidad de simplificar la educación digital. 
			No somos solo otra plataforma más; somos la solución que entiende que 
			la tecnología debe adaptarse a las necesidades educativas, no al revés.
		</p>
		<p class="cta-description" style="margin-top: 15px;">
			Trabajamos con instituciones educativas para crear un ecosistema donde 
			profesores puedan enseñar sin complicaciones tecnológicas y estudiantes 
			puedan aprender sin límites de tiempo o espacio.
		</p>
		
		<div class="cta-buttons">
			<a href="/contact" class="btn btn-primary">Contáctanos</a>
			<a href="/demo" class="btn btn-secondary">Ver Demo</a>
		</div>
	</div>
	
	<div class="tech-stack">
		<h4 class="tech-title">Impulsado por la Pasión por la Educación</h4>
		<p style="text-align: center; color: var(--text-light); margin-bottom: 20px; font-size: 0.9rem;">
			Learn.py es más que código y servidores; es el resultado de entender 
			las verdaderas necesidades del sector educativo y crear soluciones 
			que marquen la diferencia en el día a día de profesores y estudiantes.
		</p>
		<div class="tech-icons">
			<div class="tech-icon">
				<div class="icon">24/7</div>
				<span>Disponibilidad</span>
			</div>
			<div class="tech-icon">
				<div class="icon">🎓</div>
				<span>Educación</span>
			</div>
			<div class="tech-icon">
				<div class="icon">🤝</div>
				<span>Conexión</span>
			</div>
			<div class="tech-icon">
				<div class="icon">⚡</div>
				<span>Innovación</span>
			</div>
		</div>
	</div>
</section>