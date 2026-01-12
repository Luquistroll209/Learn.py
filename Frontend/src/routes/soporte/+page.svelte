<script>
	import '$lib/style/PrincipalPage.css';
	let name = '';
	let email = '';
	let message = '';
	function sendMessage() {
		//sin terminar, tengo que hacerlo
		name = '';
		email = '';
		message = '';
	}
</script>

<svelte:head>
	<title>Soporte | Learn.py</title>
	<meta name="description" content="Centro de soporte y ayuda de Learn.py" />
</svelte:head>

<section class="welcome-container">

	<div class="hero-section" style="text-align:left; max-width:900px; margin:0 auto">

		<h1 class="welcome-title">
			Soporte de <span class="welcome-highlight">Learn.py</span>
		</h1>

		<p class="welcome-subtitle">
			Estamos aquí para ayudarte a resolver cualquier duda o problema
			relacionado con el uso de la plataforma. Puedes enviarnos un mensaje
			o revisar las preguntas frecuentes.
		</p>

		<h3 class="feature-title" style="margin-top:2rem">Enviar un mensaje</h3>
		<p class="feature-description">
			Completa el siguiente formulario y nuestro equipo de soporte te responderá
			en el menor tiempo posible.
		</p>

		<div style="margin:1rem 0;">
			<input type="text" placeholder="Nombre" bind:value={name} class="feature-description" style="width:100%; padding:0.8rem; margin-bottom:0.8rem; border:1px solid #dadce0; border-radius:6px" />
			<input type="email" placeholder="Correo electrónico" bind:value={email} class="feature-description" style="width:100%; padding:0.8rem; margin-bottom:0.8rem; border:1px solid #dadce0; border-radius:6px" />
			<textarea placeholder="Tu mensaje" bind:value={message} class="feature-description" style="width:100%; padding:0.8rem; margin-bottom:0.8rem; border:1px solid #dadce0; border-radius:6px; height:120px"></textarea>
			<button class="btn btn-primary" on:click={sendMessage}>Enviar Mensaje</button>
		</div>

		<h3 class="feature-title" style="margin-top:2.5rem">Preguntas Frecuentes</h3>

		<div class="faq-items">
			<div class="faq-item">
				<strong>¿Cómo recupero mi contraseña?</strong>
				<p>Usa la opción "Olvidé mi contraseña" en la pantalla de inicio de sesión y sigue los pasos indicados.</p>
			</div>
			<div class="faq-item">
				<strong>¿Cómo creo una clase o tarea?</strong>
				<p>Si eres docente, ve a la sección "Mis clases" y selecciona "Crear clase" o "Crear tarea".</p>
			</div>
			<div class="faq-item">
				<strong>¿Puedo cambiar mi correo asociado?</strong>
				<p>Sí, desde "Configuración de cuenta" puedes actualizar tu correo electrónico.</p>
			</div>
			<div class="faq-item">
				<strong>¿Cómo contacto al soporte si no funciona la plataforma?</strong>
				<p>Si la plataforma está caída, envía un correo a <strong>soporte@learnpy.com</strong> y te atenderemos tan pronto como sea posible.</p>
			</div>
		</div>

		<h3 class="feature-title" style="margin-top:2rem">Contacto directo</h3>
		<p class="feature-description">
			Correo electrónico: <strong>soporte@learnpy.com</strong><br />
			También puedes usar nuestro formulario de mensajes para cualquier consulta.
		</p>

	</div>

</section>
