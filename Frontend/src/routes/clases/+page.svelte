<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { redirect } from '@sveltejs/kit';
    import { urlip, urlMedia } from '$lib/config';
    import imgDefault from '$lib/images/classDefault.webp';
    import type { PageLoad } from './$types';
    import '$lib/style/Clases.css'
    
    let clases: any[] = [];
    let desplegado: number | null = null;
    let isLoading = true;
    
    // Fecha actual para el dashboard
    const currentDate = new Date();
    const dayNames = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    
    const dayName = dayNames[currentDate.getDay()];
    const dayNumber = currentDate.getDate();
    const monthName = monthNames[currentDate.getMonth()];
    const year = currentDate.getFullYear();
    const formattedDate = `${dayName}, ${dayNumber} de ${monthName} de ${year}`;
    
    // Datos estáticos para el dashboard
    const recentActivity = [
        { type: 'grade', class: 'Programación Web', message: 'Nueva calificación: 9.5 en Práctica 1', time: 'Hace 2 horas' },
        { type: 'announcement', class: 'Bases de Datos', message: 'Nuevo anuncio: Cambio de horario de examen', time: 'Hace 5 horas' },
        { type: 'task', class: 'Diseño de Interfaces', message: 'Nueva tarea asignada: Mockup App', time: 'Ayer' },
        { type: 'material', class: 'Algoritmos', message: 'Nuevo material disponible: Tema 4', time: 'Hace 2 días' }
    ];
    
    const upcomingTasks = [
        { class: 'Programación Web', title: 'Proyecto Final - Primera Entrega', date: '15 Ene', priority: 'high' },
        { class: 'Bases de Datos', title: 'Práctica SQL Avanzado', date: '18 Ene', priority: 'medium' },
        { class: 'Diseño de Interfaces', title: 'Mockup App Móvil', date: '20 Ene', priority: 'high' },
        { class: 'Programación Web', title: 'Ejercicios Tema 2', date: '22 Ene', priority: 'low' }
    ];
    
    // Estadísticas
    let totalClases = 0;
    let tareasPendientes = 0;
    let tareasCompletadas = 12; // Valor por defecto
    let promedioGeneral = 9.2; // Valor por defecto

    function toggleMenu(index: number) {
        desplegado = desplegado === index ? null : index;
    }

    function abandonarClase(name: string) {
        alert(`Has elegido abandonar la clase "${name}"`);
        desplegado = null;
    }

    function verTareas(name: string) {
        alert(`Ver tareas de "${name}"`);
    }

    function abrirForo(name: string) {
        alert(`Abrir foro de "${name}"`);
    }

    function materiales(name: string) {
        alert(`Ver materiales de "${name}"`);
    }
    
    function configurarClase(id: number, name: string) {
        alert(`Configurar clase: ${name}`);
    }
    
    function invitarClase(id: number, name: string) {
        alert(`Invitar a clase: ${name}`);
    }
    
    function crearNuevaClase() {
        if (browser) {
            window.location.href = '/clases/createClass/';
        }
    }
    
    function abrirCalendario() {
        alert('Abriendo calendario');
    }

    function verDetallesClase(id: number) {
        if (browser) {
            window.location.href = `/clases/clase-${id}`;
        }
    }

    // Función original para cargar clases
    async function loadClass() {
        const token = localStorage.getItem('token');
        
        const response = await fetch(`${urlip}class/obtainClass/`, {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'authorization': `${token}`
            },
        });

        const data = await response.json();

        if (response.ok) {
            console.log(data);
            
            clases = data.clases || [];
            
            // Actualizar estadísticas
            totalClases = clases.length;
            tareasPendientes = clases.reduce((total, clase) => {
                return total + (clase.tareas_pendientes || clase.pending_tasks || 0);
            }, 0);
            
        } else {
            console.error("Error cargando clases");
        }
    }

    // Función para recargar las clases
    function recargarClases() {
        loadClass();
    }

    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = '/auth/login';
            } else {
                loadClass().finally(() => {
                    isLoading = false;
                });
            }
        }
    });

    export const load: PageLoad = async () => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                throw redirect(302, '/auth/login');
            }
        }
        return {};
    };
