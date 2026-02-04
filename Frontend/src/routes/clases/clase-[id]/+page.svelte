<script lang="ts">
    import { onMount } from 'svelte';
    import type { PageLoad } from './$types';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';
    import "$lib/style/createClass.css";

    let activeTab = 'tablón';
    let showTaskModal = false;
    let showAnnouncementModal = false;
    import "$lib/style/inClass.css";
    import imgDefault from '$lib/images/classDefault.webp';

    import { browser } from '$app/environment';
    import { redirect } from '@sveltejs/kit';
    import { urlip, urlMedia } from '$lib/config';

    let clase: any[] = [];

    import { invalidate } from '$app/navigation';
    let students: any[] = [];
    let teachers: any[] = [];
    //variables y objetos para obtener la ID
    import { page } from '$app/stores';
    let id;
    $: id = $page.params.id;

    let showInviteModal = false;
    let showCreateNews = false;
    let showCreateTask = false;

    let areYouTeacher = false;
    let username = null;

    let inviteEmail = '';

    // anuncios
    let announcements: any[] = [];
    let newsTitle = '';
    let newsDescription = '';
    let newsUrls = '';
    let newsImages: File[] = [];
    let isSubmitting = false;

    // tareas (frontend-only)
    let taskTitle = '';
    let taskDueDate = '';
    let taskStatus = 'pendiente';
    let taskMaxGrade = '10';
    let taskDescription = '';
    let taskUrls = '';
    let taskImages: File[] = [];

    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                //throw redirect(302, '/auth/login');
                window.location.href = '/auth/login';
            } else {
                loadClass().then(loadAnnouncements);
            }
        }
    });

    async function loadClass() {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('userData');
        /*
        if (userData) {
            const user = JSON.parse(userData);
            username = `${user.name}`;
        }  
        console.log(username);
        */
        
        const respose = await fetch(`${urlip}class/obtainClassByID/${id}`, {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
            });

            const data = await respose.json();

            if (respose.ok){
                clase = data || [];    
                students = [];
                teachers = [];
                console.log(clase);
                for (let i = 0; i < clase.students_info.length; i++) {
                    if (clase.students_info[i].role === "student") {
                        const studentWithAvatar = {
                            ...clase.students_info[i],
                            avatar: `${clase.students_info[i].username.charAt(0)}`.toUpperCase()
                        };
                        
                        students.push(studentWithAvatar);
                    } else if (clase.students_info[i].role === "teacher" || clase.students_info[i].role === "assistant" ){
                        const TeachersWithAvatar = {
                            ...clase.students_info[i],
                            avatar: `${clase.students_info[i].username.charAt(0)}`.toUpperCase()
                        };
                        
                        teachers.push(TeachersWithAvatar);
                    }
                }//teachers
            }/*else{
                showAlert("Error", "Error", "red");
            }*/
    }

    async function loadAnnouncements() {
        const token = localStorage.getItem('token');
        const response = await fetch(`${urlip}class/obtainAnnouncements/${id}/`, {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'authorization': `${token}`
            }
        });

        const data = await response.json();
        if (response.ok) {
            announcements = data.announcements || [];
        } else {
            showAlert("Error", data?.Error || "No se pudieron cargar los anuncios", "red");
        }
    }

    function handleNewsFiles(event: Event) {
        const target = event.currentTarget as HTMLInputElement;
        const files = target.files ? Array.from(target.files) : [];
        newsImages = files;
    }

    async function createNews() {
        if (!newsTitle.trim() || !newsDescription.trim()) {
            showAlert("Error", "Título y descripción son obligatorios", "orange");
            return;
        }

        const token = localStorage.getItem('token');
        const urlsArray = newsUrls
            .split(/\n|,/)
            .map((u) => u.trim())
            .filter(Boolean);

        const formData = new FormData();
        formData.append('clase_id', id);
        formData.append('title', newsTitle.trim());
        formData.append('description', newsDescription.trim());
        formData.append('urls', JSON.stringify(urlsArray));

        for (const file of newsImages) {
            formData.append('photos', file);
        }

        isSubmitting = true;
        const response = await fetch(`${urlip}class/createAnnouncement/`, {
            method: 'POST',
            headers: {
                'authorization': `${token}`
            },
            body: formData
        });

        const data = await response.json();
        isSubmitting = false;

        if (response.ok) {
            showAlert("Listo", "Anuncio creado", "green");
            showCreateNews = false;
            newsTitle = '';
            newsDescription = '';
            newsUrls = '';
            newsImages = [];
            await loadAnnouncements();
        } else {
            showAlert("Error", data?.Error || "No se pudo crear el anuncio", "red");
        }
    }
    /*
    let tasks: any[] = [
        { id: 1, title: 'Práctica 1: Introducción a Svelte', dueDate: '5 Ene', status: 'entregada', grade: '9.5', maxGrade: '10' },
        { id: 2, title: 'Proyecto Final - Primera Entrega', dueDate: '15 Ene', status: 'pendiente', grade: '-', maxGrade: '10' },
        { id: 3, title: 'Ejercicios Tema 2', dueDate: '20 Ene', status: 'pendiente', grade: '-', maxGrade: '10' },
        { id: 4, title: 'Lectura: Componentes Reactivos', dueDate: '25 Ene', status: 'atrasada', grade: '-', maxGrade: '5' }
    ];
    */
    const materials = [
        { id: 1, title: 'Tema 1: Introducción', type: 'pdf', size: '2.4 MB', date: '1 Dic' },
        { id: 2, title: 'Tema 2: Componentes', type: 'pdf', size: '3.1 MB', date: '8 Dic' },
        { id: 3, title: 'Ejercicios prácticos', type: 'zip', size: '1.2 MB', date: '15 Dic' },
        { id: 4, title: 'Video: Tutorial Svelte', type: 'video', size: '45 MB', date: '20 Dic' }
    ];
    
    const grades = [
        { task: 'Práctica 1: Introducción a Svelte', grade: '9.5', maxGrade: '10', percentage: '95%', date: '10 Dic' },
        { task: 'Examen Tema 1', grade: '8.0', maxGrade: '10', percentage: '80%', date: '5 Dic' },
        { task: 'Participación en clase', grade: '10', maxGrade: '10', percentage: '100%', date: '30 Nov' }
    ];
    /*
    const students = [
        { id: 1, name: 'Ana Martínez', email: 'ana@example.com', avatar: 'AM' },
        { id: 2, name: 'Carlos López', email: 'carlos@example.com', avatar: 'CL' },
        { id: 3, name: 'María García', email: 'maria@example.com', avatar: 'MG' },
        { id: 4, name: 'Juan Pérez', email: 'juan@example.com', avatar: 'JP' }
    ];
    */
    async function invitarAlumno() {
        if (!inviteEmail) return;
        
        const token = localStorage.getItem('token');
        
        try {
            const response = await fetch(`${urlip}class/invite/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `${token}`
                },
                body: JSON.stringify({
                    clase_id: id, 
                    email: inviteEmail 
                })
            });
            
            if (response.ok) {
                showAlert("Usuario invitado con exito", inviteEmail, "green");

                inviteEmail = '';
                showInviteModal = false;
                //  await loadAlumnos(token!);
            } else {
                const errorData = await response.json();
                showAlert("Error", errorData.Error, "red");
            }
        } catch (error) {
            //console.error('Error:', error);
            alert('Error al enviar la invitación');
        }
    }

    function createTask() {
        if (!taskTitle.trim()) {
            showAlert("Error", "El título es obligatorio", "orange");
            return;
        }

        const urlsArray = taskUrls
            .split(/\n|,/)
            .map((u) => u.trim())
            .filter(Boolean);

        const newTask = {
            id: Date.now(),
            title: taskTitle.trim(),
            dueDate: taskDueDate || 'Sin fecha',
            status: taskStatus,
            grade: '-',
            maxGrade: taskMaxGrade || '10',
            description: taskDescription.trim(),
            urls: urlsArray,
            photos: taskImages
        };

        tasks = [newTask, ...tasks];
        taskTitle = '';
        taskDueDate = '';
        taskStatus = 'pendiente';
        taskMaxGrade = '10';
        taskDescription = '';
        taskUrls = '';
        taskImages = [];
        showCreateTask = false;
        showAlert("Listo", "Tarea creada (solo frontend)", "green");
    }

    function handleTaskFiles(event: Event) {
        const target = event.currentTarget as HTMLInputElement;
        const files = target.files ? Array.from(target.files) : [];
        taskImages = files;
    }
</script>

<Alert />

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
                    <label style="display: block; margin-bottom: 8px; color: var(--text-color);">Correo Electrónico</label>
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
{#if showCreateNews}
    <div class="modal-overlay" on:click={() => showCreateNews = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showCreateNews = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Nuevo anuncio</h2>
                <p>Publica una actualización para la clase</p>
            </div>
            
            <form on:submit|preventDefault={createNews}>
                <div class="form-group">
                    <label for="newsTitle">Título</label>
                    <input 
                        id="newsTitle" 
                        placeholder="Introduce el título" 
                        type="text"
                        bind:value={newsTitle}
                        required
                    >
                </div>
                
                <div class="form-group">
                    <label for="newsDescription">Descripción</label>
                    <textarea 
                        id="newsDescription" 
                        placeholder="Describe el anuncio..." 
                        bind:value={newsDescription}
                        rows="4"
                    ></textarea>
                </div>

                <div class="form-group">
                    <label for="newsUrls">URLs (opcional)</label>
                    <textarea 
                        id="newsUrls" 
                        placeholder="Una por línea o separadas por coma" 
                        bind:value={newsUrls}
                        rows="3"
                    ></textarea>
                </div>
                
                <div class="form-group">
                    <label for="newsImages">Imágenes</label>
                    <div class="image-upload-area">
                        <input 
                            id="newsImages" 
                            type="file" 
                            accept="image/*"
                            multiple
                            on:change={handleNewsFiles}
                        >
                        <div class="upload-placeholder">
                            <div class="upload-icon">Subir imagen</div>
                            <div class="upload-text">Arrastra imágenes o haz clic para seleccionar</div>
                        </div>
                    </div>
                    {#if newsImages.length > 0}
                        <div class="files">
                            {#each newsImages as file}
                                <div class="file">{file.name}</div>
                            {/each}
                        </div>
                    {/if}
                </div>
                
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showCreateNews = false}>Cancelar</button>
                    <button class="send-btn" type="submit" disabled={isSubmitting}>
                        {isSubmitting ? 'Publicando...' : 'Publicar'}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

{#if showCreateTask}
    <div class="modal-overlay" on:click={() => showCreateTask = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showCreateTask = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Nueva tarea</h2>
                <p>Agrega una tarea (solo frontend)</p>
            </div>
            
            <form on:submit|preventDefault={createTask}>
                <div class="form-group">
                    <label for="taskTitle">Título</label>
                    <input 
                        id="taskTitle" 
                        placeholder="Introduce el título" 
                        type="text"
                        bind:value={taskTitle}
                        required
                    >
                </div>

                <div class="form-group">
                    <label for="taskDue">Fecha límite</label>
                    <input
                        id="taskDue"
                        type="date"
                        bind:value={taskDueDate}
                    >
                </div>

                <div class="form-group">
                    <label for="taskDesc">Descripción</label>
                    <textarea
                        id="taskDesc"
                        rows="4"
                        placeholder="Describe la tarea..."
                        bind:value={taskDescription}
                    ></textarea>
                </div>

                <div class="form-group">
                    <label for="taskStatus">Estado</label>
                    <select id="taskStatus" bind:value={taskStatus}>
                        <option value="pendiente">Pendiente</option>
                        <option value="entregada">Entregada</option>
                        <option value="atrasada">Atrasada</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="taskMax">Puntaje máximo</label>
                    <input
                        id="taskMax"
                        type="number"
                        min="1"
                        step="1"
                        bind:value={taskMaxGrade}
                    >
                </div>

                <div class="form-group">
                    <label for="taskUrls">URLs (opcional)</label>
                    <textarea
                        id="taskUrls"
                        rows="3"
                        placeholder="Una por línea o separadas por coma"
                        bind:value={taskUrls}
                    ></textarea>
                </div>

                <div class="form-group">
                    <label for="taskImages">Imágenes</label>
                    <div class="image-upload-area">
                        <input
                            id="taskImages"
                            type="file"
                            accept="image/*"
                            multiple
                            on:change={handleTaskFiles}
                        >
                        <div class="upload-placeholder">
                            <div class="upload-icon">Subir imagen</div>
                            <div class="upload-text">Arrastra imágenes o haz clic para seleccionar</div>
                        </div>
                    </div>
                    {#if taskImages.length > 0}
                        <div class="files">
                            {#each taskImages as file}
                                <div class="file">{file.name}</div>
                            {/each}
                        </div>
                    {/if}
                </div>
                
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showCreateTask = false}>Cancelar</button>
                    <button class="send-btn" type="submit">Crear tarea</button>
                </div>
            </form>
        </div>
    </div>
{/if}

<div class="class-container">
    <div class="class-header">
        {#if clase.imagen_url === null}
            <div class="portada"><img src={imgDefault} alt="" class="portada" ></div>
        {:else}
            <div class="portada"><img src={urlMedia}{clase.imagen_url} alt="" class="portada" ></div>
        {/if}
        <div class="class-header-content">
            <h1>{clase.name}</h1>
            <p>{clase.description}</p>
            <p>{clase.teacher_name} • Curso 2024-2025</p>
            <!--<span class="class-code">Código: ABC123</span> posiblemente esto no se añada-->
            <!--El tema de codigos se dejara para ultimo momento ya que no es necesario-->
        </div>
    </div>
    
    <div class="class-tabs">
        <button class="tab-button" class:active={activeTab === 'tablón'} on:click={() => activeTab = 'tablón'}>Tablón</button>
        <button class="tab-button" class:active={activeTab === 'tareas'} on:click={() => activeTab = 'tareas'}>Tareas</button>
        <button class="tab-button" class:active={activeTab === 'personas'} on:click={() => activeTab = 'personas'}>Personas</button>
        <button class="tab-button" class:active={activeTab === 'calificaciones'} on:click={() => activeTab = 'calificaciones'}>Calificaciones</button>
        <!--<button class="tab-button" class:active={activeTab === 'materiales'} on:click={() => activeTab = 'materiales'}>Materiales</button>-->
    </div>
    
    <div class="class-content">
        <div class="main-content">
            {#if activeTab === 'tablón'}
                <div class="card-title">
                    Anuncios recientes
                    <button on:click={() => showCreateNews = true}  class="action-button">+ Nuevo anuncio</button>
                </div>
                
                {#if announcements.length === 0}
                    <div class="announcement-item">
                        <div class="announcement-title">No hay anuncios</div>
                    </div>
                {:else}
                    {#each announcements as announcement}
                        <div class="announcement-item">
                            <div class="announcement-header">
                                <div class="avatar">
                                    {announcement.creator_info?.first_name?.charAt(0)}{announcement.creator_info?.last_name?.charAt(0)}
                                </div>
                                <div class="announcement-meta">
                                    <div class="announcement-author">
                                        {announcement.creator_info?.first_name} {announcement.creator_info?.last_name}
                                    </div>
                                    <div class="announcement-date">{announcement.created_at}</div>
                                </div>
                            </div>
                            <div class="announcement-title">{announcement.title}</div>
                            <div class="announcement-content">{announcement.description}</div>
                            {#if announcement.photos && announcement.photos.length > 0}
                                <div class="announcement-photos">
                                    {#each announcement.photos as photo}
                                        <img src={photo} alt="foto anuncio" />
                                    {/each}
                                </div>
                            {/if}
                            {#if announcement.urls && announcement.urls.length > 0}
                                <div class="announcement-urls">
                                    {#each announcement.urls as link}
                                        <a href={link} target="_blank" rel="noreferrer">{link}</a>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    {/each}
                {/if}
            {/if}
            
            {#if activeTab === 'tareas'}
                <div class="card-title">
                    Todas las tareas
                    <button class="action-button" on:click={() => showCreateTask = true}>+ Crear tarea</button>
                </div>
                
                {#each tasks as task}
                    <div class="task-item">
                        <div class="task-icon">📄</div>
                        <div class="task-info">
                            <div class="task-title">{task.title}</div>
                            <div class="task-due">Fecha límite: {task.dueDate}</div>
                        </div>
                        <span class="task-status {task.status}">
                            {task.status === 'entregada' ? 'Entregada' : task.status === 'pendiente' ? 'Pendiente' : 'Atrasada'}
                        </span>
                        {#if task.grade !== '-'}
                            <div style="margin-left: 16px; font-weight: 600; color: var(--primary-color);">
                                {task.grade}/{task.maxGrade}
                            </div>
                        {/if}
                    </div>
                {/each}
            {/if}
            
            {#if activeTab === 'personas'}
                <div class="card-title">    
                    Profesores
                    <button on:click={() => showInviteModal = true} class="addPerson"><i class="fa-solid fa-person-circle-plus"></i></button>
                </div>
                
                {#each teachers as teacher}
                    <div class="student-item">
                        <div class="avatar">{teacher.avatar}</div>
                        <div class="student-info">
                            <div class="student-name">{teacher.username}</div>
                            <div class="student-email">{teacher.email}</div>
                        </div>
                    </div>
                {/each}
                
                <div class="card-title" style="margin-top: 24px;">
                    Estudiantes ({students.length})
                </div>
                {#each students as student}
                    <div class="student-item">
                        <div class="avatar">{student.avatar}</div>
                        <div class="student-info">
                            <div class="student-name">{student.username}</div>
                            <div class="student-email">{student.email}</div>
                        </div>
                    </div>
                {/each}
            {/if}
            
            {#if activeTab === 'calificaciones'}
                <div class="average-card">
                    <div class="average-label">Tu calificación promedio</div>
                    <div class="average-number">9.2</div>
                </div>
                
                <div class="card-title">Historial de calificaciones</div>
                {#each grades as grade}
                    <div class="grade-item">
                        <div class="grade-info">
                            <div class="grade-task">{grade.task}</div>
                            <div class="grade-date">Calificado el {grade.date}</div>
                        </div>
                        <div class="grade-score">
                            <div class="grade-number">{grade.grade}</div>
                            <div class="grade-percentage">{grade.percentage}</div>
                        </div>
                    </div>
                {/each}
            {/if}
            
            {#if activeTab === 'materiales'}
                <div class="card-title">
                    Recursos del curso
                    <button class="action-button">+ Subir archivo</button>
                </div>
                
                {#each materials as material}
                    <div class="material-item">
                        <div class="material-icon">
                            {material.type === 'pdf' ? '📄' : material.type === 'video' ? '🎥' : '📦'}
                        </div>
                        <div class="material-info">
                            <div class="material-title">{material.title}</div>
                            <div class="material-meta">{material.size} • Subido el {material.date}</div>
                        </div>
                    </div>
                {/each}
            {/if}
        </div>
        

        <div class="sidebar">
            <div class="card">
                <div class="card-title">Próximas entregas</div>
                <div class="upcoming-item">
                    <div class="upcoming-title">Proyecto Final - Primera Entrega</div>
                    <div class="upcoming-date">15 de Enero</div>
                </div>
                <div class="upcoming-item">
                    <div class="upcoming-title">Ejercicios Tema 2</div>
                    <div class="upcoming-date">20 de Enero</div>
                </div>
            </div>
            <!--
            <div class="card">
                <div class="card-title">Código de clase</div>
                <div style="text-align: center; padding: 16px; background: var(--background-hover); border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: 700; color: var(--primary-color); margin-bottom: 8px;">
                        ABC123
                    </div>
                    <button class="secondary-button">Copiar código</button>
                </div>
            </div>
            -->
            <div class="card">
                <div class="card-title">Acciones rápidas</div>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;">
                    Enviar correo
                </button>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;">
                    Ver calendario
                </button>
                <a href="/clases/clase-{id}/dashboard" class="secondary-button" style="width: 100%;">
                    Configuración
                </a>
            </div>
        </div>
    </div>
</div>
