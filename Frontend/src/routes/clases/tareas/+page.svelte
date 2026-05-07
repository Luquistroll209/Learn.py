<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { page } from '$app/stores';
    import { urlip } from '$lib/config';
    import Alert from '$lib/components/alert.svelte';
    import { showAlert } from '$lib/store/alertStore.js';
    import '$lib/style/classTasks.css';

    type TaskRow = {
        id: number;
        title: string;
        description: string;
        clase_id: string;
        class_name: string;
        role: 'student' | 'teacher' | 'assistant';
        due_at: string | null;
        created_at: string;
        photos_count: number;
        urls_count: number;
        is_overdue: boolean;
        priority: 'high' | 'medium' | 'low' | 'overdue';
        is_delivered: boolean | null;
        delivered_at: string | null;
        grade: string | null;
        status: 'pending' | 'completed';
    };

    type Summary = {
        pending_count: number;
        completed_count: number;
        overdue_count: number;
        average_grade: string | null;
    };

    let isLoading = true;
    let isRefreshing = false;
    let activeTab: 'pending' | 'completed' = 'pending';
    let currentFilter = '';

    let summary: Summary = {
        pending_count: 0,
        completed_count: 0,
        overdue_count: 0,
        average_grade: null
    };
    let pendingTasks: TaskRow[] = [];
    let completedTasks: TaskRow[] = [];

    function formatDate(value: string | null | undefined): string {
        if (!value) return 'Sin fecha límite';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return String(value);
        return date.toLocaleString('es-ES', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function openTask(task: TaskRow) {
        if (!browser) return;
        window.location.href = `/clases/clase-${task.clase_id}/tarea-${task.id}`;
    }

    function goToClasses() {
        if (!browser) return;
        window.location.href = '/clases';
    }

    function clearFilter() {
        if (!browser) return;
        window.location.href = '/clases/tareas';
    }

    function getRoleLabel(role: string): string {
        if (role === 'teacher') return 'Profesor';
        if (role === 'assistant') return 'Asistente';
        return 'Alumno';
    }

    function getPendingStatus(task: TaskRow): string {
        if (task.role === 'teacher' || task.role === 'assistant') {
            if (task.is_overdue) return 'Cerrada';
            return 'Activa';
        }
        if (task.is_overdue) return 'Atrasada';
        return 'Pendiente';
    }

    async function loadUserTasks(silent = false) {
        const token = localStorage.getItem('token');
        if (!token) return;

        if (silent) {
            isRefreshing = true;
        } else {
            isLoading = true;
        }

        const params = new URLSearchParams();
        if (currentFilter) {
            params.set('clase_id', currentFilter);
        }
        const query = params.toString();
        const endpoint = `${urlip}class/obtainUserTasks/${query ? `?${query}` : ''}`;

        try {
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    authorization: token
                }
            });
            const data = await response.json();
            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudieron cargar las tareas', 'red');
                return;
            }

            summary = data.summary || summary;
            pendingTasks = Array.isArray(data.pending_tasks) ? data.pending_tasks : [];
            completedTasks = Array.isArray(data.completed_tasks) ? data.completed_tasks : [];
            if (activeTab === 'completed' && completedTasks.length === 0 && pendingTasks.length > 0) {
                activeTab = 'pending';
            }
        } catch (error) {
            showAlert('Error', 'Error de conexión al cargar tareas', 'red');
        } finally {
            isLoading = false;
            isRefreshing = false;
        }
    }

    onMount(async () => {
        if (!browser) return;
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/auth/login';
            return;
        }

        currentFilter = $page.url.searchParams.get('clase') || '';
        await loadUserTasks();
    });
</script>

<Alert />

