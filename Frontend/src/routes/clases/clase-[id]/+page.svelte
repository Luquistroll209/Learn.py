<script lang="ts">
    import { onMount } from 'svelte';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';
    import "$lib/style/createClass.css";

    let activeTab = 'tablón';
    import "$lib/style/inClass.css";
    import imgDefault from '$lib/images/classDefault.webp';

    import { browser } from '$app/environment';
    import { urlip, urlMedia } from '$lib/config';

    let clase: any = {};
    let students: any[] = [];
    let teachers: any[] = [];

    import { page } from '$app/stores';
    let id = '';
    $: id = $page.params.id ?? '';

    let showInviteModal = false;
    let showCreateNews = false;
    let showCreateTask = false;

    let areYouTeacher = false;
    let isClassOwner = false;
    let myRole = '';
    let currentUserId: number | null = null;
    let isSubmittingTask = false;
    let tasksLoading = false;
    let tasks: any[] = [];
    let submissionFilesByTask: Record<number, File[]> = {};
    let submittingByTask: Record<number, boolean> = {};

    let inviteEmail = '';

    // anuncios
    let announcements: any[] = [];
    let announcementSort = 'activity';
    let newsTitle = '';
    let newsDescription = '';
    let newsUrls = '';
    let newsImages: File[] = [];
    let isSubmitting = false;

    // tareas (backend)
    let taskTitle = '';
    let taskDueDate = '';
    let taskDescription = '';
    let taskUrls = '';
    let taskImages: File[] = [];
    let taskAllowAnyFileType = true;
    let taskAllowedExtensions = '';
    let taskMaxFiles = 1;
    let taskMaxFileSizeMb = 100;

    // calificaciones
    let grades: any[] = [];
    let averageGrade = '-';
    const materials: any[] = [];

    // edición y gestión
    let showEditNews = false;
    let editingAnnouncementId: number | null = null;
    let editNewsTitle = '';
    let editNewsDescription = '';
    let editNewsUrls = '';

    let showEditTask = false;
    let editingTaskId: number | null = null;
    let editTaskTitle = '';
    let editTaskDueDate = '';
    let editTaskDescription = '';
    let editTaskUrls = '';
    let editTaskAllowAnyFileType = true;
    let editTaskAllowedExtensions = '';
    let editTaskMaxFiles = 1;
    let editTaskMaxFileSizeMb = 100;

    onMount(async () => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = '/auth/login';
            } else {
                await loadClass();
                await Promise.all([loadAnnouncements(announcementSort), loadTasks()]);
            }
        }
    });

    function parseUrls(raw: string): string[] {
        return raw
            .split(/\n|,/)
            .map((u) => u.trim())
            .filter(Boolean);
    }

    function formatDate(dateValue: string | null | undefined): string {
        if (!dateValue) return 'Sin fecha';
        const date = new Date(dateValue);
        if (Number.isNaN(date.getTime())) return dateValue;
        return date.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
    }

    function toBackendDate(dateValue: string): string {
        const date = new Date(`${dateValue}T23:59:59`);
        if (Number.isNaN(date.getTime())) return dateValue;
        return date.toISOString();
    }

    function buildTaskStatus(task: any, teacherView: boolean): string {
        if (!teacherView && task.is_delivered) return 'entregada';
        if (task.due_at) {
            const dueDate = new Date(task.due_at);
            if (!Number.isNaN(dueDate.getTime()) && dueDate < new Date()) return 'atrasada';
        }
        return 'pendiente';
    }

    function updateGradesFromTasks() {
        const withGrades = tasks.filter((task) => !areYouTeacher && task.grade !== null && task.grade !== undefined);
        grades = withGrades.map((task) => {
            const gradeNumber = Number(task.grade);
            const percentage = Number.isNaN(gradeNumber) ? '-' : `${Math.round((gradeNumber / 10) * 100)}%`;
            return {
                task: task.title,
                grade: task.grade,
                maxGrade: '10',
                percentage,
                date: task.delivered_at ? formatDate(task.delivered_at) : '-'
            };
        });

        if (grades.length === 0) {
            averageGrade = '-';
            return;
        }

        const total = grades.reduce((acc, item) => acc + Number(item.grade || 0), 0);
        averageGrade = (total / grades.length).toFixed(2);
    }

    function getClassImageSource(): string {
        if (!clase?.imagen_url) return imgDefault;
        if (String(clase.imagen_url).startsWith('http')) return clase.imagen_url;
        return `${urlMedia}${clase.imagen_url}`;
    }

    function hydrateClassMembers() {
        students = [];
        teachers = [];
        const members = Array.isArray(clase.students_info) ? clase.students_info : [];
        for (let i = 0; i < members.length; i++) {
            const userData = {
                ...members[i],
                avatar: `${members[i].username.charAt(0)}`.toUpperCase()
            };
            if (members[i].role === 'student') {
                students.push(userData);
            } else if (members[i].role === 'teacher' || members[i].role === 'assistant') {
                teachers.push(userData);
            }
        }
    }

    function roleLabel(role: string): string {
        if (role === 'teacher') return 'Profesor';
        if (role === 'assistant') return 'Asistente';
        return 'Alumno';
    }

    async function loadClass() {
        const token = localStorage.getItem('token');
        
            const response = await fetch(`${urlip}class/obtainClassByID/${id}`, {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
            });

            const data = await response.json();

            if (response.ok){
                clase = data || {};
                isClassOwner = Boolean(clase.is_class_owner);
                myRole = String(clase.my_role || '');
                currentUserId = Number(clase.current_user_id || 0) || null;
                hydrateClassMembers();
            } else {
                showAlert("Error", data?.Error || "No se pudo cargar la clase", "red");
            }
    }

    async function loadAnnouncements(sortMode = announcementSort) {
        announcementSort = sortMode;
        const token = localStorage.getItem('token');
        const response = await fetch(`${urlip}class/obtainAnnouncements/${id}/?sort=${encodeURIComponent(sortMode)}`, {
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
        const urlsArray = parseUrls(newsUrls);

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

    async function loadTasks() {
        const token = localStorage.getItem('token');
        tasksLoading = true;
        try {
            const response = await fetch(`${urlip}class/obtainPendingTasks/${id}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                }
            });

            const data = await response.json();
            if (!response.ok) {
                showAlert("Error", data?.Error || "No se pudieron cargar las tareas", "red");
                tasks = [];
                return;
            }

            areYouTeacher = Boolean(data?.is_teacher);
            tasks = (data?.tasks || []).map((task: any) => {
                const status = buildTaskStatus(task, areYouTeacher);
                return {
                    ...task,
                    dueDate: formatDate(task.due_at),
                    status,
                    grade: task.grade ?? '-'
                };
            });
            updateGradesFromTasks();
        } catch (error) {
            tasks = [];
            showAlert("Error", "Error de conexión al cargar tareas", "red");
        } finally {
            tasksLoading = false;
        }
    }

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
            alert('Error al enviar la invitación');
        }
    }

    async function createTask() {
        if (!taskTitle.trim() || !taskDescription.trim()) {
            showAlert("Error", "Título y descripción son obligatorios", "orange");
            return;
        }

        const token = localStorage.getItem('token');
        const urlsArray = parseUrls(taskUrls);
        const extensionsArray = taskAllowedExtensions
            .split(/[,\n]/)
            .map((item) => item.trim().replace('.', '').toLowerCase())
            .filter(Boolean);

        const formData = new FormData();
        //formData.append('clase_id', id);
        formData.append('title', taskTitle.trim());
        formData.append('description', taskDescription.trim());
        formData.append('allow_any_file_type', String(taskAllowAnyFileType));
        formData.append('allowed_extensions', JSON.stringify(extensionsArray));
        formData.append('max_files', String(taskMaxFiles));
        formData.append('max_file_size_mb', String(taskMaxFileSizeMb));
        formData.append('urls', JSON.stringify(urlsArray));
        if (taskDueDate) {
            formData.append('due_at', toBackendDate(taskDueDate));
        }
        for (const file of taskImages) {
            formData.append('photos', file);
        }

        isSubmittingTask = true;
        const response = await fetch(`${urlip}class/createTask/${id}/`, {
            method: 'POST',
            headers: {
                'authorization': `${token}`
            },
            body: formData
        });
        const data = await response.json();
        isSubmittingTask = false;

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo crear la tarea", "red");
            return;
        }

        taskTitle = '';
        taskDueDate = '';
        taskDescription = '';
        taskUrls = '';
        taskImages = [];
        taskAllowAnyFileType = true;
        taskAllowedExtensions = '';
        taskMaxFiles = 1;
        taskMaxFileSizeMb = 100;
        showCreateTask = false;
        showAlert("Listo", "Tarea creada correctamente", "green");
        await loadTasks();
    }

    function handleTaskFiles(event: Event) {
        const target = event.currentTarget as HTMLInputElement;
        const files = target.files ? Array.from(target.files) : [];
        taskImages = files;
    }

    function handleTaskSubmissionFiles(event: Event, taskId: number) {
        const target = event.currentTarget as HTMLInputElement;
        const files = target.files ? Array.from(target.files) : [];
        submissionFilesByTask = {
            ...submissionFilesByTask,
            [taskId]: files
        };
    }

    async function submitTask(taskId: number) {
        const files = submissionFilesByTask[taskId] || [];
        if (!files.length) {
            showAlert("Error", "Selecciona al menos un archivo para entregar", "orange");
            return;
        }

        const token = localStorage.getItem('token');
        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }

        submittingByTask = { ...submittingByTask, [taskId]: true };
        const response = await fetch(`${urlip}class/submitTask/${taskId}/`, {
            method: 'POST',
            headers: {
                'authorization': `${token}`
            },
            body: formData
        });
        const data = await response.json();
        submittingByTask = { ...submittingByTask, [taskId]: false };

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo entregar la tarea", "red");
            return;
        }

        showAlert("Listo", "Tarea entregada correctamente", "green");
        submissionFilesByTask = { ...submissionFilesByTask, [taskId]: [] };
        await loadTasks();
    }

    function openEditAnnouncement(announcement: any) {
        editingAnnouncementId = Number(announcement.id);
        editNewsTitle = announcement.title || '';
        editNewsDescription = announcement.description || '';
        editNewsUrls = Array.isArray(announcement.urls) ? announcement.urls.join('\n') : '';
        showEditNews = true;
    }

    async function saveEditedAnnouncement() {
        if (!editingAnnouncementId) return;
        if (!editNewsTitle.trim() || !editNewsDescription.trim()) {
            showAlert("Error", "Título y descripción son obligatorios", "orange");
            return;
        }

        const token = localStorage.getItem('token');
        const payload = {
            title: editNewsTitle.trim(),
            description: editNewsDescription.trim(),
            urls: parseUrls(editNewsUrls)
        };

        const response = await fetch(`${urlip}class/manageAnnouncement/${editingAnnouncementId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'authorization': `${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo editar el anuncio", "red");
            return;
        }

        showEditNews = false;
        editingAnnouncementId = null;
        showAlert("Listo", "Anuncio actualizado", "green");
        await loadAnnouncements(announcementSort);
    }

    async function deleteAnnouncement(announcementId: number) {
        if (!confirm("¿Quieres eliminar este anuncio?")) return;

        const token = localStorage.getItem('token');
        const response = await fetch(`${urlip}class/manageAnnouncement/${announcementId}/`, {
            method: 'DELETE',
            headers: {
                'authorization': `${token}`
            }
        });
        const data = await response.json();

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo eliminar el anuncio", "red");
            return;
        }

        showAlert("Listo", "Anuncio eliminado", "green");
        await loadAnnouncements(announcementSort);
    }

    function openEditTask(task: any) {
        editingTaskId = Number(task.id);
        editTaskTitle = task.title || '';
        editTaskDescription = task.description || '';
        editTaskUrls = Array.isArray(task.urls) ? task.urls.join('\n') : '';
        editTaskAllowAnyFileType = Boolean(task.allow_any_file_type);
        editTaskAllowedExtensions = Array.isArray(task.allowed_extensions)
            ? task.allowed_extensions.join(', ')
            : '';
        editTaskMaxFiles = Number(task.max_files || 1);
        editTaskMaxFileSizeMb = Number(task.max_file_size_mb || 100);
        editTaskDueDate = task.due_at ? new Date(task.due_at).toISOString().slice(0, 10) : '';
        showEditTask = true;
    }

    async function saveEditedTask() {
        if (!editingTaskId) return;
        if (!editTaskTitle.trim() || !editTaskDescription.trim()) {
            showAlert("Error", "Título y descripción son obligatorios", "orange");
            return;
        }

        const token = localStorage.getItem('token');
        const payload: any = {
            title: editTaskTitle.trim(),
            description: editTaskDescription.trim(),
            urls: parseUrls(editTaskUrls),
            allow_any_file_type: editTaskAllowAnyFileType,
            max_files: editTaskMaxFiles,
            max_file_size_mb: editTaskMaxFileSizeMb,
        };
        if (editTaskDueDate) {
            payload.due_at = toBackendDate(editTaskDueDate);
        } else {
            payload.due_at = null;
        }
        if (!editTaskAllowAnyFileType) {
            payload.allowed_extensions = editTaskAllowedExtensions
                .split(/[,\n]/)
                .map((item) => item.trim().replace('.', '').toLowerCase())
                .filter(Boolean);
        } else {
            payload.allowed_extensions = [];
        }

        const response = await fetch(`${urlip}class/manageTask/${editingTaskId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'authorization': `${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo editar la tarea", "red");
            return;
        }

        showEditTask = false;
        editingTaskId = null;
        showAlert("Listo", "Tarea actualizada", "green");
        await loadTasks();
    }

    async function deleteTask(taskId: number) {
        if (!confirm("¿Quieres eliminar esta tarea? También se eliminarán sus entregas.")) return;

        const token = localStorage.getItem('token');
        const response = await fetch(`${urlip}class/manageTask/${taskId}/`, {
            method: 'DELETE',
            headers: {
                'authorization': `${token}`
            }
        });
        const data = await response.json();

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo eliminar la tarea", "red");
            return;
        }

        showAlert("Listo", "Tarea eliminada", "green");
        await loadTasks();
    }

    async function expulsarAlumno(studentId: number) {
        if (!confirm("¿Seguro que quieres expulsar a este alumno de la clase?")) return;
        const token = localStorage.getItem('token');
        const response = await fetch(`${urlip}class/removeMember/${id}/${studentId}/`, {
            method: 'DELETE',
            headers: {
                'authorization': `${token}`
            }
        });
        const data = await response.json();
        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo expulsar al alumno", "red");
            return;
        }
        showAlert("Listo", "Alumno expulsado", "green");
        await loadClass();
        await loadTasks();
    }

    async function abandonarClase() {
        if (!confirm("¿Quieres abandonar esta clase?")) return;
        const token = localStorage.getItem('token');
        const response = await fetch(`${urlip}class/leaveClass/${id}/`, {
            method: 'POST',
            headers: {
                'authorization': `${token}`
            }
        });
        const data = await response.json();
        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo abandonar la clase", "red");
            return;
        }
        showAlert("Listo", "Has abandonado la clase", "green");
        window.location.href = '/clases';
    }

    async function actualizarRolMiembro(userId: number, role: string) {
        if (!isClassOwner) return;
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch(`${urlip}class/updateMemberRole/${id}/${userId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'authorization': `${token}`
            },
            body: JSON.stringify({ role })
        });
        const data = await response.json();
        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo actualizar el rol", "red");
            await loadClass();
            return;
        }

        showAlert("Listo", "Rol actualizado", "green");
        await loadClass();
        await loadTasks();
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
                <p>Crea una tarea real en el backend</p>
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

                <div class="form-group">
                    <label for="taskAllowAnyType">Tipos de archivo</label>
                    <select id="taskAllowAnyType" bind:value={taskAllowAnyFileType}>
                        <option value={true}>Permitir cualquier tipo</option>
                        <option value={false}>Restringir por extensión</option>
                    </select>
                </div>

                {#if !taskAllowAnyFileType}
                    <div class="form-group">
                        <label for="taskAllowedExtensions">Extensiones permitidas</label>
                        <input
                            id="taskAllowedExtensions"
                            placeholder="pdf, docx, zip, py"
                            type="text"
                            bind:value={taskAllowedExtensions}
                        >
                    </div>
                {/if}

                <div class="form-group">
                    <label for="taskMaxFiles">Máximo archivos por entrega</label>
                    <input
                        id="taskMaxFiles"
                        type="number"
                        min="1"
                        max="50"
                        bind:value={taskMaxFiles}
                    >
                </div>

                <div class="form-group">
                    <label for="taskMaxSize">Tamaño máximo por archivo (MB)</label>
                    <input
                        id="taskMaxSize"
                        type="number"
                        min="1"
                        max="1024"
                        bind:value={taskMaxFileSizeMb}
                    >
                </div>
                
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showCreateTask = false}>Cancelar</button>
                    <button class="send-btn" type="submit" disabled={isSubmittingTask}>
                        {isSubmittingTask ? 'Creando...' : 'Crear tarea'}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

{#if showEditNews}
    <div class="modal-overlay" on:click={() => showEditNews = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showEditNews = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Editar anuncio</h2>
                <p>Actualiza el contenido del tablón</p>
            </div>

            <form on:submit|preventDefault={saveEditedAnnouncement}>
                <div class="form-group">
                    <label for="editNewsTitle">Título</label>
                    <input id="editNewsTitle" type="text" bind:value={editNewsTitle} required>
                </div>
                <div class="form-group">
                    <label for="editNewsDescription">Descripción</label>
                    <textarea id="editNewsDescription" rows="4" bind:value={editNewsDescription} required></textarea>
                </div>
                <div class="form-group">
                    <label for="editNewsUrls">URLs (opcional)</label>
                    <textarea id="editNewsUrls" rows="3" bind:value={editNewsUrls}></textarea>
                </div>
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showEditNews = false}>Cancelar</button>
                    <button class="send-btn" type="submit">Guardar cambios</button>
                </div>
            </form>
        </div>
    </div>
{/if}

{#if showEditTask}
    <div class="modal-overlay" on:click={() => showEditTask = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showEditTask = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Editar tarea</h2>
                <p>Modifica la configuración de la tarea</p>
            </div>

            <form on:submit|preventDefault={saveEditedTask}>
                <div class="form-group">
                    <label for="editTaskTitle">Título</label>
                    <input id="editTaskTitle" type="text" bind:value={editTaskTitle} required>
                </div>
                <div class="form-group">
                    <label for="editTaskDueDate">Fecha límite</label>
                    <input id="editTaskDueDate" type="date" bind:value={editTaskDueDate}>
                </div>
                <div class="form-group">
                    <label for="editTaskDescription">Descripción</label>
                    <textarea id="editTaskDescription" rows="4" bind:value={editTaskDescription} required></textarea>
                </div>
                <div class="form-group">
                    <label for="editTaskUrls">URLs</label>
                    <textarea id="editTaskUrls" rows="3" bind:value={editTaskUrls}></textarea>
                </div>
                <div class="form-group">
                    <label for="editTaskAllowAny">Tipos de archivo</label>
                    <select id="editTaskAllowAny" bind:value={editTaskAllowAnyFileType}>
                        <option value={true}>Permitir cualquier tipo</option>
                        <option value={false}>Restringir por extensión</option>
                    </select>
                </div>
                {#if !editTaskAllowAnyFileType}
                    <div class="form-group">
                        <label for="editTaskAllowedExtensions">Extensiones permitidas</label>
                        <input id="editTaskAllowedExtensions" type="text" bind:value={editTaskAllowedExtensions} placeholder="pdf, docx, zip">
                    </div>
                {/if}
                <div class="form-group">
                    <label for="editTaskMaxFiles">Máximo archivos</label>
                    <input id="editTaskMaxFiles" type="number" min="1" max="50" bind:value={editTaskMaxFiles}>
                </div>
                <div class="form-group">
                    <label for="editTaskMaxFileSizeMb">Tamaño máximo (MB)</label>
                    <input id="editTaskMaxFileSizeMb" type="number" min="1" max="1024" bind:value={editTaskMaxFileSizeMb}>
                </div>
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showEditTask = false}>Cancelar</button>
                    <button class="send-btn" type="submit">Guardar cambios</button>
                </div>
            </form>
        </div>
    </div>
{/if}

<div class="class-container">
    <div class="class-header">
        <div class="portada-wrap"><img src={getClassImageSource()} alt="" class="portada-image" ></div>
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
                    <div class="manage-row">
                        <select class="forum-sort-select" bind:value={announcementSort} on:change={(event) => loadAnnouncements((event.currentTarget as HTMLSelectElement).value)}>
                            <option value="activity">Más activos</option>
                            <option value="new">Más nuevos</option>
                            <option value="top">Más comentados</option>
                        </select>
                        <button on:click={() => showCreateNews = true}  class="action-button">+ Nuevo anuncio</button>
                    </div>
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
                                    <div class="announcement-date">
                                        {announcement.created_at} • {announcement.comments_count || 0} comentario(s)
                                    </div>
                                </div>
                                <div class="manage-row">
                                    <a class="secondary-button" href={`/clases/clase-${id}/anuncio-${announcement.id}`}>Ver hilo</a>
                                    {#if announcement.can_edit}
                                        <button class="secondary-button manage-btn" type="button" on:click={() => openEditAnnouncement(announcement)}>
                                            Editar
                                        </button>
                                    {/if}
                                    {#if announcement.can_delete}
                                        <button class="secondary-button manage-btn danger-btn" type="button" on:click={() => deleteAnnouncement(announcement.id)}>
                                            Eliminar
                                        </button>
                                    {/if}
                                </div>
                            </div>
                            <a class="announcement-title" style="text-decoration: none; display: inline-block;" href={`/clases/clase-${id}/anuncio-${announcement.id}`}>{announcement.title}</a>
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
                    {#if areYouTeacher}
                        <button class="action-button" on:click={() => showCreateTask = true}>+ Crear tarea</button>
                    {/if}
                </div>

                {#if tasksLoading}
                    <div class="announcement-item">
                        <div class="announcement-title">Cargando tareas...</div>
                    </div>
                {:else if tasks.length === 0}
                    <div class="announcement-item">
                        <div class="announcement-title">No hay tareas pendientes</div>
                    </div>
                {:else}
                    {#each tasks as task}
                        <div class="task-item task-item-expanded">
                            <a class="task-row task-row-link" href={`/clases/clase-${id}/tarea-${task.id}`}>
                                <div class="task-icon"><i class="fa-solid fa-file-lines"></i></div>
                                <div class="task-info">
                                    <div class="task-title">{task.title}</div>
                                    <div class="task-due">Fecha límite: {task.dueDate}</div>
                                </div>
                                <span class="task-status {task.status}">
                                    {task.status === 'entregada' ? 'Entregada' : task.status === 'pendiente' ? 'Pendiente' : 'Atrasada'}
                                </span>
                            </a>

                            <div class="task-meta-row">
                                {#if areYouTeacher}
                                    <span class="task-due">Entregadas: {task.delivered_count ?? 0}</span>
                                    <span class="task-due">Pendientes: {task.pending_count ?? 0}</span>
                                    <span class="task-due">Por calificar: {task.to_grade_count ?? 0}</span>
                                {:else}
                                    <span class="task-due">Nota: {task.grade ?? '-'}</span>
                                {/if}
                                <a class="secondary-button" href={`/clases/clase-${id}/tarea-${task.id}`}>Ver detalle</a>
                                {#if areYouTeacher}
                                    <button class="secondary-button manage-btn" type="button" on:click={() => openEditTask(task)}>
                                        Editar
                                    </button>
                                    <button class="secondary-button manage-btn danger-btn" type="button" on:click={() => deleteTask(task.id)}>
                                        Eliminar
                                    </button>
                                {/if}
                            </div>

                            {#if !areYouTeacher && !task.is_delivered}
                                <div class="task-submit-row">
                                    <input
                                        type="file"
                                        multiple
                                        on:change={(event) => handleTaskSubmissionFiles(event, task.id)}
                                    >
                                    <button
                                        class="action-button"
                                        on:click={() => submitTask(task.id)}
                                        disabled={submittingByTask[task.id]}
                                    >
                                        {submittingByTask[task.id] ? 'Entregando...' : 'Entregar'}
                                    </button>
                                </div>
                                {#if submissionFilesByTask[task.id]?.length}
                                    <div class="files files-compact">
                                        {#each submissionFilesByTask[task.id] as file}
                                            <div class="file">{file.name}</div>
                                        {/each}
                                    </div>
                                {/if}
                            {/if}
                        </div>
                    {/each}
                {/if}
            {/if}
            
            {#if activeTab === 'personas'}
                <div class="card-title">    
                    Profesores
                    {#if isClassOwner}
                        <button on:click={() => showInviteModal = true} class="addPerson"><i class="fa-solid fa-person-circle-plus"></i></button>
                    {/if}
                </div>
                
                {#each teachers as teacher}
                    <div class="student-item">
                        <div class="avatar">{teacher.avatar}</div>
                        <div class="student-info">
                            <div class="student-name">{teacher.username}</div>
                            <div class="student-email">{teacher.email}</div>
                            <div class="student-email">Rol: {roleLabel(teacher.role)}</div>
                        </div>
                        {#if isClassOwner}
                            <select
                                class="forum-sort-select"
                                value={teacher.role}
                                disabled={currentUserId === teacher.user_id}
                                on:change={(event) => actualizarRolMiembro(teacher.user_id, (event.currentTarget as HTMLSelectElement).value)}
                            >
                                <option value="teacher">Profesor</option>
                                <option value="assistant">Asistente</option>
                                <option value="student">Alumno</option>
                            </select>
                        {/if}
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
                            <div class="student-email">Rol: {roleLabel(student.role)}</div>
                        </div>
                        {#if isClassOwner}
                            <select
                                class="forum-sort-select"
                                value={student.role}
                                disabled={currentUserId === student.user_id}
                                on:change={(event) => actualizarRolMiembro(student.user_id, (event.currentTarget as HTMLSelectElement).value)}
                            >
                                <option value="student">Alumno</option>
                                <option value="assistant">Asistente</option>
                                <option value="teacher">Profesor</option>
                            </select>
                        {/if}
                        {#if isClassOwner}
                            <button
                                class="secondary-button"
                                type="button"
                                on:click={() => expulsarAlumno(student.user_id)}
                            >
                                Expulsar
                            </button>
                        {/if}
                    </div>
                {/each}
            {/if}
            
            {#if activeTab === 'calificaciones'}
                <div class="average-card">
                    <div class="average-label">Tu calificación promedio</div>
                    <div class="average-number">{averageGrade}</div>
                </div>
                
                <div class="card-title">Historial de calificaciones</div>
                {#if areYouTeacher}
                    <div class="announcement-item">
                        <div class="announcement-title">Esta vista de calificaciones es para alumnos.</div>
                    </div>
                {:else if grades.length === 0}
                    <div class="announcement-item">
                        <div class="announcement-title">Aún no tienes tareas calificadas.</div>
                    </div>
                {:else}
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
            {/if}
            
            {#if activeTab === 'materiales'}
                <div class="card-title">
                    Recursos del curso
                    <button class="action-button">+ Subir archivo</button>
                </div>
                
                {#each materials as material}
                    <div class="material-item">
                        <div class="material-icon">
                            {#if material.type === 'pdf'}
                                <i class="fa-solid fa-file-pdf"></i>
                            {:else if material.type === 'video'}
                                <i class="fa-solid fa-video"></i>
                            {:else}
                                <i class="fa-solid fa-box-archive"></i>
                            {/if}
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
                {#if tasks.length === 0}
                    <div class="upcoming-item">
                        <div class="upcoming-title">Sin tareas pendientes</div>
                    </div>
                {:else}
                    {#each tasks.slice(0, 3) as task}
                        <div class="upcoming-item">
                            <div class="upcoming-title">{task.title}</div>
                            <div class="upcoming-date">{task.dueDate}</div>
                        </div>
                    {/each}
                {/if}
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
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={abandonarClase}>
                    Abandonar clase
                </button>
                {#if areYouTeacher}
                    <a href="/clases/clase-{id}/dashboard" class="secondary-button" style="width: 100%;">
                        Dashboard
                    </a>
                {/if}
            </div>
        </div>
    </div>
</div>

<style>
    .manage-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
    }

    .forum-sort-select {
        min-width: 150px;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 8px 10px;
        background: #fff;
    }

    .manage-btn {
        border-radius: 999px;
        padding: 8px 12px;
    }

    .danger-btn {
        border-color: #f2b8b5;
        color: #b42318;
        background: #fff5f5;
    }
</style>
