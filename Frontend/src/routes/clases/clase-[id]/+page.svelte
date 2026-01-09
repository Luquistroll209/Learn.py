<script lang="ts">
    import { onMount } from 'svelte';
    import type { PageLoad } from './$types';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';

    
    let activeTab = 'tablón';
    let showTaskModal = false;
    let showAnnouncementModal = false;
    import "$lib/style/inClass.css"
    import imgDefault from '$lib/images/classDefault.webp'
    
    import { browser } from '$app/environment';
    import { redirect } from '@sveltejs/kit';
    import { urlip } from '$lib/config';
    let clase: any[] = [];
    
    import { classicNameResolver } from 'typescript';
    import { invalidate } from '$app/navigation';
    let students: any[] = [];
    let teachers: any[] = [];
    //variables y objetos para obtener la ID
    import { page } from '$app/stores';
    let id;
    $: id = $page.params.id;

    let showInviteModal = false;
	

    let areYouTeacher = false;
    let username = null;

    let inviteEmail = '';
    
    
    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                //throw redirect(302, '/auth/login');
                window.location.href = '/auth/login';

            } else {
                loadClass();
            }
        }
    });

    async function loadClass(){
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
                console.log(clase)
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


    const announcements = [
        { id: 1, author: 'Profesor1', title: 'Bienvenidos al curso', date: '15 Dic', content: 'Bienvenidos a la clase de Programación Web. Espero que tengamos un gran semestre.', avatar: 'PG' },
        { id: 2, author: 'Profesor1', title: 'Examen próximo', date: '20 Dic', content: 'Recordatorio: El examen del tema 3 será el próximo viernes.', avatar: 'PG' },
        { id: 3, author: 'alumno', title: 'Titulo del mensaje de alumno', date: '28 Dic', content: 'mensaje', avatar: 'A1' }
    ];
    
    const tasks = [
        { id: 1, title: 'Práctica 1: Introducción a Svelte', dueDate: '5 Ene', status: 'entregada', grade: '9.5', maxGrade: '10' },
        { id: 2, title: 'Proyecto Final - Primera Entrega', dueDate: '15 Ene', status: 'pendiente', grade: '-', maxGrade: '10' },
        { id: 3, title: 'Ejercicios Tema 2', dueDate: '20 Ene', status: 'pendiente', grade: '-', maxGrade: '10' },
        { id: 4, title: 'Lectura: Componentes Reactivos', dueDate: '25 Ene', status: 'atrasada', grade: '-', maxGrade: '5' }
    ];
    
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
    
</script>


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

<div class="class-container">
    <div class="class-header">
        {#if clase.imagen_url === null}
            <div class="portada"><img src={imgDefault} alt="" class="portada" ></div>
        {:else}
            <div class="portada"><img src={clase.imagen_url} alt="" class="portada" ></div>
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
        <button class="tab-button" class:active={activeTab === 'materiales'} on:click={() => activeTab = 'materiales'}>Materiales</button>
    </div>
    
    <div class="class-content">
        <div class="main-content">
            {#if activeTab === 'tablón'}
                <div class="card-title">
                    Anuncios recientes
                    <button class="action-button">+ Nuevo anuncio</button>
                </div>
                
                {#each announcements as announcement}
                    <div class="announcement-item">
                        <div class="announcement-header">
                            <div class="avatar">{announcement.avatar}</div>
                            <div class="announcement-meta">
                                <div class="announcement-author">{announcement.author}</div>
                                <div class="announcement-date">{announcement.date}</div>
                            </div>
                        </div>
                        <div class="announcement-title">{announcement.title}</div>
                        <div class="announcement-content">{announcement.content}</div>
                    </div>
                {/each}
            {/if}
            
            {#if activeTab === 'tareas'}
                <div class="card-title">
                    Todas las tareas
                    <button class="action-button">+ Crear tarea</button>
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