<div class="tasks-board-container">
    <div class="tasks-board-header">
        <div>
            <h1>Tareas</h1>
            <p>
                {#if currentFilter}
                    Vista filtrada por clase ({currentFilter}).
                {:else}
                    Revisa tus pendientes y entregas completadas.
                {/if}
            </p>
        </div>
        <div class="tasks-header-actions">
            <button class="soft-btn" on:click={goToClasses}>Volver a clases</button>
            {#if currentFilter}
                <button class="soft-btn" on:click={clearFilter}>Quitar filtro</button>
            {/if}
            <button class="primary-btn" on:click={() => loadUserTasks(true)} disabled={isRefreshing}>
                {isRefreshing ? 'Actualizando...' : 'Actualizar'}
            </button>
        </div>
    </div>

    <div class="tasks-summary-grid">
        <div class="summary-card">
            <div class="summary-value">{summary.pending_count}</div>
            <div class="summary-label">Pendientes</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{summary.overdue_count}</div>
            <div class="summary-label">Atrasadas</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{summary.completed_count}</div>
            <div class="summary-label">Completadas</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">{summary.average_grade || '-'}</div>
            <div class="summary-label">Promedio</div>
        </div>
    </div>

    <div class="tasks-tabs">
        <button class:active={activeTab === 'pending'} on:click={() => activeTab = 'pending'}>
            Pendientes ({summary.pending_count})
        </button>
        <button class:active={activeTab === 'completed'} on:click={() => activeTab = 'completed'}>
            Completadas ({summary.completed_count})
        </button>
    </div>

    {#if isLoading}
        <div class="tasks-empty">
            <i class="fa-solid fa-spinner fa-spin"></i>
            Cargando tareas...
        </div>
    {:else if activeTab === 'pending'}
        {#if pendingTasks.length === 0}
            <div class="tasks-empty">
                <i class="fa-solid fa-check-circle"></i>
                No tienes tareas pendientes.
            </div>
        {:else}
            <div class="tasks-grid">
                {#each pendingTasks as task}
                    <article class="task-card {task.priority}">
                        <div class="task-card-top">
                            <div class="task-class">{task.class_name}</div>
                            <span class="task-role">{getRoleLabel(task.role)}</span>
                        </div>

                        <h2>{task.title}</h2>
                        <p>{task.description || 'Sin descripción'}</p>

                        <div class="task-meta">
                            <span><i class="fa-solid fa-calendar-day"></i> {formatDate(task.due_at)}</span>
                            <span><i class="fa-solid fa-image"></i> {task.photos_count}</span>
                            <span><i class="fa-solid fa-link"></i> {task.urls_count}</span>
                        </div>

                        <div class="task-actions">
                            <span class="task-badge {task.is_overdue ? 'danger' : 'normal'}">{getPendingStatus(task)}</span>
                            <button class="primary-btn" on:click={() => openTask(task)}>Abrir tarea</button>
                        </div>
                    </article>
                {/each}
            </div>
        {/if}
    {:else}
        {#if completedTasks.length === 0}
            <div class="tasks-empty">
                <i class="fa-solid fa-folder-open"></i>
                Todavía no hay tareas completadas.
            </div>
        {:else}
            <div class="tasks-grid">
                {#each completedTasks as task}
                    <article class="task-card completed">
                        <div class="task-card-top">
                            <div class="task-class">{task.class_name}</div>
                            <span class="task-role">{getRoleLabel(task.role)}</span>
                        </div>

                        <h2>{task.title}</h2>
                        <p>{task.description || 'Sin descripción'}</p>

                        <div class="task-meta">
                            <span><i class="fa-solid fa-calendar-check"></i> {formatDate(task.delivered_at || task.due_at)}</span>
                            {#if task.grade}
                                <span><i class="fa-solid fa-star"></i> Nota: {task.grade}</span>
                            {/if}
                        </div>

                        <div class="task-actions">
                            <span class="task-badge normal">Completada</span>
                            <button class="primary-btn" on:click={() => openTask(task)}>Ver detalle</button>
                        </div>
                    </article>
                {/each}
            </div>
        {/if}
    {/if}
</div>
