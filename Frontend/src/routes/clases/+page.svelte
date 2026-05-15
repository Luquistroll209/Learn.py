<script lang="ts">
    import { onMount } from "svelte";
    import { browser } from "$app/environment";
    import { urlip, urlMedia } from "$lib/config";
    import imgDefault from "$lib/images/classDefault.webp";
    import "$lib/style/Clases.css";
    import { fetchWithRateLimit } from "$lib/utils/fetchWithRateLimit";
    import { goto } from "$app/navigation";

    type CalendarTask = {
        id: number;
        title: string;
        description?: string;
        clase_id: string;
        class_name: string;
        role: "student" | "teacher" | "assistant";
        due_at: string | null;
        delivered_at: string | null;
        priority: "high" | "medium" | "low" | "overdue";
        status: "pending" | "completed";
        is_overdue?: boolean;
    };

    type CalendarDay = {
        key: string;
        date: Date;
        day: number;
        isCurrentMonth: boolean;
        isToday: boolean;
        tasks: CalendarTask[];
    };

    let clases: any[] = [];
    let desplegado: number | null = null;
    let isLoading = true;
    let showCalendar = false;
    let isCalendarLoading = false;
    let calendarTasks: CalendarTask[] = [];

    // Fecha actual para el dashboard
    const currentDate = new Date();
    let calendarDate = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        1,
    );
    const dayNames = [
        "Domingo",
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
    ];
    const monthNames = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ];

    const dayName = dayNames[currentDate.getDay()];
    const dayNumber = currentDate.getDate();
    const monthName = monthNames[currentDate.getMonth()];
    const year = currentDate.getFullYear();
    const formattedDate = `${dayName}, ${dayNumber} de ${monthName} de ${year}`;

    let recentActivity: any[] = [];
    let upcomingTasks: any[] = [];
    $: calendarDays = buildCalendarDays(calendarDate, calendarTasks);
    $: calendarMonthLabel = calendarDate.toLocaleDateString("es-ES", {
        month: "long",
        year: "numeric",
    });
    $: visibleCalendarTasks = calendarTasks
        .filter((task) => {
            const date = task.due_at || task.delivered_at;
            if (!date) return false;
            const taskDate = new Date(date);
            return (
                taskDate.getFullYear() === calendarDate.getFullYear() &&
                taskDate.getMonth() === calendarDate.getMonth()
            );
        })
        .sort(
            (a, b) =>
                new Date(a.due_at || a.delivered_at || 0).getTime() -
                new Date(b.due_at || b.delivered_at || 0).getTime(),
        );

    // Estadísticas
    let totalClases = 0;
    let tareasPendientes = 0;
    let tareasCompletadas = 0;
    let promedioGeneral: string | number = "-";

    function toggleMenu(index: number) {
        desplegado = desplegado === index ? null : index;
    }

    function verTareas(id?: string | number) {
        if (!browser) return;
        if (id) {
            window.location.href = `/clases/tareas?clase=${id}`;
            return;
        }
        window.location.href = "/clases/tareas";
    }

    function configurarClase(id: string | number, name: string) {
        goto(`/clases/clase-${id}/dashboard`);
    }

    function invitarClase(id: string | number, name: string) {
        goto(`/clases/clase-${id}/dashboard`);
    }

    function crearNuevaClase() {
        if (browser) {
            window.location.href = "/clases/createClass/";
        }
    }

    async function abrirCalendario() {
        showCalendar = true;
        await loadCalendarTasks();
    }

    function cerrarCalendario() {
        showCalendar = false;
    }

    function changeCalendarMonth(offset: number) {
        calendarDate = new Date(
            calendarDate.getFullYear(),
            calendarDate.getMonth() + offset,
            1,
        );
    }

    function goToCurrentMonth() {
        calendarDate = new Date(
            currentDate.getFullYear(),
            currentDate.getMonth(),
            1,
        );
    }

    function getTaskDateKey(task: CalendarTask): string {
        return getDateKey(task.due_at || task.delivered_at);
    }

    function getDateKey(value: string | Date | null | undefined): string {
        if (!value) return "";
        const date = value instanceof Date ? value : new Date(value);
        if (Number.isNaN(date.getTime())) return "";
        const year = date.getFullYear();
        const month = `${date.getMonth() + 1}`.padStart(2, "0");
        const day = `${date.getDate()}`.padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    function buildCalendarDays(
        monthDate: Date,
        tasks: CalendarTask[],
    ): CalendarDay[] {
        const year = monthDate.getFullYear();
        const month = monthDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const startOffset = (firstDay.getDay() + 6) % 7;
        const gridStart = new Date(year, month, 1 - startOffset);
        const todayKey = getDateKey(currentDate);
        const days: CalendarDay[] = [];

        for (let index = 0; index < 42; index += 1) {
            const date = new Date(
                gridStart.getFullYear(),
                gridStart.getMonth(),
                gridStart.getDate() + index,
            );
            const key = getDateKey(date);
            days.push({
                key,
                date,
                day: date.getDate(),
                isCurrentMonth: date.getMonth() === month,
                isToday: key === todayKey,
                tasks: tasks.filter((task) => getTaskDateKey(task) === key),
            });
        }

        return days;
    }

    function formatCalendarTaskTime(value: string | null): string {
        if (!value) return "Sin hora";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "";
        return date.toLocaleTimeString("es-ES", {
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function openCalendarTask(task: CalendarTask) {
        if (!browser) return;
        window.location.href = `/clases/clase-${task.clase_id}/tarea-${task.id}`;
    }

    function verDetallesClase(id: string | number) {
        if (browser) {
            window.location.href = `/clases/clase-${id}`;
        }
    }

    function getClassImageSource(clase: any): string {
        if (!clase?.imagen_url) return imgDefault;
        if (
            String(clase.imagen_url).startsWith("http://") ||
            String(clase.imagen_url).startsWith("https://")
        ) {
            return clase.imagen_url;
        }
        return `${urlMedia.replace(/\/+$/, "")}/${String(clase.imagen_url).replace(/^\/+/, "")}`;
    }

    async function loadCalendarTasks() {
        const token = localStorage.getItem("token");
        if (!token) return;

        isCalendarLoading = true;
        try {
            const response = await fetchWithRateLimit(
                `${urlip}class/obtainUserTasks/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                        authorization: token,
                    },
                },
            );
            const data = await response.json();
            if (!response.ok) {
                calendarTasks = [];
                return;
            }

            calendarTasks = [
                ...(Array.isArray(data.pending_tasks)
                    ? data.pending_tasks
                    : []),
                ...(Array.isArray(data.completed_tasks)
                    ? data.completed_tasks
                    : []),
            ].filter((task) => task.due_at || task.delivered_at);
        } catch (error) {
            calendarTasks = [];
        } finally {
            isCalendarLoading = false;
        }
    }

    // Función original para cargar clases
    async function loadClass() {
        const token = localStorage.getItem("token");

        const response = await fetchWithRateLimit(
            `${urlip}class/obtainClass/`,
            {
                method: "get",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    authorization: `${token}`,
                },
            },
        );

        const data = await response.json();

        if (response.ok) {
            clases = data.clases || [];

            const stats = data.stats || {};
            totalClases = Number(stats.active_classes ?? clases.length ?? 0);
            tareasCompletadas = Number(stats.completed_tasks ?? 0);
            tareasPendientes = Number(stats.pending_tasks ?? 0);
            promedioGeneral = stats.average_grade ?? "-";

            recentActivity = Array.isArray(data.recent_activity)
                ? data.recent_activity
                : [];
            upcomingTasks = Array.isArray(data.upcoming_tasks)
                ? data.upcoming_tasks
                : [];
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
            const token = localStorage.getItem("token");
            if (!token) {
                window.location.href = "/auth/login";
            } else {
                loadClass().finally(() => {
                    isLoading = false;
                });
            }
        }
    });
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
                <button
                    class="quick-action-btn secondary"
                    on:click={abrirCalendario}
                >
                    <i class="fa-solid fa-calendar"></i>
                    Calendario
                </button>
                <button
                    class="reload-btn"
                    on:click={recargarClases}
                    title="Recargar clases"
                >
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
                    <button class="view-all" on:click={recargarClases}
                        >Actualizar</button
                    >
                </div>

                {#if clases.length === 0}
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fa-solid fa-book"></i>
                        </div>
                        <div class="empty-text">
                            No tienes clases registradas
                        </div>
                        <button
                            class="quick-action-btn"
                            on:click={crearNuevaClase}
                        >
                            <i class="fa-solid fa-plus"></i>
                            Crear mi primera clase
                        </button>
                    </div>
                {:else}
                    <div class="clases-grid">
                        {#each clases as clase, i}
                            <div class="clase-card">
                                <div class="clase-img-container">
                                    <div
                                        class="clase-link-overlay"
                                        on:click={() =>
                                            verDetallesClase(clase.id)}
                                    >
                                        {#if clase.imagen_url}
                                            <img
                                                src={getClassImageSource(clase)}
                                                alt={clase.name}
                                                class="portada"
                                            />
                                        {:else}
                                            <div
                                                class="default-class-bg"
                                                style="background: #1a73e8"
                                            ></div>
                                        {/if}

                                        <div class="clase-header-overlay">
                                            <h3 class="clase-title">
                                                {clase.name}
                                            </h3>

                                            <p class="clase-teacher">
                                                {clase.teacher_name ||
                                                    clase.teacher}
                                            </p>
                                        </div>

                                        <!-- Badge de tareas pendientes -->
                                        {#if (clase.pending_tasks || clase.tareas_pendientes || 0) > 0}
                                            <div class="class-info">
                                                <i class="fa-solid fa-clock"
                                                ></i>
                                                {clase.pending_tasks ||
                                                    clase.tareas_pendientes} pendiente{(clase.pending_tasks ||
                                                    clase.tareas_pendientes) > 1
                                                    ? "s"
                                                    : ""}
                                            </div>
                                        {/if}
                                    </div>
                                    <button
                                        class="clase-options"
                                        on:click|stopPropagation={() =>
                                            toggleMenu(i)}
                                    >
                                        <i class="fa-solid fa-ellipsis-vertical"
                                        ></i>
                                    </button>
                                    {#if desplegado === i}
                                        <div class="menu">
                                            <button
                                                on:click|stopPropagation={() =>
                                                    configurarClase(
                                                        clase.id,
                                                        clase.name,
                                                    )}
                                            >
                                                <i class="fa-solid fa-gear"></i>
                                                Configurar
                                            </button>
                                            <button
                                                on:click|stopPropagation={() =>
                                                    invitarClase(
                                                        clase.id,
                                                        clase.name,
                                                    )}
                                            >
                                                <i class="fa-solid fa-user-plus"
                                                ></i>
                                                Invitar
                                            </button>
                                        </div>
                                    {/if}
                                </div>

                                <div class="clase-footer">
                                    <button
                                        class="footer-icon-btn"
                                        on:click|stopPropagation={() =>
                                            verTareas(clase.id)}
                                        title="Próximas tareas"
                                    >
                                        <i class="fa-solid fa-list-check"></i>
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
                        {monthName}
                        {year}
                    </div>
                </div>

                <!-- Upcoming Tasks -->
                <div class="card">
                    <div class="card-title">
                        <i class="fa-solid fa-clock-rotate-left"></i>
                        Próximas Entregas
                        <button class="view-all" on:click={() => verTareas()}
                            >Ver todas</button
                        >
                    </div>
                    {#if upcomingTasks.length === 0}
                        <div class="activity-message">
                            No hay entregas próximas.
                        </div>
                    {:else}
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
                    {/if}
                </div>

                <!-- Recent Activity -->
                <div class="card">
                    <div class="card-title">
                        <i class="fa-solid fa-bell"></i>
                        Actividad Reciente
                    </div>
                    {#if recentActivity.length === 0}
                        <div class="activity-message">
                            Todavía no hay actividad reciente.
                        </div>
                    {:else}
                        {#each recentActivity as activity}
                            <div class="activity-item">
                                <div class="activity-icon {activity.type}">
                                    {#if activity.type === "grade"}
                                        <i class="fa-solid fa-star"></i>
                                    {:else if activity.type === "announcement"}
                                        <i class="fa-solid fa-bullhorn"></i>
                                    {:else if activity.type === "task"}
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
                                    <div class="activity-message">
                                        {activity.message}
                                    </div>
                                    <div class="activity-time">
                                        <i class="fa-solid fa-clock"></i>
                                        {activity.time}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>
        </div>
    {/if}
</div>

{#if showCalendar}
    <div class="calendar-overlay" on:click={cerrarCalendario}>
        <section class="calendar-panel" on:click|stopPropagation>
            <button
                class="calendar-close"
                on:click={cerrarCalendario}
                aria-label="Cerrar calendario"
            >
                ×
            </button>

            <div class="calendar-panel-header">
                <div>
                    <span>Calendario</span>
                    <h2>{calendarMonthLabel}</h2>
                </div>
                <div class="calendar-controls">
                    <button
                        on:click={() => changeCalendarMonth(-1)}
                        aria-label="Mes anterior"
                    >
                        <i class="fa-solid fa-chevron-left"></i>
                    </button>
                    <button class="calendar-today-btn" on:click={goToCurrentMonth}>
                        Hoy
                    </button>
                    <button
                        on:click={() => changeCalendarMonth(1)}
                        aria-label="Mes siguiente"
                    >
                        <i class="fa-solid fa-chevron-right"></i>
                    </button>
                </div>
            </div>

            {#if isCalendarLoading}
                <div class="calendar-loading">
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    Cargando tareas...
                </div>
            {:else}
                <div class="calendar-weekdays">
                    <span>Lun</span>
                    <span>Mar</span>
                    <span>Mié</span>
                    <span>Jue</span>
                    <span>Vie</span>
                    <span>Sáb</span>
                    <span>Dom</span>
                </div>

                <div class="calendar-grid">
                    {#each calendarDays as day}
                        <div
                            class:muted={!day.isCurrentMonth}
                            class:today={day.isToday}
                            class="calendar-cell"
                        >
                            <div class="calendar-cell-number">{day.day}</div>
                            <div class="calendar-cell-tasks">
                                {#each day.tasks.slice(0, 3) as task}
                                    <button
                                        class="calendar-task {task.status} {task.priority}"
                                        on:click={() => openCalendarTask(task)}
                                        title={task.title}
                                    >
                                        <span>{task.title}</span>
                                    </button>
                                {/each}
                                {#if day.tasks.length > 3}
                                    <div class="calendar-more">
                                        +{day.tasks.length - 3} más
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>

                <aside class="calendar-agenda">
                    <div class="calendar-agenda-title">
                        Tareas de {calendarMonthLabel}
                    </div>
                    {#if visibleCalendarTasks.length === 0}
                        <div class="calendar-empty">
                            No hay tareas con fecha este mes.
                        </div>
                    {:else}
                        {#each visibleCalendarTasks as task}
                            <button
                                class="calendar-agenda-item {task.status}"
                                on:click={() => openCalendarTask(task)}
                            >
                                <div>
                                    <strong>{task.title}</strong>
                                    <span>{task.class_name}</span>
                                </div>
                                <small>
                                    {formatCalendarTaskTime(
                                        task.due_at || task.delivered_at,
                                    )}
                                </small>
                            </button>
                        {/each}
                    {/if}
                </aside>
            {/if}
        </section>
    </div>
{/if}
