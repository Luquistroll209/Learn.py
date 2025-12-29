<script lang="ts">
    import { onMount } from 'svelte';
    
    const classes = [
        { 
            id: 1, 
            name: 'Programación Web Avanzada', 
            teacher: 'Prof. García', 
            color: '#1a73e8',
            pending: 2,
            nextTask: 'Proyecto Final',
            image: '💻'
        },
        { 
            id: 2, 
            name: 'Bases de Datos', 
            teacher: 'Prof. Martínez', 
            color: '#34a853',
            pending: 1,
            nextTask: 'Práctica SQL',
            image: '🗄️'
        },
        { 
            id: 3, 
            name: 'Diseño de Interfaces', 
            teacher: 'Prof. López', 
            color: '#ea4335',
            pending: 3,
            nextTask: 'Mockup App',
            image: '🎨'
        },
        { 
            id: 4, 
            name: 'Algoritmos', 
            teacher: 'Prof. Sánchez', 
            color: '#fbbc05',
            pending: 0,
            nextTask: 'Sin tareas',
            image: '🧮'
        }
    ];
    
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
</script>

<style>
    :root {
        --primary-color: #1a73e8;
        --primary-dark: #0d47a1;
        --text-color: #202124;
        --text-light: #5f6368;
        --background: #ffffff;
        --background-hover: #f1f3f4;
        --border-color: #dadce0;
        --shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
        --shadow-heavy: 0 4px 12px rgba(0, 0, 0, 0.15);
        --success-color: #34a853;
        --warning-color: #fbbc05;
        --error-color: #ea4335;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }
    
    body {
        background-color: #f8f9fa;
        padding: 20px;
    }
    
    .dashboard-container {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header del Dashboard */
    .dashboard-header {
        margin-bottom: 30px;
    }
    
    .welcome-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .welcome-text h1 {
        font-size: 32px;
        color: var(--text-color);
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .welcome-text p {
        color: var(--text-light);
        font-size: 16px;
    }
    
    .quick-actions {
        display: flex;
        gap: 12px;
    }
    
    .quick-action-btn {
        padding: 12px 24px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
    }
    
    .quick-action-btn:hover {
        background: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(26, 115, 232, 0.4);
    }
    
    .quick-action-btn.secondary {
        background: white;
        color: var(--primary-color);
        border: 2px solid var(--primary-color);
        box-shadow: var(--shadow);
    }
    
    .quick-action-btn.secondary:hover {
        background: rgba(26, 115, 232, 0.08);
    }
    
    /* Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: var(--shadow);
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-heavy);
    }
    
    .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 16px;
    }
    
    .stat-icon.blue { background: #e3f2fd; }
    .stat-icon.green { background: #e8f5e9; }
    .stat-icon.orange { background: #fff3e0; }
    .stat-icon.red { background: #ffebee; }
    
    .stat-value {
        font-size: 36px;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 4px;
    }
    
    .stat-label {
        font-size: 14px;
        color: var(--text-light);
        font-weight: 500;
    }
    
    /* Main Grid */
    .main-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 20px;
    }
    
    /* Classes Grid */
    .classes-section {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: var(--shadow);
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-color);
    }
    
    .view-all {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
        font-size: 14px;
        transition: color 0.2s;
    }
    
    .view-all:hover {
        color: var(--primary-dark);
    }
    
    .classes-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }
    
    .class-card {
        position: relative;
        padding: 24px;
        border-radius: 12px;
        color: white;
        cursor: pointer;
        transition: transform 0.2s;
        overflow: hidden;
    }
    
    .class-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 150px;
        height: 150px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        transform: translate(30%, -30%);
    }
    
    .class-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }
    
    .class-emoji {
        font-size: 48px;
        margin-bottom: 12px;
    }
    
    .class-name {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }
    
    .class-teacher {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 16px;
    }
    
    .class-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .pending-badge {
        background: rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    .next-task {
        font-size: 12px;
        opacity: 0.9;
    }
    
    /* Right Sidebar */
    .sidebar-section {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: var(--shadow);
    }
    
    .card-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 16px;
    }
    
    /* Activity Feed */
    .activity-item {
        display: flex;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: background 0.2s;
    }
    
    .activity-item:hover {
        background: var(--background-hover);
    }
    
    .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    
    .activity-icon.grade { background: #e8f5e9; }
    .activity-icon.announcement { background: #e3f2fd; }
    .activity-icon.task { background: #fff3e0; }
    .activity-icon.material { background: #f3e5f5; }
    
    .activity-content {
        flex: 1;
    }
    
    .activity-class {
        font-weight: 600;
        font-size: 13px;
        color: var(--primary-color);
        margin-bottom: 2px;
    }
    
    .activity-message {
        font-size: 13px;
        color: var(--text-color);
        margin-bottom: 4px;
        line-height: 1.4;
    }
    
    .activity-time {
        font-size: 11px;
        color: var(--text-light);
    }
    
    /* Upcoming Tasks */
    .task-list-item {
        padding: 14px;
        border-left: 3px solid var(--border-color);
        background: #fafafa;
        border-radius: 6px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    
    .task-list-item:hover {
        border-left-color: var(--primary-color);
        background: white;
        box-shadow: var(--shadow);
    }
    
    .task-list-item.high {
        border-left-color: var(--error-color);
        background: #ffebee;
    }
    
    .task-list-item.medium {
        border-left-color: var(--warning-color);
        background: #fffbf0;
    }
    
    .task-list-item.low {
        border-left-color: var(--success-color);
        background: #e8f5e9;
    }
    
    .task-class-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--primary-color);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .task-list-title {
        font-weight: 500;
        color: var(--text-color);
        font-size: 14px;
        margin-bottom: 6px;
    }
    
    .task-list-date {
        font-size: 12px;
        color: var(--text-light);
    }
    
    /* Calendar Widget */
    .mini-calendar {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    
    .calendar-date {
        font-size: 48px;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 4px;
    }
    
    .calendar-day {
        font-size: 16px;
        opacity: 0.9;
        margin-bottom: 12px;
    }
    
    .calendar-month {
        font-size: 14px;
        opacity: 0.8;
    }
    
    /* Responsive */
    @media (max-width: 1200px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .main-grid {
            grid-template-columns: 1fr;
        }
        
        .classes-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        body {
            padding: 12px;
        }
        
        .welcome-section {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
        }
        
        .welcome-text h1 {
            font-size: 24px;
        }
        
        .quick-actions {
            width: 100%;
            flex-direction: column;
        }
        
        .quick-action-btn {
            width: 100%;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .classes-grid {
            grid-template-columns: 1fr;
        }
    }
</style>

<div class="dashboard-container">
    <!-- Header -->
    <div class="dashboard-header">
        <div class="welcome-section">
            <div class="welcome-text">
                <h1>¡Bienvenido de nuevo! 👋</h1>
                <p>Lunes, 29 de Diciembre de 2025</p>
            </div>
            <div class="quick-actions">
                <button class="quick-action-btn">+ Nueva Clase</button>
                <button class="quick-action-btn secondary">📅 Calendario</button>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon blue">📚</div>
                <div class="stat-value">4</div>
                <div class="stat-label">Clases activas</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green">✅</div>
                <div class="stat-value">12</div>
                <div class="stat-label">Tareas completadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon orange">⏰</div>
                <div class="stat-value">6</div>
                <div class="stat-label">Tareas pendientes</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon red">⭐</div>
                <div class="stat-value">9.2</div>
                <div class="stat-label">Promedio general</div>
            </div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-grid">
        <!-- Classes Section -->
        <div class="classes-section">
            <div class="section-header">
                <h2 class="section-title">Mis Clases</h2>
                <a href="#" class="view-all">Ver todas →</a>
            </div>
            
            <div class="classes-grid">
                {#each classes as cls}
                    <div class="class-card" style="background: {cls.color};">
                        <div class="class-emoji">{cls.image}</div>
                        <div class="class-name">{cls.name}</div>
                        <div class="class-teacher">{cls.teacher}</div>
                        <div class="class-footer">
                            {#if cls.pending > 0}
                                <span class="pending-badge">{cls.pending} pendiente{cls.pending > 1 ? 's' : ''}</span>
                            {:else}
                                <span class="pending-badge">Al día</span>
                            {/if}
                            <span class="next-task">{cls.nextTask}</span>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
        
        <!-- Right Sidebar -->
        <div class="sidebar-section">
            <!-- Calendar -->
            <div class="mini-calendar">
                <div class="calendar-date">29</div>
                <div class="calendar-day">Lunes</div>
                <div class="calendar-month">Diciembre 2025</div>
            </div>
            
            <!-- Upcoming Tasks -->
            <div class="card">
                <div class="card-title">Próximas Entregas 📌</div>
                {#each upcomingTasks as task}
                    <div class="task-list-item {task.priority}">
                        <div class="task-class-label">{task.class}</div>
                        <div class="task-list-title">{task.title}</div>
                        <div class="task-list-date">📅 {task.date}</div>
                    </div>
                {/each}
            </div>
            
            <!-- Recent Activity -->
            <div class="card">
                <div class="card-title">Actividad Reciente 🔔</div>
                {#each recentActivity as activity}
                    <div class="activity-item">
                        <div class="activity-icon {activity.type}">
                            {activity.type === 'grade' ? '⭐' : 
                             activity.type === 'announcement' ? '📢' : 
                             activity.type === 'task' ? '📝' : '📚'}
                        </div>
                        <div class="activity-content">
                            <div class="activity-class">{activity.class}</div>
                            <div class="activity-message">{activity.message}</div>
                            <div class="activity-time">{activity.time}</div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    </div>
</div>