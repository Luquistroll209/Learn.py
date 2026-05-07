<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { page } from '$app/stores';
    import { urlip, urlMedia } from '$lib/config';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';
    import imgDefault from '$lib/images/classDefault.webp';
    import '$lib/style/inClass.css';

    type StudentRow = {
        id: number;
        username: string;
        first_name?: string;
        last_name?: string;
        email?: string;
        role?: string;
        joined_at?: string;
        delivered_tasks?: number;
        graded_tasks?: number;
        pending_tasks?: number;
        pending_grading_tasks?: number;
        average_grade?: string | null;
        average_percentage?: string | null;
        status?: string;
        avatar?: string;
    };

    type TaskRow = {
        id: number;
        title: string;
        description: string;
        due_at: string | null;
        allow_any_file_type: boolean;
        allowed_extensions: string[];
        max_files: number;
        max_file_size_mb: number;
        photos: string[];
        urls: string[];
        status: 'activa' | 'cerrada';
        delivered_count: number;
        pending_count: number;
        graded_count: number;
        to_grade_count: number;
        total_students: number;
        average_grade: string | null;
        created_at: string;
    };

    type DeliveredStudent = {
        id: number;
        username: string;
        first_name?: string;
        last_name?: string;
        email?: string;
        grade?: string | null;
        feedback?: string;
    };

    type PendingStudent = {
        id: number;
        username: string;
        first_name?: string;
        last_name?: string;
        email?: string;
    };

    type TaskDetail = {
        id: number;
        delivered_students: DeliveredStudent[];
        pending_students: PendingStudent[];
    };

    let id = '';
    $: id = $page.params.id ?? '';

    let activeTab = 'alumnos';
    let isLoading = true;
    let classData: any = {};
    let teachers: any[] = [];
    let students: StudentRow[] = [];
    let tasks: TaskRow[] = [];
    let stats: any = {
        total_students: 0,
        total_tasks: 0,
        delivered_submissions: 0,
        pending_submissions: 0,
        graded_submissions: 0,
        pending_grading_submissions: 0,
        expected_submissions: 0,
        delivery_rate: 0,
        active_tasks: 0,
        overdue_tasks: 0,
        next_due_at: null,
        class_average_grade: null
    };

    let showInviteModal = false;
    let showCreateTaskModal = false;
    let showEditTaskModal = false;
    let inviteEmail = '';
    let isSubmittingTask = false;
    let isUpdatingTask = false;
    let selectedTaskId = '';
    let selectedTaskDetail: TaskDetail | null = null;
    let gradingValues: Record<number, string> = {};
    let feedbackValues: Record<number, string> = {};
    let savingByStudent: Record<number, boolean> = {};
    let classSettingsName = '';
    let classSettingsDescription = '';
    let classSettingsBannerFile: File | null = null;
    let removeCurrentBanner = false;
    let isSavingClassSettings = false;
    let taskUrlsText = '';
    let taskImages: File[] = [];

    let editingTaskId: number | null = null;
    let editTaskTitle = '';
    let editTaskDescription = '';
    let editTaskDueDate = '';
    let editTaskAllowAnyFileType = true;
    let editTaskAllowedExtensions = '';
    let editTaskMaxFiles = 1;
    let editTaskMaxFileSizeMb = 100;
    let editTaskUrlsText = '';
    let editTaskExistingPhotos: string[] = [];
    let editTaskNewImages: File[] = [];

    let newTask = {
        title: '',
        description: '',
        dueDate: '',
        allowAnyFileType: true,
        allowedExtensions: '',
        maxFiles: 1,
        maxFileSizeMb: 100
    };

    onMount(async () => {
        if (!browser) return;
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/auth/login';
            return;
        }

        await loadDashboard();
        isLoading = false;
    });

    function getClassImageSource(): string {
        if (!classData?.imagen_url) return imgDefault;
        if (String(classData.imagen_url).startsWith('http')) return classData.imagen_url;
        return `${urlMedia}${classData.imagen_url}`;
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

    function parseUrls(raw: string): string[] {
        return raw
            .split(/\n|,/)
            .map((item) => item.trim())
            .filter(Boolean);
    }

    function parseAllowedExtensions(raw: string): string[] {
        return raw
            .split(/[,\n]/)
            .map((item) => item.trim().replace('.', '').toLowerCase())
            .filter(Boolean);
    }

    function formatDateInput(dateValue: string | null | undefined): string {
        if (!dateValue) return '';
        const date = new Date(dateValue);
        if (Number.isNaN(date.getTime())) return '';
        return date.toISOString().slice(0, 10);
    }

    function toBool(value: unknown): boolean {
        if (typeof value === 'boolean') return value;
        return String(value).toLowerCase() === 'true';
    }

    function getTaskImageSource(photoPath: string): string {
        if (!photoPath) return '';
        if (photoPath.startsWith('http://') || photoPath.startsWith('https://')) {
            return photoPath;
        }
        return `${urlMedia}${photoPath.replace(/^\/+/, '')}`;
    }

    function parseTaskStatus(status: string): string {
        if (status === 'cerrada') return 'atrasada';
        return 'entregada';
    }

    function parseStudentStatusClass(status?: string): string {
        if (status === 'al_dia') return 'entregada';
        if (status === 'sin_entregas') return 'atrasada';
        return 'pendiente';
    }

    function parseStudentStatusLabel(status?: string): string {
        if (status === 'al_dia') return 'Al día';
        if (status === 'sin_entregas') return 'Sin entregas';
        if (status === 'por_calificar') return 'Por calificar';
        if (status === 'sin_tareas') return 'Sin tareas';
        return 'Pendiente';
    }

    function displayName(user: { username?: string; first_name?: string; last_name?: string }) {
        const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
        return fullName || user.username || 'Usuario';
    }

    function addAvatar<T extends { username?: string }>(rows: T[]): (T & { avatar: string })[] {
        return rows.map((row) => ({
            ...row,
            avatar: (row.username || 'U').charAt(0).toUpperCase()
        }));
    }

    async function loadDashboard(keepSelectedTask = true) {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${urlip}class/obtainClassDashboard/${id}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    authorization: token
                }
            });
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 403) {
                    showAlert('Sin acceso', 'Este dashboard solo está disponible para profesorado', 'orange');
                    window.location.href = `/clases/clase-${id}`;
                    return;
                }
                showAlert('Error', data?.Error || 'No se pudo cargar el dashboard', 'red');
                return;
            }

            classData = data.clase || {};
            classSettingsName = classData.name || '';
            classSettingsDescription = classData.description || '';
            classSettingsBannerFile = null;
            removeCurrentBanner = false;
            teachers = addAvatar(data.teachers || []);
            students = addAvatar(data.students || []);
            tasks = data.tasks || [];
            stats = data.stats || stats;

            const previousTaskId = keepSelectedTask ? selectedTaskId : '';
            const keepIdExists = tasks.some((task) => String(task.id) === String(previousTaskId));
            selectedTaskId = keepIdExists ? String(previousTaskId) : (tasks[0] ? String(tasks[0].id) : '');

            await loadSelectedTaskDetail();
        } catch (error) {
            showAlert('Error', 'Error de conexión al cargar el dashboard', 'red');
        }
    }

    async function loadSelectedTaskDetail() {
        if (!selectedTaskId) {
            selectedTaskDetail = null;
            gradingValues = {};
            feedbackValues = {};
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch(`${urlip}class/obtainTaskDetail/${selectedTaskId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                authorization: token
            }
        });

        const data = await response.json();
        if (!response.ok) {
            selectedTaskDetail = null;
            showAlert('Error', data?.Error || 'No se pudo cargar el detalle de la tarea', 'red');
            return;
        }

        if (!data?.is_teacher) {
            selectedTaskDetail = null;
            return;
        }

        selectedTaskDetail = data.task;
        const gradeMap: Record<number, string> = {};
        const feedbackMap: Record<number, string> = {};
        for (const delivered of data.task?.delivered_students || []) {
            gradeMap[delivered.id] = delivered.grade !== null && delivered.grade !== undefined
                ? String(delivered.grade)
                : '';
            feedbackMap[delivered.id] = delivered.feedback !== null && delivered.feedback !== undefined
                ? String(delivered.feedback)
                : '';
        }
        gradingValues = gradeMap;
        feedbackValues = feedbackMap;
    }

    async function invitarAlumno() {
        if (!inviteEmail.trim()) return;
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${urlip}class/invite/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    authorization: token
                },
                body: JSON.stringify({
                    clase_id: id,
                    email: inviteEmail.trim()
                })
            });
            const data = await response.json();
            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudo enviar la invitación', 'red');
                return;
            }

            showAlert('Listo', 'Invitación enviada', 'green');
            inviteEmail = '';
            showInviteModal = false;
        } catch (error) {
            showAlert('Error', 'Error de conexión al enviar invitación', 'red');
        }
    }

    async function crearTarea() {
        if (!newTask.title.trim() || !newTask.description.trim()) {
            showAlert('Error', 'Título y descripción son obligatorios', 'orange');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) return;

        const allowAny = toBool(newTask.allowAnyFileType);
        const extensionsArray = parseAllowedExtensions(newTask.allowedExtensions);
        if (!allowAny && extensionsArray.length === 0) {
            showAlert('Error', 'Añade al menos una extensión permitida', 'orange');
            return;
        }
        const urlsArray = parseUrls(taskUrlsText);

        const formData = new FormData();
        formData.append('title', newTask.title.trim());
        formData.append('description', newTask.description.trim());
        formData.append('allow_any_file_type', String(allowAny));
        formData.append('allowed_extensions', JSON.stringify(extensionsArray));
        formData.append('max_files', String(newTask.maxFiles || 1));
        formData.append('max_file_size_mb', String(newTask.maxFileSizeMb || 100));
        formData.append('urls', JSON.stringify(urlsArray));
        if (newTask.dueDate) {
            formData.append('due_at', toBackendDate(newTask.dueDate));
        }
        for (const image of taskImages) {
            formData.append('photos[]', image);
        }

        isSubmittingTask = true;
        try {
            const response = await fetch(`${urlip}class/createTask/${id}/`, {
                method: 'POST',
                headers: {
                    authorization: token
                },
                body: formData
            });
            const data = await response.json();

            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudo crear la tarea', 'red');
                return;
            }

            showAlert('Listo', 'Tarea creada correctamente', 'green');
            showCreateTaskModal = false;
            newTask = {
                title: '',
                description: '',
                dueDate: '',
                allowAnyFileType: true,
                allowedExtensions: '',
                maxFiles: 1,
                maxFileSizeMb: 100
            };
            taskUrlsText = '';
            taskImages = [];
            activeTab = 'tareas';
            await loadDashboard(false);
        } catch (error) {
            showAlert('Error', 'Error de conexión al crear la tarea', 'red');
        } finally {
            isSubmittingTask = false;
        }
    }

    function handleTaskImages(event: Event) {
        const input = event.currentTarget as HTMLInputElement;
        const files = input.files ? Array.from(input.files) : [];
        taskImages = files;
    }

    function removeTaskImage(index: number) {
        taskImages = taskImages.filter((_, idx) => idx !== index);
    }

    function openEditTask(task: TaskRow) {
        editingTaskId = Number(task.id);
        editTaskTitle = task.title || '';
        editTaskDescription = task.description || '';
        editTaskDueDate = formatDateInput(task.due_at);
        editTaskAllowAnyFileType = Boolean(task.allow_any_file_type);
        editTaskAllowedExtensions = Array.isArray(task.allowed_extensions) ? task.allowed_extensions.join(', ') : '';
        editTaskMaxFiles = Number(task.max_files || 1);
        editTaskMaxFileSizeMb = Number(task.max_file_size_mb || 100);
        editTaskUrlsText = Array.isArray(task.urls) ? task.urls.join('\n') : '';
        editTaskExistingPhotos = Array.isArray(task.photos) ? [...task.photos] : [];
        editTaskNewImages = [];
        showEditTaskModal = true;
    }

    function handleEditTaskImages(event: Event) {
        const input = event.currentTarget as HTMLInputElement;
        const files = input.files ? Array.from(input.files) : [];
        editTaskNewImages = files;
    }

    function removeEditTaskExistingPhoto(index: number) {
        editTaskExistingPhotos = editTaskExistingPhotos.filter((_, idx) => idx !== index);
    }

    function removeEditTaskNewImage(index: number) {
        editTaskNewImages = editTaskNewImages.filter((_, idx) => idx !== index);
    }

    async function saveEditedTask() {
        if (!editingTaskId) return;
        if (!editTaskTitle.trim() || !editTaskDescription.trim()) {
            showAlert('Error', 'Título y descripción son obligatorios', 'orange');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) return;

        const allowAny = toBool(editTaskAllowAnyFileType);
        const extensionsArray = parseAllowedExtensions(editTaskAllowedExtensions);
        if (!allowAny && extensionsArray.length === 0) {
            showAlert('Error', 'Añade al menos una extensión permitida', 'orange');
            return;
        }
        const urlsArray = parseUrls(editTaskUrlsText);

        const formData = new FormData();
        formData.append('title', editTaskTitle.trim());
        formData.append('description', editTaskDescription.trim());
        formData.append('allow_any_file_type', String(allowAny));
        formData.append('allowed_extensions', JSON.stringify(extensionsArray));
        formData.append('max_files', String(editTaskMaxFiles || 1));
        formData.append('max_file_size_mb', String(editTaskMaxFileSizeMb || 100));
        formData.append('urls', JSON.stringify(urlsArray));
        formData.append('photos', JSON.stringify(editTaskExistingPhotos));
        if (editTaskDueDate) {
            formData.append('due_at', toBackendDate(editTaskDueDate));
        } else {
            formData.append('due_at', '');
        }
        for (const image of editTaskNewImages) {
            formData.append('photos[]', image);
        }

        isUpdatingTask = true;
        try {
            const response = await fetch(`${urlip}class/manageTask/${editingTaskId}/`, {
                method: 'PATCH',
                headers: {
                    authorization: token
                },
                body: formData
            });
            const data = await response.json();
            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudo actualizar la tarea', 'red');
                return;
            }

            showAlert('Listo', 'Tarea actualizada', 'green');
            showEditTaskModal = false;
            editingTaskId = null;
            await loadDashboard(true);
        } catch (error) {
            showAlert('Error', 'Error de conexión al editar tarea', 'red');
        } finally {
            isUpdatingTask = false;
        }
    }

    async function deleteTask(taskId: number) {
        if (!confirm('¿Seguro que quieres eliminar esta tarea? También se borrarán sus entregas.')) return;
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${urlip}class/manageTask/${taskId}/`, {
                method: 'DELETE',
                headers: {
                    authorization: token
                }
            });
            const data = await response.json();
            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudo eliminar la tarea', 'red');
                return;
            }

            showAlert('Listo', 'Tarea eliminada', 'green');
            await loadDashboard(false);
        } catch (error) {
            showAlert('Error', 'Error de conexión al eliminar tarea', 'red');
        }
    }

    async function guardarCalificacion(studentId: number) {
        if (!selectedTaskId) return;

        const token = localStorage.getItem('token');
        if (!token) return;

        const rawGrade = String(gradingValues[studentId] ?? '').replace(',', '.').trim();
        const rawFeedback = String(feedbackValues[studentId] ?? '').trim();

        if (rawGrade !== '') {
            const gradeValue = Number(rawGrade);
            if (Number.isNaN(gradeValue) || gradeValue < 0 || gradeValue > 10) {
                showAlert('Error', 'La nota debe estar entre 0 y 10', 'orange');
                return;
            }
        }

        const payload: Record<string, unknown> = {
            student_id: studentId,
            feedback: rawFeedback
        };
        if (!rawGrade) {
            payload.clear_grade = true;
        } else {
            payload.grade = rawGrade;
        }

        savingByStudent = { ...savingByStudent, [studentId]: true };
        try {
            const response = await fetch(`${urlip}class/gradeTaskSubmission/${selectedTaskId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    authorization: token
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudo guardar la calificación', 'red');
                return;
            }

            showAlert('Listo', 'Calificación actualizada', 'green');
            await loadDashboard(true);
        } catch (error) {
            showAlert('Error', 'Error de conexión al guardar calificación', 'red');
        } finally {
            savingByStudent = { ...savingByStudent, [studentId]: false };
        }
    }

    function handleClassSettingsBanner(event: Event) {
        const target = event.currentTarget as HTMLInputElement;
        const file = target.files && target.files.length > 0 ? target.files[0] : null;
        classSettingsBannerFile = file;
    }

    async function saveClassSettings() {
        if (!classSettingsName.trim()) {
            showAlert('Error', 'El nombre de la clase es obligatorio', 'orange');
            return;
        }
        const token = localStorage.getItem('token');
        if (!token) return;

        const formData = new FormData();
        formData.append('name', classSettingsName.trim());
        formData.append('description', classSettingsDescription.trim());
        if (removeCurrentBanner) {
            formData.append('remove_banner', 'true');
        }
        if (classSettingsBannerFile) {
            formData.append('imagen', classSettingsBannerFile);
        }

        isSavingClassSettings = true;
        try {
            const response = await fetch(`${urlip}class/updateClassSettings/${id}/`, {
                method: 'PATCH',
                headers: {
                    authorization: token
                },
                body: formData
            });
            const data = await response.json();
            if (!response.ok) {
                showAlert('Error', data?.Error || 'No se pudo actualizar la clase', 'red');
                return;
            }

            showAlert('Listo', 'Configuración de clase actualizada', 'green');
            classSettingsBannerFile = null;
            removeCurrentBanner = false;
            await loadDashboard(false);
        } catch (error) {
            showAlert('Error', 'Error de conexión al guardar configuración', 'red');
        } finally {
            isSavingClassSettings = false;
        }
    }
</script>

<Alert />

{#if showInviteModal}
    <div class="modal-overlay" on:click={() => showInviteModal = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showInviteModal = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Invitar alumno</h2>
                <p>Envía invitación por correo para unirse a la clase</p>
            </div>
            <div class="form-group">
                <label for="inviteEmail">Correo electrónico</label>
                <input id="inviteEmail" type="email" bind:value={inviteEmail} placeholder="alumno@ejemplo.com" />
            </div>
            <div class="form-actions">
                <button type="button" class="cancel-btn" on:click={() => showInviteModal = false}>Cancelar</button>
                <button type="button" class="send-btn" on:click={invitarAlumno}>Enviar invitación</button>
            </div>
        </div>
    </div>
{/if}

{#if showCreateTaskModal}
    <div class="modal-overlay" on:click={() => showCreateTaskModal = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showCreateTaskModal = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Nueva tarea</h2>
                <p>Publica una tarea para la clase</p>
            </div>

            <form on:submit|preventDefault={crearTarea}>
                <div class="form-group">
                    <label for="taskTitle">Título</label>
                    <input id="taskTitle" type="text" bind:value={newTask.title} required />
                </div>
                <div class="form-group">
                    <label for="taskDescription">Descripción</label>
                    <textarea id="taskDescription" rows="4" bind:value={newTask.description} required></textarea>
                </div>
                <div class="form-group">
                    <label for="taskUrls">Enlaces de apoyo</label>
                    <textarea
                        id="taskUrls"
                        rows="3"
                        bind:value={taskUrlsText}
                        placeholder="Pega enlaces separados por coma o una URL por línea"
                    ></textarea>
                </div>
                <div class="form-group">
                    <label for="taskImages">Fotos / material visual</label>
                    <input id="taskImages" type="file" accept="image/*" multiple on:change={handleTaskImages} />
                    {#if taskImages.length > 0}
                        <div class="files" style="margin-top: 8px;">
                            {#each taskImages as file, idx (file.name + file.lastModified)}
                                <div class="file task-file-row">
                                    <span>{file.name}</span>
                                    <button type="button" class="secondary-button tiny-btn" on:click={() => removeTaskImage(idx)}>Quitar</button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
                <div class="form-group">
                    <label for="taskDueDate">Fecha límite</label>
                    <input id="taskDueDate" type="date" bind:value={newTask.dueDate} />
                </div>
                <div class="form-group">
                    <label for="taskAllowAny">Tipos de archivo</label>
                    <select id="taskAllowAny" bind:value={newTask.allowAnyFileType}>
                        <option value={true}>Permitir cualquier tipo</option>
                        <option value={false}>Restringir por extensión</option>
                    </select>
                </div>
                {#if !toBool(newTask.allowAnyFileType)}
                    <div class="form-group">
                        <label for="taskExtensions">Extensiones permitidas</label>
                        <input id="taskExtensions" type="text" bind:value={newTask.allowedExtensions} placeholder="pdf, docx, zip, py" />
                    </div>
                {/if}
                <div class="form-group">
                    <label for="taskMaxFiles">Máximo archivos por entrega</label>
                    <input id="taskMaxFiles" type="number" min="1" max="50" bind:value={newTask.maxFiles} />
                </div>
                <div class="form-group">
                    <label for="taskMaxSize">Tamaño máximo por archivo (MB)</label>
                    <input id="taskMaxSize" type="number" min="1" max="1024" bind:value={newTask.maxFileSizeMb} />
                </div>
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showCreateTaskModal = false}>Cancelar</button>
                    <button type="submit" class="send-btn" disabled={isSubmittingTask}>
                        {isSubmittingTask ? 'Creando...' : 'Crear tarea'}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

{#if showEditTaskModal}
    <div class="modal-overlay" on:click={() => showEditTaskModal = false}>
        <div class="modal-card" on:click|stopPropagation>
            <button class="modal-close" on:click={() => showEditTaskModal = false} aria-label="Cerrar">×</button>
            <div class="form-header">
                <h2>Editar tarea</h2>
                <p>Actualiza contenido, archivos y configuración de entrega</p>
            </div>

            <form on:submit|preventDefault={saveEditedTask}>
                <div class="form-group">
                    <label for="editTaskTitle">Título</label>
                    <input id="editTaskTitle" type="text" bind:value={editTaskTitle} required />
                </div>
                <div class="form-group">
                    <label for="editTaskDescription">Descripción</label>
                    <textarea id="editTaskDescription" rows="4" bind:value={editTaskDescription} required></textarea>
                </div>
                <div class="form-group">
                    <label for="editTaskUrls">Enlaces</label>
                    <textarea
                        id="editTaskUrls"
                        rows="3"
                        bind:value={editTaskUrlsText}
                        placeholder="Una URL por línea o separadas por coma"
                    ></textarea>
                </div>
                <div class="form-group">
                    <label for="editTaskDueDate">Fecha límite</label>
                    <input id="editTaskDueDate" type="date" bind:value={editTaskDueDate} />
                </div>
                <div class="form-group">
                    <label for="editTaskAllowAny">Tipos de archivo</label>
                    <select id="editTaskAllowAny" bind:value={editTaskAllowAnyFileType}>
                        <option value={true}>Permitir cualquier tipo</option>
                        <option value={false}>Restringir por extensión</option>
                    </select>
                </div>
                {#if !toBool(editTaskAllowAnyFileType)}
                    <div class="form-group">
                        <label for="editTaskExtensions">Extensiones permitidas</label>
                        <input id="editTaskExtensions" type="text" bind:value={editTaskAllowedExtensions} placeholder="pdf, docx, zip, py" />
                    </div>
                {/if}
                <div class="form-group">
                    <label for="editTaskMaxFiles">Máximo archivos por entrega</label>
                    <input id="editTaskMaxFiles" type="number" min="1" max="50" bind:value={editTaskMaxFiles} />
                </div>
                <div class="form-group">
                    <label for="editTaskMaxSize">Tamaño máximo por archivo (MB)</label>
                    <input id="editTaskMaxSize" type="number" min="1" max="1024" bind:value={editTaskMaxFileSizeMb} />
                </div>
                <div class="form-group">
                    <label>Fotos actuales</label>
                    {#if editTaskExistingPhotos.length === 0}
                        <div class="task-due">No hay fotos guardadas.</div>
                    {:else}
                        <div class="task-photos-grid">
                            {#each editTaskExistingPhotos as photo, idx (photo)}
                                <div class="task-photo-box">
                                    <img src={getTaskImageSource(photo)} alt="foto tarea" />
                                    <button type="button" class="secondary-button tiny-btn" on:click={() => removeEditTaskExistingPhoto(idx)}>
                                        Quitar
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
                <div class="form-group">
                    <label for="editTaskImages">Añadir más fotos</label>
                    <input id="editTaskImages" type="file" accept="image/*" multiple on:change={handleEditTaskImages} />
                    {#if editTaskNewImages.length > 0}
                        <div class="files" style="margin-top: 8px;">
                            {#each editTaskNewImages as file, idx (file.name + file.lastModified)}
                                <div class="file task-file-row">
                                    <span>{file.name}</span>
                                    <button type="button" class="secondary-button tiny-btn" on:click={() => removeEditTaskNewImage(idx)}>
                                        Quitar
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
                <div class="form-actions">
                    <button type="button" class="cancel-btn" on:click={() => showEditTaskModal = false}>Cancelar</button>
                    <button type="submit" class="send-btn" disabled={isUpdatingTask}>
                        {isUpdatingTask ? 'Guardando...' : 'Guardar cambios'}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

<div class="class-container dashboard-shell">
    <div class="class-header">
        <div class="portada-wrap"><img src={getClassImageSource()} alt="" class="portada-image" /></div>
        <div class="class-header-content dashboard-identity">
            <div class="dashboard-badge">Panel de profesorado</div>
            <h1>{classData.name || 'Clase'} · Dashboard</h1>
            <p>{classData.description || 'Gestión académica y seguimiento de entregas'}</p>
            <p>Docente principal: {classData.teacher_name || '-'}</p>
            <div class="dashboard-mini-stats">
                <div><span>Alumnos</span><strong>{stats.total_students}</strong></div>
                <div><span>Tareas</span><strong>{stats.total_tasks}</strong></div>
                <div><span>Entrega</span><strong>{stats.delivery_rate}%</strong></div>
            </div>
        </div>
    </div>

    <div class="class-tabs">
        <button class="tab-button" class:active={activeTab === 'alumnos'} on:click={() => activeTab = 'alumnos'}>Alumnos</button>
        <button class="tab-button" class:active={activeTab === 'tareas'} on:click={() => activeTab = 'tareas'}>Tareas</button>
        <button class="tab-button" class:active={activeTab === 'calificaciones'} on:click={() => activeTab = 'calificaciones'}>Calificaciones</button>
        <button class="tab-button" class:active={activeTab === 'configuracion'} on:click={() => activeTab = 'configuracion'}>Configuración</button>
    </div>

    <div class="class-content">
        <div class="main-content">
            {#if isLoading}
                <div class="announcement-item">
                    <div class="announcement-title">Cargando dashboard...</div>
                </div>
            {/if}

            {#if !isLoading && activeTab === 'alumnos'}
                <div class="card-title">
                    Alumnos ({students.length})
                    <button class="action-button" on:click={() => showInviteModal = true}>Invitar alumno</button>
                </div>

                {#if students.length === 0}
                    <div class="announcement-item">
                        <div class="announcement-title">No hay alumnos en esta clase</div>
                    </div>
                {:else}
                    {#each students as student}
                        <div class="student-item">
                            <div class="avatar">{student.avatar}</div>
                            <div class="student-info">
                                <div class="student-name">{displayName(student)}</div>
                                <div class="student-email">{student.email}</div>
                                <div class="task-due">
                                    Entregadas: {student.delivered_tasks || 0} • Pendientes: {student.pending_tasks || 0}
                                    {#if student.average_grade}
                                        • Promedio: {student.average_grade}/10
                                    {/if}
                                </div>
                            </div>
                            <span class="task-status {parseStudentStatusClass(student.status)}">
                                {parseStudentStatusLabel(student.status)}
                            </span>
                        </div>
                    {/each}
                {/if}
            {/if}

            {#if !isLoading && activeTab === 'tareas'}
                <div class="card-title">
                    Tareas ({tasks.length})
                    <button class="action-button" on:click={() => showCreateTaskModal = true}>Crear tarea</button>
                </div>

                {#if tasks.length === 0}
                    <div class="announcement-item">
                        <div class="announcement-title">No hay tareas creadas</div>
                    </div>
                {:else}
                    {#each tasks as task}
                        <div class="task-item task-item-expanded">
                            <a class="task-row task-row-link" href={`/clases/clase-${id}/tarea-${task.id}`}>
                                <div class="task-icon"><i class="fa-solid fa-file-lines"></i></div>
                                <div class="task-info">
                                    <div class="task-title">{task.title}</div>
                                    <div class="task-due">Fecha límite: {formatDate(task.due_at)}</div>
                                </div>
                                <span class="task-status {parseTaskStatus(task.status)}">
                                    {task.status === 'cerrada' ? 'Cerrada' : 'Activa'}
                                </span>
                            </a>
                            <div class="task-meta-row">
                                <span class="task-due">Entregadas: {task.delivered_count}/{task.total_students}</span>
                                <span class="task-due">Por calificar: {task.to_grade_count}</span>
                                <span class="task-due">Promedio: {task.average_grade || '-'}</span>
                                <span class="task-due">Enlaces: {task.urls?.length || 0}</span>
                                <span class="task-due">Fotos: {task.photos?.length || 0}</span>
                                <button class="secondary-button tiny-btn" on:click={() => openEditTask(task)}>
                                    Editar
                                </button>
                                <button class="secondary-button tiny-btn danger-soft" on:click={() => deleteTask(task.id)}>
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    {/each}
                {/if}
            {/if}

            {#if !isLoading && activeTab === 'calificaciones'}
                <div class="average-card">
                    <div class="average-label">Promedio general de la clase</div>
                    <div class="average-number">{stats.class_average_grade || '-'}</div>
                </div>

                <div class="card-title">Libreta de calificaciones</div>
                {#if tasks.length === 0}
                    <div class="announcement-item">
                        <div class="announcement-title">Crea tareas para empezar a calificar.</div>
                    </div>
                {:else}
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label for="selectedTask">Tarea</label>
                        <select
                            id="selectedTask"
                            bind:value={selectedTaskId}
                            on:change={loadSelectedTaskDetail}
                        >
                            {#each tasks as task}
                                <option value={String(task.id)}>
                                    {task.title} ({formatDate(task.due_at)})
                                </option>
                            {/each}
                        </select>
                    </div>

                    {#if selectedTaskDetail && selectedTaskDetail.delivered_students.length > 0}
                        {#each selectedTaskDetail.delivered_students as delivered}
                            <div class="grade-item">
                                <div class="grade-info">
                                    <div class="grade-task">{displayName(delivered)}</div>
                                    <div class="grade-date">{delivered.email}</div>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px; width: 62%;">
                                    <input
                                        type="number"
                                        min="0"
                                        max="10"
                                        step="0.01"
                                        class="grade-inline-input"
                                        bind:value={gradingValues[delivered.id]}
                                        placeholder="Nota (0-10)"
                                    />
                                    <input
                                        type="text"
                                        class="grade-inline-feedback"
                                        bind:value={feedbackValues[delivered.id]}
                                        placeholder="Feedback (opcional)"
                                    />
                                    <button
                                        class="action-button"
                                        on:click={() => guardarCalificacion(delivered.id)}
                                        disabled={savingByStudent[delivered.id]}
                                    >
                                        {savingByStudent[delivered.id] ? 'Guardando...' : 'Guardar'}
                                    </button>
                                </div>
                            </div>
                        {/each}
                    {:else}
                        <div class="announcement-item">
                            <div class="announcement-title">Esta tarea aún no tiene entregas.</div>
                        </div>
                    {/if}

                    {#if selectedTaskDetail && selectedTaskDetail.pending_students.length > 0}
                        <div class="card-title" style="margin-top: 22px;">
                            Pendientes de entrega ({selectedTaskDetail.pending_students.length})
                        </div>
                        {#each selectedTaskDetail.pending_students as pending}
                            <div class="student-item">
                                <div class="avatar">{(pending.username || 'U').charAt(0).toUpperCase()}</div>
                                <div class="student-info">
                                    <div class="student-name">{displayName(pending)}</div>
                                    <div class="student-email">{pending.email}</div>
                                </div>
                                <span class="task-status atrasada">Sin entregar</span>
                            </div>
                        {/each}
                    {/if}
                {/if}
            {/if}

            {#if !isLoading && activeTab === 'configuracion'}
                <div class="card-title">Configuración de clase</div>
                <div class="card">
                    <div class="form-group">
                        <label for="classSettingsName">Nombre de la clase</label>
                        <input id="classSettingsName" type="text" bind:value={classSettingsName} required />
                    </div>
                    <div class="form-group">
                        <label for="classSettingsDescription">Descripción</label>
                        <textarea id="classSettingsDescription" rows="4" bind:value={classSettingsDescription}></textarea>
                    </div>
                    <div class="form-group">
                        <label for="classSettingsBanner">Actualizar banner</label>
                        <input id="classSettingsBanner" type="file" accept="image/*" on:change={handleClassSettingsBanner} />
                        {#if classSettingsBannerFile}
                            <div class="task-due" style="margin-top: 8px;">Nuevo archivo: {classSettingsBannerFile.name}</div>
                        {/if}
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" bind:checked={removeCurrentBanner} />
                            Quitar banner actual
                        </label>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
                        <button class="action-button" on:click={saveClassSettings} disabled={isSavingClassSettings}>
                            {isSavingClassSettings ? 'Guardando...' : 'Guardar cambios'}
                        </button>
                        <button class="secondary-button" on:click={() => { classSettingsName = classData.name || ''; classSettingsDescription = classData.description || ''; classSettingsBannerFile = null; removeCurrentBanner = false; }}>
                            Revertir
                        </button>
                    </div>
                    <div class="task-due" style="margin-top: 12px;">
                        ID clase: {classData.id} • Creada: {formatDate(classData.created_at)}
                    </div>
                </div>
            {/if}
        </div>

        <div class="sidebar">
            <div class="card">
                <div class="card-title">Estadísticas</div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <span>Alumnos</span>
                    <span style="font-weight: 600;">{stats.total_students}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <span>Tareas</span>
                    <span style="font-weight: 600;">{stats.total_tasks}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <span>Progreso entregas</span>
                    <span style="font-weight: 600;">{stats.delivery_rate}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0;">
                    <span>Próxima entrega</span>
                    <span style="font-weight: 600;">{formatDate(stats.next_due_at)}</span>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Acciones</div>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => showInviteModal = true}>
                    Invitar alumnos
                </button>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => showCreateTaskModal = true}>
                    Crear tarea
                </button>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => activeTab = 'configuracion'}>
                    Configurar clase
                </button>
                <button class="secondary-button" style="width: 100%; margin-bottom: 8px;" on:click={() => loadDashboard()}>
                    Recargar
                </button>
                <a href={`/clases/clase-${id}`} class="secondary-button" style="width: 100%;">
                    Volver a clase
                </a>
            </div>

            <div class="card">
                <div class="card-title">Docentes</div>
                {#if teachers.length === 0}
                    <div class="task-due">Sin profesorado registrado.</div>
                {:else}
                    {#each teachers as teacher}
                        <div class="student-item">
                            <div class="avatar">{teacher.avatar}</div>
                            <div class="student-info">
                                <div class="student-name">{displayName(teacher)}</div>
                                <div class="student-email">{teacher.email}</div>
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
</div>

<style>
    .send-btn {
        padding: 10px 20px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
    }

    .send-btn:hover {
        background: var(--primary-dark);
    }

    .cancel-btn {
        padding: 10px 20px;
        background: #f1f3f4;
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        cursor: pointer;
    }

    .grade-inline-input {
        width: 92px;
        padding: 10px 12px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }

    .grade-inline-feedback {
        flex: 1;
        min-width: 0;
        padding: 10px 12px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }

    .grade-inline-input:focus,
    .grade-inline-feedback:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.12);
    }

    .tiny-btn {
        padding: 6px 10px;
        font-size: 0.82rem;
        border-radius: 8px;
    }

    .danger-soft {
        border-color: #f2b8b5;
        color: #b42318;
        background: #fff5f5;
    }

    .task-file-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
    }

    .task-photos-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 10px;
    }

    .task-photo-box {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .task-photo-box img {
        width: 100%;
        height: 96px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }

    .dashboard-shell {
        background: linear-gradient(180deg, #f7f8fb 0%, #eef2f7 100%);
    }

    .dashboard-shell .class-header {
        border: 1px solid #d0d9e7;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    }

    .dashboard-identity h1 {
        letter-spacing: 0.2px;
        font-size: 2rem;
    }

    .dashboard-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 6px 12px;
        background: #11243d;
        color: #edf2fa;
        font-weight: 600;
        font-size: 0.78rem;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .dashboard-mini-stats {
        margin-top: 10px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .dashboard-mini-stats div {
        min-width: 110px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #dbe4f3;
        padding: 8px 10px;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .dashboard-mini-stats span {
        color: #4d5c74;
        font-size: 0.78rem;
    }

    .dashboard-mini-stats strong {
        color: #18253a;
        font-size: 1.05rem;
    }

    .dashboard-shell .card,
    .dashboard-shell .task-item,
    .dashboard-shell .announcement-item {
        border-color: #d8e1ee;
    }

    @media (max-width: 980px) {
        .grade-item {
            flex-direction: column;
            align-items: stretch;
            gap: 10px;
        }
    }
</style>
