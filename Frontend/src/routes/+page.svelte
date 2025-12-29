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
	<!-- Hero Section Mejorada -->
	<div class="hero-section">
		<h1 class="welcome-title">Transforma la Educación con <span class="welcome-highlight">Learn.py</span></h1>
		
		<p class="welcome-subtitle">
			La plataforma todo-en-uno que une a profesores y estudiantes en un entorno intuitivo, 
			disponible 24/7. Simplificamos la enseñanza y el aprendizaje, eliminando barreras tecnológicas.
		</p>
		
		<div class="hero-stats">
			<div class="stat">
				<div class="stat-number">24/7</div>
				<div class="stat-label">Disponibilidad</div>
			</div>
			<div class="stat">
				<div class="stat-number">⚡</div>
				<div class="stat-label">Intuitivo</div>
			</div>
			<div class="stat">
				<div class="stat-number">🔒</div>
				<div class="stat-label">Seguro</div>
			</div>
		</div>
	</div>
	
	<!-- Llamada a la acción inmediata -->
	<div class="quick-cta">
		<h3>¿Eres profesor o estudiante?</h3>
		<p>Comienza ahora sin complicaciones</p>
		<div class="cta-buttons">
			<a href="/auth?type=register&role=teacher" class="btn btn-primary">
				👨‍🏫 Soy Profesor
			</a>
			<a href="/auth?type=register&role=student" class="btn btn-secondary">
				🎓 Soy Estudiante
			</a>
			<a href="/demo" class="btn btn-outline">
				🎬 Ver Demo Gratis
			</a>
		</div>
	</div>
	
	<!-- Características Principales Mejoradas -->
	<div class="section-header">
		<h2>Todo lo que necesitas en un solo lugar</h2>
		<p>Diseñado pensando en la experiencia real del aula</p>
	</div>
	
	<div class="welcome-features">
		<div class="feature-card">
			<div class="feature-icon">🏫</div>
			<h3 class="feature-title">Gestión de Clases</h3>
			<p class="feature-description">
				Crea y organiza tus clases, materias y horarios fácilmente. Invita estudiantes, 
				comparte materiales y gestiona todo desde un panel intuitivo.
			</p>
			<a href="/features#classes" class="feature-link">Ver más →</a>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">📚</div>
			<h3 class="feature-title">Sistema de Tareas</h3>
			<p class="feature-description">
				Asigna ejercicios con fechas límite, recibe entregas, califica automáticamente 
				y proporciona retroalimentación personalizada.
			</p>
			<a href="/features#assignments" class="feature-link">Ver más →</a>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">📊</div>
			<h3 class="feature-title">Seguimiento en Tiempo Real</h3>
			<p class="feature-description">
				Monitorea el progreso de cada estudiante, genera reportes automáticos 
				y detecta oportunidades de mejora inmediatamente.
			</p>
			<a href="/features#analytics" class="feature-link">Ver más →</a>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">💬</div>
			<h3 class="feature-title">Comunicación Directa</h3>
			<p class="feature-description">
				Chatea con estudiantes, comparte archivos, envía anuncios y recibe 
				notificaciones instantáneas. Todo en tiempo real.
			</p>
			<a href="/features#communication" class="feature-link">Ver más →</a>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">📱</div>
			<h3 class="feature-title">Acceso Multidispositivo</h3>
			<p class="feature-description">
				Funciona perfectamente en computadoras, tablets y móviles. 
				Accede a tus clases desde cualquier lugar, en cualquier momento.
			</p>
			<a href="/features#mobile" class="feature-link">Ver más →</a>
		</div>
		
		<div class="feature-card">
			<div class="feature-icon">🎯</div>
			<h3 class="feature-title">Sin Curva de Aprendizaje</h3>
			<p class="feature-description">
				Interfaz tan simple que no necesitas capacitación. Enfócate en enseñar, 
				nosotros nos encargamos de la tecnología.
			</p>
			<a href="/features#easy" class="feature-link">Ver más →</a>
		</div>
	</div>
	
	<!-- Testimonios -->
	<div class="testimonials-section">
		<h2>Lo que dicen nuestros usuarios</h2>
		<div class="testimonials">
			<div class="testimonial">
				<p>"Learn.py hizo que la transición a clases en línea fuera increíblemente fácil. Mis estudiantes lo aman."</p>
				<div class="testimonial-author">
					<strong>María González</strong>
					<span>Profesora de Matemáticas</span>
				</div>
			</div>
			<div class="testimonial">
				<p>"Finalmente una plataforma que entiende lo que realmente necesitamos en el aula."</p>
				<div class="testimonial-author">
					<strong>Carlos Rodríguez</strong>
					<span>Director de Instituto</span>
				</div>
			</div>
			<div class="testimonial">
				<p>"Puedo entregar mis tareas desde el móvil y recibir feedback al instante. ¡Genial!"</p>
				<div class="testimonial-author">
					<strong>Ana Martínez</strong>
					<span>Estudiante</span>
				</div>
			</div>
		</div>
	</div>
	
	<!-- CTA Principal -->
	<div class="cta-section cta-premium">
		<h3 class="cta-title">¿Listo para revolucionar tu experiencia educativa?</h3>
		<p class="cta-description">
			Únete a miles de profesores y estudiantes que ya confían en Learn.py. 
			Comienza gratis y escala según tus necesidades.
		</p>
		
		<div class="pricing-highlights">
			<div class="pricing-feature">✓ Plan Gratis: Clases ilimitadas</div>
			<div class="pricing-feature">✓ Plan Premium: Soporte prioritario</div>
		</div>
		
		<div class="cta-buttons">
			<a href="/auth?type=register" class="btn btn-primary btn-large">
				🚀 Comenzar Gratis
			</a>
			<a href="/pricing" class="btn btn-secondary">
				Ver Planes y Precios
			</a>
		</div>
		<p class="cta-note">Sin tarjeta de crédito requerida • Cancelación en cualquier momento</p>
	</div>
	
	<!-- Preguntas Frecuentes Rápidas -->
	<div class="faq-preview">
		<h3>Preguntas Frecuentes</h3>
		<div class="faq-items">
			<div class="faq-item">
				<strong>¿Necesito experiencia técnica?</strong>
				<p>Para nada. Learn.py está diseñado para ser usado por cualquier persona sin conocimientos técnicos.</p>
			</div>
			<div class="faq-item">
				<strong>¿Funciona en móviles?</strong>
				<p>Sí, nuestra plataforma es completamente responsive y funciona perfectamente en cualquier dispositivo.</p>
			</div>
			<div class="faq-item">
				<strong>¿Hay límite de estudiantes?</strong>
				<p>En el plan gratuito puedes tener hasta 30 estudiantes. Los planes de pago ofrecen límites más altos.</p>
			</div>
		</div>
		<a href="/faq" class="btn btn-outline">Ver todas las preguntas</a>
	</div>
	
	<!-- Tecnología + Contacto -->
	<div class="tech-contact-section">
		<div class="tech-stack">
			<h4 class="tech-title">Construido con tecnología moderna</h4>
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
					<div class="icon">⚡</div>
					<span>Rápido</span>
				</div>
				<div class="tech-icon">
					<div class="icon">🔒</div>
					<span>Seguro</span>
				</div>
			</div>
		</div>
		
		<div class="contact-promo">
			<h4>¿Tienes preguntas específicas?</h4>
			<p>Nuestro equipo está aquí para ayudarte</p>
			<a href="/contact" class="btn btn-outline">📧 Contactar Soporte</a>
		</div>
	</div>
	
</section>