<script lang="ts">
    import "$lib/style/pricing.css";
</script>

<svelte:head>
    <title>Planes y precios - Learn.py</title>
    <meta
        name="description"
        content="Elige el plan perfecto para ti. Desde gratis hasta centros educativos, con descuento del 10% en planes Básico y Profesional."
    />
</svelte:head>

<section class="welcome-container">
    <div class="hero-section">
        <h1 class="welcome-title">
            Planes para <span class="brand-learn">potenciar</span>
            <span class="brand-py">tu enseñanza</span>
        </h1>
        <p class="welcome-subtitle">
            Precios claros, sin sorpresas. Elige el plan que mejor se adapte a
            tus necesidades y empieza a transformar tu aula hoy mismo.
        </p>
        <div class="discount-banner">
            <i class="fas fa-tag"></i>
            <span
                ><strong>Oferta especial:</strong> 10% de descuento en los
                planes <strong>Básico</strong> y <strong>Profesional</strong> durante
                los primeros 3 meses. ¡Aprovecha ahora!</span
            >
        </div>
    </div>

    <div class="pricing-grid">
        <div class="pricing-card">
            <div class="card-header">
                <div class="plan-icon">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <h3 class="plan-nombre">Free</h3>
            </div>
            <div class="plan-precio">
                <span class="precio">Gratis</span>
                <span class="periodo">siempre</span>
            </div>
            <ul class="caracteristicas">
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >2 clases activas</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Hasta 15 alumnos por clase</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Foro de dudas básico</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Soporte por email</span
                    >
                </li>
            </ul>
            <div class="card-cta">
                <a
                    href="/auth?type=register&role=teacher"
                    class="btn btn-secondary btn-plan"
                    >Comenzar gratis <i class="fas fa-arrow-right"></i></a
                >
            </div>
        </div>

        <div class="pricing-card">
            <div class="discount-badge">-10%</div>
            <div class="card-header">
                <div class="plan-icon">
                    <i class="fas fa-chalkboard-teacher"></i>
                </div>
                <h3 class="plan-nombre">Básico</h3>
            </div>
            <div class="plan-precio">
                <span class="precio-original">7€</span>
                <span class="precio-descuento">6.30€</span>
                <span class="periodo">/mes</span>
            </div>
            <ul class="caracteristicas">
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >5 clases simultáneas</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >30 alumnos por clase</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >1 GB de almacenamiento</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Subir archivos y tareas</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Soporte prioritario 48h</span
                    >
                </li>
            </ul>
            <div class="card-cta">
                <a
                    href="/auth?type=register&plan=basico"
                    class="btn btn-secondary btn-plan"
                    >Elegir plan <i class="fas fa-arrow-right"></i></a
                >
            </div>
            <div class="plan-nota">
                <i class="fas fa-calendar-alt"></i> Precio con descuento por tiempo
                limitado
            </div>
        </div>

        <div class="pricing-card destacado">
            <div class="popular-label">Más popular</div>
            <div class="discount-badge">-10%</div>
            <div class="card-header">
                <div class="plan-icon"><i class="fas fa-chart-line"></i></div>
                <h3 class="plan-nombre">Profesional</h3>
            </div>
            <div class="plan-precio">
                <span class="precio-original">20€</span>
                <span class="precio-descuento">18.00€</span>
                <span class="periodo">/mes</span>
            </div>
            <ul class="caracteristicas">
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Clases ilimitadas</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >100 alumnos por clase</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >10 GB de almacenamiento</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Estadísticas avanzadas</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span>Soporte 24/7</span>
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Exámenes online</span
                    >
                </li>
            </ul>
            <div class="card-cta">
                <a
                    href="/auth?type=register&plan=profesional"
                    class="btn btn-primary btn-plan"
                    >Elegir plan <i class="fas fa-arrow-right"></i></a
                >
            </div>
            <div class="plan-nota">
                <i class="fas fa-calendar-alt"></i> Precio con descuento por tiempo
                limitado
            </div>
        </div>

        <div class="pricing-card">
            <div class="card-header">
                <div class="plan-icon"><i class="fas fa-building"></i></div>
                <h3 class="plan-nombre">Centro educativo</h3>
            </div>
            <div class="plan-precio">
                <span class="precio">500€</span>
                <span class="periodo">/mes</span>
            </div>
            <ul class="caracteristicas">
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Todo lo de Profesional</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Almacenamiento ilimitado</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Logo personalizado</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Gestión de profesores y alumnos</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Soporte dedicado 24/7</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >Informes personalizados</span
                    >
                </li>
                <li>
                    <i class="fas fa-check-circle"></i><span
                        >API de integración</span
                    >
                </li>
            </ul>
            <div class="card-cta">
                <a href="/contact" class="btn btn-secondary btn-plan"
                    >Contactar ventas <i class="fas fa-arrow-right"></i></a
                >
            </div>
            <div class="plan-nota">
                <i class="fas fa-phone-alt"></i> Consulta descuento por pago anual
            </div>
        </div>
    </div>

    <div class="comparativa-section">
        <div class="section-header">
            <h2>Compara todas las características</h2>
            <p>Más detalles de lo que incluye cada plan</p>
        </div>
        <div class="compare-header-labels">
            <div class="compare-feature-spacer"></div>
            <div class="compare-plan-labels">
                <span>Free</span>
                <span>Básico</span>
                <span class="compare-label-destacado">Profesional</span>
                <span>Centro</span>
            </div>
        </div>
        <div class="feature-compare">
            <div class="compare-row">
                <div class="compare-feature">Clases</div>
                <div class="compare-values">
                    <span>2 clases</span><span>5 clases</span><span
                        >Ilimitadas</span
                    ><span>Ilimitadas</span>
                </div>
            </div>
            <div class="compare-row">
                <div class="compare-feature">Alumnos por clase</div>
                <div class="compare-values">
                    <span>15</span><span>30</span><span>100</span><span
                        >Sin límite</span
                    >
                </div>
            </div>
            <div class="compare-row">
                <div class="compare-feature">Almacenamiento</div>
                <div class="compare-values">
                    <span>100 MB</span><span>1 GB</span><span>10 GB</span><span
                        >Ilimitado</span
                    >
                </div>
            </div>
            <div class="compare-row">
                <div class="compare-feature">Soporte</div>
                <div class="compare-values">
                    <span>Email</span><span>Prioritario 48h</span><span
                        >24/7</span
                    ><span>Dedicado</span>
                </div>
            </div>
            <div class="compare-row">
                <div class="compare-feature">Informes analíticos</div>
                <div class="compare-values">
                    <span><i class="fas fa-times"></i></span><span
                        ><i class="fas fa-check"></i> Básicos</span
                    ><span><i class="fas fa-check"></i> Avanzados</span><span
                        ><i class="fas fa-check"></i> Personalizados</span
                    >
                </div>
            </div>
            <div class="compare-row">
                <div class="compare-feature">Logo personalizado</div>
                <div class="compare-values">
                    <span><i class="fas fa-times"></i></span><span
                        ><i class="fas fa-times"></i></span
                    ><span><i class="fas fa-times"></i></span><span
                        ><i class="fas fa-check"></i></span
                    >
                </div>
            </div>
        </div>
    </div>

    <div class="faq-preview">
        <h3>Preguntas frecuentes sobre planes y pagos</h3>
        <div class="faq-items">
            <div class="faq-item">
                <strong>¿Puedo cambiar de plan en cualquier momento?</strong>
                <p>
                    Sí, puedes actualizar o cancelar tu plan cuando lo
                    necesites. Los cambios se aplican en el siguiente ciclo de
                    facturación.
                </p>
            </div>
            <div class="faq-item">
                <strong>¿Hay descuentos para instituciones educativas?</strong>
                <p>
                    Sí, para colegios, institutos o universidades ofrecemos
                    condiciones especiales. Contacta con nuestro equipo de
                    ventas.
                </p>
            </div>
            <div class="faq-item">
                <strong>¿Qué métodos de pago aceptan?</strong>
                <p>
                    Aceptamos tarjetas de crédito/débito, PayPal y transferencia
                    bancaria para planes anuales o centros educativos.
                </p>
            </div>
        </div>
        <a href="/faq" class="btn btn-outline">Ver todas las preguntas</a>
    </div>

    <div class="cta-section">
        <h3 class="cta-title">¿Necesitas un plan a medida para tu centro?</h3>
        <p class="cta-description">
            Contáctanos y diseñamos una solución personalizada adaptada al
            tamaño y necesidades de tu institución.
        </p>
        <div class="cta-buttons">
            <a href="/contact" class="btn btn-primary"
                ><i class="fas fa-headset"></i> Hablar con ventas</a
            >
            <a href="/demo" class="btn btn-secondary"
                ><i class="fas fa-play-circle"></i> Solicitar demo gratuita</a
            >
        </div>
    </div>
</section>
