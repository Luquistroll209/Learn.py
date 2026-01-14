<!-- dashboard.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { redirect } from '@sveltejs/kit';
    import { urlip } from '$lib/config';
    import { page } from '$app/stores';
    
    // Importar el mismo CSS
    import "$lib/style/inClass.css";
    
    let id;
    let clase: any = {};
    let activeTab = 'alumnos';
    let showInviteModal = false;
    let showCreateTaskModal = false;
    let showManageGradesModal = false;
    
    // Datos del dashboard
    let alumnos: any[] = [];
    let tareas: any[] = [];
    let calificaciones: any[] = [];
    let materiales: any[] = [];
    let estadisticas: any = {};
    
    // Formularios
    let inviteEmail = '';
    let newTask = {
        title: '',
        description: '',
        dueDate: '',
        maxGrade: 10,
        type: 'tarea'
    };
    
    $: id = $page.params.id;
    
    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = '/auth/login';
            } else {
                loadDashboardData();
            }
        }
    });
    
    async function loadDashboardData() {
        const token = localStorage.getItem('token');
        
        // Cargar información de la clase
        const classResponse = await fetch(`${urlip}class/obtainClassByID/${id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'authorization': `${token}`
            },
        });
        
        if (classResponse.ok) {
            clase = await classResponse.json();
        }
        
        await loadAlumnos(token);
        
        await loadTareas(token);
        
        await loadEstadisticas(token);
    }
    
    async function loadAlumnos(token: string) {
        alumnos = [
            { id: 1, name: 'Ana Martínez', email: 'ana@example.com', status: 'activo', avatar: 'AM' },
            { id: 2, name: 'Carlos López', email: 'carlos@example.com', status: 'activo', avatar: 'CL' },
            { id: 3, name: 'María García', email: 'maria@example.com', status: 'pendiente', avatar: 'MG' },
            { id: 4, name: 'Juan Pérez', email: 'juan@example.com', status: 'activo', avatar: 'JP' },
            { id: 5, name: 'Laura Sánchez', email: 'laura@example.com', status: 'inactivo', avatar: 'LS' }
        ];
    }
    
    async function loadTareas(token: string) {
        tareas = [
            { id: 1, title: 'Práctica 1: Introducción a Svelte', dueDate: '5 Ene', entregadas: 15, total: 20, status: 'activa' },
            { id: 2, title: 'Proyecto Final - Primera Entrega', dueDate: '15 Ene', entregadas: 8, total: 20, status: 'activa' },
            { id: 3, title: 'Ejercicios Tema 2', dueDate: '20 Ene', entregadas: 0, total: 20, status: 'activa' },
            { id: 4, title: 'Lectura: Componentes Reactivos', dueDate: '25 Ene', entregadas: 18, total: 20, status: 'cerrada' }
        ];
    }
    
    async function loadEstadisticas(token: string) {
        estadisticas = {
            totalAlumnos: 20,
            alumnosActivos: 18,
            tareasActivas: 3,
            tareasCerradas: 1,
            promedioClase: 8.5,
            proximaEntrega: '15 Ene'
        };
    }
    
    async function invitarAlumno() {
        if (!inviteEmail) return;
        
        const token = localStorage.getItem('token');
        
        try {
            const response = await fetch(`${urlip}class/${id}/invite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `${token}`
                },
                body: JSON.stringify({ email: inviteEmail })
            });
            
            if (response.ok) {
                alert('Invitación enviada correctamente');
                inviteEmail = '';
                showInviteModal = false;
                await loadAlumnos(token!);
            } else {
                alert('Error al enviar la invitación');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al enviar la invitación');
        }
    }
    
    async function crearTarea() {
        if (!newTask.title || !newTask.dueDate) {
            alert('Por favor, completa los campos obligatorios');
            return;
        }
        
        const token = localStorage.getItem('token');
        
        try {
            const response = await fetch(`${urlip}class/${id}/tasks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `${token}`
                },
                body: JSON.stringify(newTask)
            });
            
            if (response.ok) {
                alert('Tarea creada correctamente');
                // Reset formulario
                newTask = {
                    title: '',
                    description: '',
                    dueDate: '',
                    maxGrade: 10,
                    type: 'tarea'
                };
                showCreateTaskModal = false;
                // Recargar tareas
                await loadTareas(token!);
            } else {
                alert('Error al crear la tarea');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al crear la tarea');
        }
    }
    
    function eliminarAlumno(alumnoId: number) {
        if (confirm('¿Estás seguro de eliminar a este alumno de la clase?')) {
            const token = localStorage.getItem('token');
            
            fetch(`${urlip}class/${id}/students/${alumnoId}`, {
                method: 'DELETE',
                headers: {
                    'authorization': `${token}`
                }
            })
            .then(response => {
                if (response.ok) {
                    loadAlumnos(token!);
                }
            });
        }
    }
    
    function eliminarTarea(tareaId: number) {
        if (confirm('¿Estás seguro de eliminar esta tarea?')) {
            const token = localStorage.getItem('token');
            
            fetch(`${urlip}class/${id}/tasks/${tareaId}`, {
                method: 'DELETE',
                headers: {
                    'authorization': `${token}`
                }
            })
            .then(response => {
                if (response.ok) {
                    loadTareas(token!);
                }
            });
        }
    }
    
    function copiarCodigoClase() {
        // Aquí implementarías la lógica para copiar el código de la clase
        navigator.clipboard.writeText(clase.code || 'CLASE123');
        alert('Código copiado al portapapeles');
    }
</script>

<div class="class-container">
    <!-- Header de la clase -->
    <div class="class-header">
        <div class="class-header-content">
            <h1>Dashboard - {clase.name}</h1>
            <p>Panel de control del profesor</p>
            <p>Curso 2024-2025</p>
        </div>
    </div>
    
    <!-- Navegación por pestañas del dashboard -->
    <div class="class-tabs">
        <button class="tab-button" class:active={activeTab === 'alumnos'} on:click={() => activeTab = 'alumnos'}>
            👥 Gestión de Alumnos
        </button>
        <button class="tab-button" class:active={activeTab === 'tareas'} on:click={() => activeTab = 'tareas'}>
            📝 Gestión de Tareas
        </button>
        <button class="tab-button" class:active={activeTab === 'calificaciones'} on:click={() => activeTab = 'calificaciones'}>
            📊 Calificaciones
        </button>
        <button class="tab-button" class:active={activeTab === 'configuracion'} on:click={() => activeTab = 'configuracion'}>
            ⚙️ Configuración
        </button>
    </div>
    
    <div class="class-content">
        <!-- Contenido principal -->
        <div class="main-content">
            <!-- Tab: Gestión de Alumnos -->
            {#if activeTab === 'alumnos'}
                <div class="card-title">
                    Lista de Alumnos ({alumnos.length})
                    <button class="action-button" on:click={() => showInviteModal = true}>
                        + Invitar Alumno
                    </button>
                </div>
                
                <div class="card" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; padding: 16px; border-bottom: 1px solid var(--border-color);">
                        <span style="font-weight: 600;">Nombre</span>
                        <span style="font-weight: 600;">Correo</span>
                        <span style="font-weight: 600;">Estado</span>
                        <span style="font-weight: 600;">Acciones</span>
                    </div>
                    
                    {#each alumnos as alumno}
                        <div class="student-item">
                            <div class="avatar">{alumno.avatar}</div>
                            <div class="student-info">
                                <div class="student-name">{alumno.name}</div>
                                <div class="student-email">{alumno.email}</div>
                            </div>
                            <div>
                                <span class="task-status {alumno.status === 'activo' ? 'entregada' : alumno.status === 'pendiente' ? 'pendiente' : 'atrasada'}" 
                                      style="margin-right: 12px;">
                                    {alumno.status === 'activo' ? 'Activo' : alumno.status === 'pendiente' ? 'Pendiente' : 'Inactivo'}
                                </span>
                            </div>
                            <div>
                                <button class="secondary-button" style="margin-right: 8px;" 
                                        on:click={() => eliminarAlumno(alumno.id)}>
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
            
            <!-- Tab: Gestión de Tareas -->
            {#if activeTab === 'tareas'}
                <div class="card-title">
                    Tareas de la Clase
                    <button class="action-button" on:click={() => showCreateTaskModal = true}>
                        + Crear Nueva Tarea
                    </button>
                </div>
                
                <div class="card" style="margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 16px; padding: 16px; border-bottom: 1px solid var(--border-color); font-weight: 600;">
                        <span>Título</span>
                        <span>Fecha Límite</span>
                        <span>Entregadas</span>
                        <span>Acciones</span>
                    </div>
                    
                    {#each tareas as tarea}
                        <div class="task-item" style="grid-template-columns: 2fr 1fr 1fr 1fr; display: grid; gap: 16px; align-items: center;">
                            <div>
                                <div class="task-title">{tarea.title}</div>
                                <div class="task-due">ID: {tarea.id}</div>
                            </div>
                            <div class="task-due">{tarea.dueDate}</div>
                            <div>
                                <span class="task-status {tarea.status === 'cerrada' ? 'entregada' : 'pendiente'}">
                                    {tarea.entregadas}/{tarea.total}
                                </span>
                            </div>
                            <div style="display: flex; gap: 8px;">
                                <button class="secondary-button" on:click={() => window.location.href = `/clases/clase-${id}/tarea-${tarea.id}`}>
                                    Ver
                                </button>
                                <button class="secondary-button" on:click={() => eliminarTarea(tarea.id)}>
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
            
            <!-- Tab: Calificaciones -->
            {#if activeTab === 'calificaciones'}
                <div class="card-title">
                    Gestión de Calificaciones
                    <button class="action-button" on:click={() => showManageGradesModal = true}>
                        📊 Calificar Tarea
                    </button>
                </div>
                
                <div class="card" style="margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="average-card">
                            <div class="average-label">Promedio de la Clase</div>
                            <div class="average-number">{estadisticas.promedioClase}</div>
                        </div>
                        <div class="average-card" style="background: linear-gradient(135deg, var(--success-color), #1e8e3e);">
                            <div class="average-label">Alumnos Activos</div>
                            <div class="average-number">{estadisticas.alumnosActivos}/{estadisticas.totalAlumnos}</div>
                        </div>
                    </div>
                </div>
                
                <div class="card-title">Tareas para Calificar</div>
                {#each tareas.filter(t => t.status === 'activa') as tarea}
                    <div class="task-item">
                        <div class="task-icon">📝</div>
                        <div class="task-info">
                            <div class="task-title">{tarea.title}</div>
                            <div class="task-due">Fecha límite: {tarea.dueDate}</div>
                            <div class="task-due">Por calificar: {tarea.total - tarea.entregadas} alumnos</div>
                        </div>
                        <button class="action-button" on:click={() => window.location.href = `/clases/clase-${id}/calificar-${tarea.id}`}>
                            Calificar
                        </button>
                    </div>
                {/each}
            {/if}
            
            <!-- Tab: Configuración -->
            {#if activeTab === 'configuracion'}
                <div class="card-title">
                    Configuración de la Clase
                </div>
                
                <div class="card" style="margin-bottom: 20px;">
                    <div style="padding: 16px;">
                        <div style="margin-bottom: 24px;">
                            <h3 style="margin-bottom: 12px; color: var(--text-color);">Información de la Clase</h3>
                            <div style="display: grid; gap: 12px;">
                                <div>
                                    <label for="NombreClase" style="display: block; margin-bottom: 4px; color: var(--text-light);">Nombre de la Clase</label>
                                    <input type="text" value={clase.name} style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px;" />
                                </div>
                                <div>
                                    <label for="Descripción" style="display: block; margin-bottom: 4px; color: var(--text-light);">Descripción</label>
                                    <textarea style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; min-height: 100px;">
                                        {clase.description}
                                    </textarea>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 24px;">
                            <h3 style="margin-bottom: 12px; color: var(--text-color);">Código de Invitación</h3>
                            <div style="text-align: center; padding: 24px; background: var(--background-hover); border-radius: 8px;">
                                <div style="font-size: 32px; font-weight: 700; color: var(--primary-color); margin-bottom: 16px;">
                                    {clase.code || 'CLASE123'}
                                </div>
                                <button class="action-button" on:click={copiarCodigoClase}>
                                    Copiar Código
                                </button>
                            </div>
                        </div>
                        
                        <div>
                            <h3 style="margin-bottom: 12px; color: var(--text-color);">Acciones Peligrosas</h3>
                            <div style="display: flex; gap: 12px;">
                                <button class="secondary-button" style="background: var(--error-color); color: white; border-color: var(--error-color);">
                                    Archivar Clase
                                </button>
                                <button class="secondary-button" style="background: #ff9800; color: white; border-color: #ff9800;">
                                    Exportar Datos
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
        
        <!-- Sidebar con estadísticas y acciones rápidas -->
        <div class="sidebar">
            <!-- Estadísticas rápidas -->
            <div class="card">
                <div class="card-title">Estadísticas</div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <span>Alumnos</span>
                    <span style="font-weight: 600;">{estadisticas.totalAlumnos}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <span>Tareas Activas</span>
                    <span style="font-weight: 600;">{estadisticas.tareasActivas}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <span>Promedio Clase</span>
                    <span style="font-weight: 600;">{estadisticas.promedioClase}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0;">
                    <span>Próxima Entrega</span>
                    <span style="font-weight: 600;">{estadisticas.proximaEntrega}</span>
                </div>
            </div>
            
            <!-- Acciones rápidas -->
            <div class="card">
                <div class="card-title">Acciones Rápidas</div>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => showInviteModal = true}>
                    📧 Invitar Alumnos
                </button>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => showCreateTaskModal = true}>
                    📝 Crear Tarea
                </button>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => activeTab = 'calificaciones'}>
                    📊 Calificar
                </button>
                <a href="/clases/clase-{id}" class="secondary-button" style="width: 100%;">
                    👁️ Ver como Alumno
                </a>
            </div>
            
            <!-- Enlaces útiles -->
            <div class="card">
                <div class="card-title">Enlaces</div>
                <a href="/clases" class="secondary-button" style="width: 100%; margin-bottom: 8px;">
                    ← Volver a Clases
                </a>
                <button class="secondary-button" style="width: 100%;">
                    📅 Calendario de Entregas
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Modal: Invitar Alumno -->
{#if showInviteModal}
    <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
        <div class="card" style="width: 90%; max-width: 500px;">
            <div class="card-title">
                Invitar Alumno
                <button on:click={() => showInviteModal = false} style="background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
            </div>
            <div style="padding: 16px;">
                <p style="margin-bottom: 16px; color: var(--text-light);">Envía una invitación por correo electrónico para unirse a la clase.</p>
                <div style="margin-bottom: 20px;">
                    <label for="inviteEmail" style="display: block; margin-bottom: 8px; color: var(--text-color);">Correo Electrónico</label>
                    <input type="email" bind:value={inviteEmail} 
                           style="width: 100%; padding: 12px; border: 1px solid var(--border-color); border-radius: 6px;" 
                           placeholder="alumno@ejemplo.com" />
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 12px;">
                    <button class="secondary-button" on:click={() => showInviteModal = false}>
                        Cancelar
                    </button>
                    <button class="action-button" on:click={invitarAlumno}>
                        Enviar Invitación
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Modal: Crear Tarea -->
{#if showCreateTaskModal}
    <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
        <div class="card" style="width: 90%; max-width: 500px;">
            <div class="card-title">
                Crear Nueva Tarea
                <button on:click={() => showCreateTaskModal = false} style="background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
            </div>
            <div style="padding: 16px;">
                <div style="display: grid; gap: 16px; margin-bottom: 20px;">
                    <div>
                        <label for="titulo" style="display: block; margin-bottom: 8px; color: var(--text-color);">
                            Título *
                        </label>
                        <input type="text" bind:value={newTask.title} 
                               style="width: 100%; padding: 12px; border: 1px solid var(--border-color); border-radius: 6px;" 
                               placeholder="Nombre de la tarea" />
                    </div>
                    <div>
                        <label for="Descripción" style="display: block; margin-bottom: 8px; color: var(--text-color);">Descripción</label>
                        <textarea bind:value={newTask.description} 
                                  style="width: 100%; padding: 12px; border: 1px solid var(--border-color); border-radius: 6px; min-height: 100px;"
                                  placeholder="Descripción detallada de la tarea"></textarea>
                    </div>
                    <div>
                        <label for="Fecha_Limite" style="display: block; margin-bottom: 8px; color: var(--text-color);">Fecha Límite *</label>
                        <input type="date" bind:value={newTask.dueDate} 
                               style="width: 100%; padding: 12px; border: 1px solid var(--border-color); border-radius: 6px;" />
                    </div>
                    <div>
                        <label for="Puntuación Máximo" style="display: block; margin-bottom: 8px; color: var(--text-color);">Puntuación Máxima</label>
                        <input type="number" bind:value={newTask.maxGrade} min="1" max="100"
                               style="width: 100%; padding: 12px; border: 1px solid var(--border-color); border-radius: 6px;" />
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 12px;">
                    <button class="secondary-button" on:click={() => showCreateTaskModal = false}>
                        Cancelar
                    </button>
                    <button class="action-button" on:click={crearTarea}>
                        Crear Tarea
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .task-item[style*="grid-template-columns"] {
        display: grid;
        padding: 16px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        margin-bottom: 12px;
        align-items: center;
    }
    
    input, textarea {
        font-family: inherit;
        font-size: 14px;
    }
    
    input:focus, textarea:focus {
        outline: none;
        border-color: var(--primary-color);
    }
</style>