</script>

<div class="dashboard-container">
    <!-- Header -->
    <div class="dashboard-header">
        <div class="welcome-section">
            <div class="welcome-text">
                <h1>
                    <i class="fa-solid fa-hand-wave"></i>
                    ¡Bienvenido de nuevo!
                </h1>
                <p>{formattedDate}</p>
            </div>
            <div class="quick-actions">
                <button class="quick-action-btn" on:click={crearNuevaClase}>
                    <i class="fa-solid fa-plus"></i>
                    Nueva Clase
                </button>
                <button class="quick-action-btn secondary" on:click={abrirCalendario}>
                    <i class="fa-solid fa-calendar"></i>
                    Calendario
                </button>
                <button class="reload-btn" on:click={recargarClases} title="Recargar clases">
                    <i class="fa-solid fa-rotate-right"></i>
                    Recargar
                </button>
            </div>
        </div>
        
        <!-- Stats -->
        {#if !isLoading}
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon blue">
                        <i class="fa-solid fa-book-open"></i>
                    </div>
                    <div class="stat-value">{totalClases}</div>
                    <div class="stat-label">Clases activas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon green">
                        <i class="fa-solid fa-check-circle"></i>
                    </div>
                    <div class="stat-value">{tareasCompletadas}</div>
                    <div class="stat-label">Tareas completadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon orange">
                        <i class="fa-solid fa-clock"></i>
                    </div>
                    <div class="stat-value">{tareasPendientes}</div>
                    <div class="stat-label">Tareas pendientes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon red">
                        <i class="fa-solid fa-star"></i>
                    </div>
                    <div class="stat-value">{promedioGeneral}</div>
                    <div class="stat-label">Promedio general</div>
                </div>
            </div>
        {/if}
    </div>
    
    <!-- Loading State -->
    {#if isLoading}
        <div class="loading-state">
            <div class="loading-spinner">
                <i class="fa-solid fa-spinner fa-spin"></i>
            </div>
            <div class="loading-text">Cargando tus clases...</div>
        </div>
    {/if}
    
    <!-- Main Content -->
    {#if !isLoading}
        <div class="main-grid">
            <!-- Classes Section -->
            <div class="classes-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fa-solid fa-graduation-cap"></i>
                        Mis Clases
                    </h2>
                    <a href="#" class="view-all">Ver todas →</a>
                </div>
                
                {#if clases.length === 0}
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fa-solid fa-book"></i>
                        </div>
                        <div class="empty-text">No tienes clases registradas</div>
                        <button class="quick-action-btn" on:click={crearNuevaClase}>
                            <i class="fa-solid fa-plus"></i>
                            Crear mi primera clase
                        </button>
                    </div>
                {:else}
                    <div class="clases-grid">
                        {#each clases as clase, i}
                            <div class="clase-card">
                                <div class="clase-img-container">
                                    <div class="clase-link-overlay" on:click={() => verDetallesClase(clase.id)}>
                                        {#if clase.imagen_url}
                                            <img src={urlMedia}{clase.imagen_url} alt={clase.name} class="portada">
                                        {:else}
                                            <div class="default-class-bg" style="background: #1a73e8">
                                            </div>
                                        {/if}
                                        
                                        <div class="clase-header-overlay">
                                            <h3 class="clase-title">{clase.name}</h3>
                                            
                                            <p class="clase-teacher">{clase.teacher_name || clase.teacher}</p>
                                        </div>
                                        
                                        <!-- Badge de tareas pendientes -->
                                        {#if (clase.tareas_pendientes || clase.pending_tasks) > 0}
                                            <div class="class-info">
                                                <i class="fa-solid fa-clock"></i>
                                                {clase.tareas_pendientes || clase.pending_tasks} pendiente{(clase.tareas_pendientes || clase.pending_tasks) > 1 ? 's' : ''}
                                            </div>
                                        {/if}
                                    </div>
                                    <button class="clase-options" on:click|stopPropagation={() => toggleMenu(i)}>
                                        <i class="fa-solid fa-ellipsis-vertical"></i>
                                    </button>
                                    {#if desplegado === i}
                                        <div class="menu">
                                            <button on:click|stopPropagation={() => abandonarClase(clase.name)}>
                                                <i class="fa-solid fa-door-open"></i>
                                                Abandonar clase
                                            </button>
                                            <button on:click|stopPropagation={() => configurarClase(clase.id, clase.name)}>
                                                <i class="fa-solid fa-gear"></i>
                                                Configurar
                                            </button>
                                            <button on:click|stopPropagation={() => invitarClase(clase.id, clase.name)}>
                                                <i class="fa-solid fa-user-plus"></i>
                                                Invitar
                                            </button>
                                        </div>
                                    {/if}
                                </div>
                                
                                <div class="clase-footer">
                                    <button class="footer-icon-btn" on:click|stopPropagation={() => verTareas(clase.name)} title="Próximas tareas">
                                        <i class="fa-solid fa-list-check"></i>
                                    </button>
                                    <button class="footer-icon-btn" on:click|stopPropagation={() => abrirForo(clase.name)} title="Foro de clase">
                                        <i class="fa-solid fa-comments"></i>
                                    </button>
                                    <button class="footer-icon-btn" on:click|stopPropagation={() => materiales(clase.name)} title="Materiales">
                                        <i class="fa-solid fa-folder-open"></i>
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
            
            <!-- Right Sidebar -->
            <div class="sidebar-section">
                <!-- Calendar -->
                <div class="mini-calendar">
                    <div class="calendar-date">{dayNumber}</div>
                    <div class="calendar-day">{dayName}</div>
                    <div class="calendar-month">
                        <i class="fa-solid fa-calendar-days"></i>
                        {monthName} {year}
                    </div>
                </div>
                
                <!-- Upcoming Tasks -->
                <div class="card">
                    <div class="card-title">
                        <i class="fa-solid fa-clock-rotate-left"></i>
                        Próximas Entregas
                    </div>
                    {#each upcomingTasks as task}
                        <div class="task-list-item {task.priority}">
                            <div class="task-class-label">
                                <i class="fa-solid fa-book"></i>
                                {task.class}
                            </div>
                            <div class="task-list-title">{task.title}</div>
                            <div class="task-list-date">
                                <i class="fa-solid fa-calendar-day"></i>
                                {task.date}
                            </div>
                        </div>
                    {/each}
                </div>
                
                <!-- Recent Activity -->
                <div class="card">
                    <div class="card-title">
                        <i class="fa-solid fa-bell"></i>
                        Actividad Reciente
                    </div>
                    {#each recentActivity as activity}
                        <div class="activity-item">
                            <div class="activity-icon {activity.type}">
                                {#if activity.type === 'grade'}
                                    <i class="fa-solid fa-star"></i>
                                {:else if activity.type === 'announcement'}
                                    <i class="fa-solid fa-bullhorn"></i>
                                {:else if activity.type === 'task'}
                                    <i class="fa-solid fa-tasks"></i>
                                {:else}
                                    <i class="fa-solid fa-file-lines"></i>
                                {/if}
                            </div>
                            <div class="activity-content">
                                <div class="activity-class">
                                    <i class="fa-solid fa-book"></i>
                                    {activity.class}
                                </div>
                                <div class="activity-message">{activity.message}</div>
                                <div class="activity-time">
                                    <i class="fa-solid fa-clock"></i>
                                    {activity.time}
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    {/if}
</div>