<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { browser } from "$app/environment";
    import { urlip, urlMedia } from "$lib/config";
    import { showAlert } from "$lib/store/alertStore.js";
    import Alert from "$lib/components/alert.svelte";
    import "$lib/style/inClass.css";
    import "$lib/style/task.css";
    import { fetchWithRateLimit } from "$lib/utils/fetchWithRateLimit";

    // Interfaces
    interface MemberInfo {
        id: number;
        username: string;
        first_name?: string;
        last_name?: string;
        email?: string;
        role?: string;
    }
    interface SubmissionFile {
        id: number;
        file_url: string;
        original_name: string;
        size_bytes: number;
    }
    interface DeliveredStudentInfo extends MemberInfo {
        submission_id?: number;
        delivered_at?: string;
        grade?: string | null;
        files?: SubmissionFile[];
    }
    interface TaskDetail {
        id: number;
        title: string;
        description: string;
        clase_id: string;
        due_at: string | null;
        allow_any_file_type: boolean;
        allowed_extensions: string[];
        max_files: number;
        max_file_size_mb: number;
        photos: string[];
        urls: string[];
        creator_info: MemberInfo;
        is_teacher: boolean;
        created_at: string;
        class_members: MemberInfo[];
        delivered_students: DeliveredStudentInfo[];
        pending_students: MemberInfo[];
        grades: Array<{ student_id: number; grade: string }>;
        delivered_count: number;
        pending_count: number;
        total_students: number;
        is_delivered?: boolean;
        grade?: string | null;
        submission?: any;
    }
    interface TaskDetailResponse {
        is_teacher: boolean;
        task: TaskDetail;
    }

    $: taskId = getTaskIdFromPath($page.url.pathname);
    let isLoading = true;
    let loadError = "";
    let taskResponse: TaskDetailResponse | null = null;
    let selectedImage = "";
    let selectedSubmissionFiles: File[] = [];
    let isSubmitting = false;
    let grading = new Map<number, string>(); // student_id -> grade input

    $: task = taskResponse?.task ?? null;
    $: isTeacher = taskResponse?.is_teacher ?? false;
    $: delivered = task?.delivered_students ?? [];
    $: pending = task?.pending_students ?? [];
    $: teacherMembers = (task?.class_members ?? []).filter(
        (m) => m.role === "teacher" || m.role === "assistant",
    );
    $: dueInfo = getDueInfo(task?.due_at);
    $: completionRate = task
        ? Math.round((task.delivered_count / task.total_students) * 100)
        : 0;
    $: studentDeliveryStatus = task?.is_delivered
        ? task.due_at &&
          new Date(task.submission?.delivered_at) > new Date(task.due_at)
            ? { label: "Entregado con retraso", className: "atrasada" }
            : { label: "Entregado", className: "entregada" }
        : task?.due_at && new Date(task.due_at) < new Date()
          ? { label: "Sin entregar", className: "atrasada" }
          : { label: "Pendiente", className: "pendiente" };

    onMount(async () => {
        if (!browser) return;
        const token = localStorage.getItem("token");
        if (!token) window.location.href = "/auth/login";
        else await loadTask();
    });

    async function loadTask() {
        const token = localStorage.getItem("token");
        if (!token) return;
        isLoading = true;
        try {
            const res = await fetchWithRateLimit(
                `${urlip}class/obtainTaskDetail/${taskId}/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        authorization: token,
                    },
                },
            );
            const data = await readJsonResponse(res);
            if (!res.ok)
                throw new Error(data?.Error || "Error al cargar tarea");
            taskResponse = data;
            //console.log(taskResponse)
            if (data.task.grades) {
                data.task.grades.forEach(
                    (g: { student_id: number; grade: string }) =>
                        grading.set(g.student_id, g.grade),
                );
            }
        } catch (err: any) {
            loadError = err.message || "Error de conexión";
            taskResponse = null;
        } finally {
            isLoading = false;
        }
    }

    async function submitTask() {
        if (!task || !selectedSubmissionFiles.length) {
            showAlert("Error", "Selecciona al menos un archivo", "orange");
            return;
        }
        const token = localStorage.getItem("token");
        if (!token) return;

        const formData = new FormData();
        selectedSubmissionFiles.forEach((f) => formData.append("files", f));

        isSubmitting = true;
        try {
            const res = await fetch(`${urlip}class/submitTask/${task.id}/`, {
                method: "POST",
                headers: { authorization: token },
                body: formData,
            });
            const data = await readJsonResponse(res);
            if (!res.ok) throw new Error(data?.Error || "Error al entregar");
            showAlert("Listo", "Tarea entregada", "green");
            selectedSubmissionFiles = [];
            await loadTask();
        } catch (err: any) {
            showAlert("Error", err.message, "red");
        } finally {
            isSubmitting = false;
        }
    }

    async function gradeStudent(studentId: number, grade: string) {
        if (!task) return;
        const token = localStorage.getItem("token");
        if (!token) return;
        try {
            const res = await fetch(
                `${urlip}class/gradeTaskSubmission/${task.id}/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        authorization: token,
                    },
                    body: JSON.stringify({ student_id: studentId, grade }),
                },
            );
            const data = await readJsonResponse(res);
            if (!res.ok) throw new Error(data?.Error || "Error al calificar");
            showAlert("Nota guardada", `Nota ${grade} asignada`, "green");
            grading.set(studentId, grade);
            await loadTask();
        } catch (err: any) {
            showAlert("Error", err.message, "red");
        }
    }

    function handleStudentFiles(e: Event) {
        if (!task) return;
        const input = e.currentTarget as HTMLInputElement;
        const files = Array.from(input.files || []);
        input.value = "";

        const maxFiles = Math.max(1, task.max_files);
        const allowedExt = task.allow_any_file_type
            ? null
            : (task.allowed_extensions ?? []).map((e) =>
                  e.replace(".", "").toLowerCase(),
              );
        const next = [...selectedSubmissionFiles];
        for (const f of files) {
            if (next.length >= maxFiles) {
                showAlert("Aviso", `Máximo ${maxFiles} archivo(s)`, "orange");
                break;
            }
            const ext = f.name.split(".").pop()?.toLowerCase();
            if (
                !task.allow_any_file_type &&
                (!ext || !allowedExt?.includes(ext))
            ) {
                showAlert(
                    "Aviso",
                    `Extensión no permitida: ${f.name}`,
                    "orange",
                );
                continue;
            }
            if (f.size > task.max_file_size_mb * 1024 * 1024) {
                showAlert(
                    "Aviso",
                    `${f.name} excede ${task.max_file_size_mb} MB`,
                    "orange",
                );
                continue;
            }
            if (
                !next.some(
                    (ex) =>
                        ex.name === f.name &&
                        ex.size === f.size &&
                        ex.lastModified === f.lastModified,
                )
            ) {
                next.push(f);
            }
        }
        selectedSubmissionFiles = next;
    }

    function removeSelectedFile(idx: number) {
        selectedSubmissionFiles = selectedSubmissionFiles.filter(
            (_, i) => i !== idx,
        );
    }
    function clearSelectedFiles() {
        selectedSubmissionFiles = [];
    }

    // Helpers
    const formatDate = (d?: string | null) =>
        d
            ? new Date(d).toLocaleDateString("es-ES", {
                  day: "2-digit",
                  month: "short",
                  year: "numeric",
              })
            : "Sin fecha";
    const formatDateTime = (d?: string | null) =>
        d
            ? new Date(d).toLocaleString("es-ES", {
                  day: "2-digit",
                  month: "short",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
              })
            : "Sin fecha";
    const formatBytes = (b: number) =>
        b < 1024
            ? `${b} B`
            : b < 1048576
              ? `${(b / 1024).toFixed(1)} KB`
              : `${(b / 1048576).toFixed(1)} MB`;
    const getDisplayName = (u?: MemberInfo | null) =>
        u
            ? u.first_name || u.last_name
                ? `${u.first_name} ${u.last_name}`.trim()
                : u.username
            : "Usuario";
    const getSecondaryLine = (u?: MemberInfo | null) =>
        u && (u.first_name || u.last_name) ? `@${u.username}` : u?.email || "";
    const initials = (u?: MemberInfo | null) => {
        const name = getDisplayName(u).replace("@", "");
        const parts = name.split(" ").filter(Boolean);
        if (!parts.length) return "U";
        if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
        return (parts[0][0] + parts[1][0]).toUpperCase();
    };
    const getDueInfo = (due?: string | null) => {
        if (!due)
            return {
                formatted: "Sin fecha límite",
                relative: "",
                isLate: false,
            };
        const dueDate = new Date(due);
        if (isNaN(dueDate.getTime()))
            return { formatted: due, relative: "", isLate: false };
        const diff = dueDate.getTime() - Date.now();
        const days = Math.ceil(Math.abs(diff) / (1000 * 60 * 60 * 24));
        if (diff < 0)
            return {
                formatted: formatDateTime(due),
                relative: `Retrasada ${days} día${days === 1 ? "" : "s"}`,
                isLate: true,
            };
        return {
            formatted: formatDateTime(due),
            relative:
                days === 0
                    ? "Vence hoy"
                    : `Faltan ${days} día${days === 1 ? "" : "s"}`,
            isLate: false,
        };
    };

    function normalizeAssetUrl(photo: string): string {
        const value = String(photo || "");
        const apiBase = urlMedia.replace(/\/+$/, "");

        if (value.match(/^https?:\/\/[^/]+\/media\//)) {
            return value.replace(/\/media\//, "/api/media/");
        }
        return value;
    }
    const acceptAttr = () =>
        task && !task.allow_any_file_type
            ? task.allowed_extensions
                  .map((e) => `.${e.replace(".", "")}`)
                  .join(",")
            : undefined;

    function openImagePreview(url: string) {
        selectedImage = url;
    }
    function closeImagePreview() {
        selectedImage = "";
    }

    function getTaskIdFromPath(pathname: string): string {
        const taskSegment = pathname
            .split("/")
            .find((segment) => segment.startsWith("tarea-"));
        return taskSegment?.replace("tarea-", "") || $page.params.id || "";
    }

    async function readJsonResponse(response: Response) {
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            throw new Error(
                "La API devolvió HTML en vez de JSON. Revisa que la ruta del endpoint exista y termine con /.",
            );
        }
        return response.json();
    }
</script>

<svelte:window on:keydown={(e) => e.key === "Escape" && closeImagePreview()} />
<Alert />

<div class="class-container task-page-container">
    {#if isLoading}
        <div class="main-content task-state-card">
            <div class="loading-spinner"></div>
            <p>Cargando...</p>
        </div>
    {:else if loadError}
        <div class="main-content task-state-card">
            <i class="fa-solid fa-circle-exclamation"></i>
            <p>{loadError}</p>
            <button on:click={loadTask}>Reintentar</button>
        </div>
    {:else if task}
        <div class="task-layout-grid">
            <section class="main-content classroom-main">
                <div class="task-title-row">
                    <div class="task-icon-circle">
                        <i class="fa-solid fa-clipboard-list"></i>
                    </div>
                    <div class="task-title-block">
                        <h1>{task.title}</h1>
                        <p>
                            {getDisplayName(task.creator_info)} • {formatDate(
                                task.created_at,
                            )}
                        </p>
                    </div>
                    <a
                        class="secondary-button task-back-link"
                        href={`/clases/clase-${task.clase_id}`}>Volver</a
                    >
                </div>

                <div class="task-points-row">
                    <span class="task-points">Tarea de clase</span>
                    <span class="task-due" class:late={dueInfo.isLate}>
                        Fecha de entrega: {dueInfo.formatted}
                        {#if dueInfo.relative}<strong
                                >({dueInfo.relative})</strong
                            >{/if}
                    </span>
                </div>
                <div class="task-divider"></div>
                <div class="task-description">
                    {task.description || "Sin descripción."}
                </div>
                <div class="task-detail-badges">
                    <span class="detail-chip"
                        >Máx. archivos: {task.max_files}</span
                    >
                    <span class="detail-chip"
                        >Tamaño máx.: {task.max_file_size_mb} MB</span
                    >
                    <span class="detail-chip">
                        {task.allow_any_file_type
                            ? "Cualquier tipo"
                            : `Extensiones: ${(task.allowed_extensions ?? []).map((e) => e.replace(".", "")).join(", ")}`}
                    </span>
                </div>

                {#if task.photos?.length}
                    <div class="task-section-title">Materiales</div>
                    <div class="task-photo-grid">
                        {#each task.photos as photo}
                            <button
                                class="task-photo-card"
                                on:click={() =>
                                    openImagePreview(normalizeAssetUrl(photo))}
                            >
                                <img
                                    src={normalizeAssetUrl(photo)}
                                    alt="material"
                                    loading="lazy"
                                />
                            </button>
                        {/each}
                    </div>
                {/if}

                {#if task.urls?.length}
                    <div class="task-section-title">Enlaces</div>
                    <div class="announcement-urls">
                        {#each task.urls as link}
                            <a href={link} target="_blank" rel="noreferrer"
                                >{link}</a
                            >
                        {/each}
                    </div>
                {/if}
            </section>

            <aside class="sidebar classroom-sidebar">
                {#if isTeacher}
                    <div class="card">
                        <div class="card-title">Resumen</div>
                        <div class="task-summary-row">
                            <span>Total estudiantes</span><strong
                                >{task.total_students}</strong
                            >
                        </div>
                        <div class="task-summary-row">
                            <span>Entregaron</span><strong
                                >{task.delivered_count}</strong
                            >
                        </div>
                        <div class="task-summary-row">
                            <span>Pendientes</span><strong
                                >{task.pending_count}</strong
                            >
                        </div>
                        <div class="task-progress-wrap">
                            <div class="task-progress-label">
                                Progreso {completionRate}%
                            </div>
                            <div class="task-progress-track">
                                <div
                                    class="task-progress-fill"
                                    style="width: {completionRate}%"
                                ></div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title">Calificaciones</div>
                        {#each delivered as student}
                            <div class="student-item task-member-item compact">
                                <div class="avatar">{initials(student)}</div>
                                <div class="student-info">
                                    <div class="student-name">
                                        {getDisplayName(student)}
                                    </div>
                                    {#if getSecondaryLine(student)}<div
                                            class="student-email"
                                        >
                                            {getSecondaryLine(student)}
                                        </div>{/if}
                                </div>
                                <div class="grade-panel">
                                    <input
                                        type="text"
                                        placeholder="Nota"
                                        value={grading.get(student.id) ??
                                            student.grade ??
                                            ""}
                                        on:input={(e) =>
                                            grading.set(
                                                student.id,
                                                (e.target as HTMLInputElement)
                                                    .value,
                                            )}
                                        class="grade-input"
                                    />
                                    <button
                                        class="action-button small"
                                        on:click={() =>
                                            gradeStudent(
                                                student.id,
                                                grading.get(student.id) ??
                                                    student.grade ??
                                                    "",
                                            )}>Guardar</button
                                    >
                                </div>
                            </div>
                            {#if student.files?.length}
                                <div class="submission-files">
                                    <div class="task-list-title">
                                        Archivos entregados
                                    </div>
                                    {#each student.files as file}
                                        <a
                                            href={file.file_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            class="submitted-file"
                                        >
                                            <div class="submitted-file-main">
                                                <div
                                                    class="submitted-file-name"
                                                >
                                                    {file.original_name}
                                                </div>
                                                <div
                                                    class="submitted-file-meta"
                                                >
                                                    {formatBytes(
                                                        file.size_bytes,
                                                    )}
                                                </div>
                                            </div>
                                            <i
                                                class="fa-solid fa-up-right-from-square"
                                            ></i>
                                        </a>
                                    {/each}
                                </div>
                            {/if}
                        {/each}
                        {#if !delivered.length}<div class="student-work-empty">
                                Aún no hay entregas.
                            </div>{/if}
                    </div>

                    <div class="card">
                        <div class="card-title">
                            Pendientes ({pending.length})
                        </div>
                        {#each pending as student}
                            <div class="student-item task-member-item compact">
                                <div class="avatar">{initials(student)}</div>
                                <div class="student-info">
                                    <div class="student-name">
                                        {getDisplayName(student)}
                                    </div>
                                    {#if getSecondaryLine(student)}<div
                                            class="student-email"
                                        >
                                            {getSecondaryLine(student)}
                                        </div>{/if}
                                </div>
                                <span class="task-status atrasada"
                                    >Sin entregar</span
                                >
                            </div>
                        {/each}
                    </div>
                {:else}
                    <!-- Vista estudiante -->
                    <div class="card">
                        <div class="card-title">
                            Tu trabajo
                            <span
                                class="task-status {studentDeliveryStatus.className}"
                                >{studentDeliveryStatus.label}</span
                            >
                        </div>
                        {#if task.submission?.delivered_at}
                            <div class="student-work-date">
                                Entregado: {formatDateTime(
                                    task.submission.delivered_at,
                                )}
                            </div>
                        {/if}
                        {#if task.grade}<div class="student-work-date">
                                Calificación: {task.grade}
                            </div>{/if}
                        {#if task.submission?.files?.length}
                            <div class="task-list-title">Archivos enviados</div>
                            {#each task.submission.files as file}
                                <a
                                    class="submitted-file"
                                    href={file.file_url}
                                    target="_blank"
                                >
                                    <div class="submitted-file-main">
                                        <div class="submitted-file-name">
                                            {file.original_name}
                                        </div>
                                        <div class="submitted-file-meta">
                                            {formatBytes(file.size_bytes)}
                                        </div>
                                    </div>
                                    <i class="fa-solid fa-up-right-from-square"
                                    ></i>
                                </a>
                            {/each}
                        {:else}<div class="student-work-empty">
                                Aún no has entregado archivos.
                            </div>{/if}

                        <div class="task-list-title">Añadir archivos</div>
                        <input
                            type="file"
                            multiple
                            on:change={handleStudentFiles}
                            accept={acceptAttr()}
                            class="student-file-input"
                        />

                        {#if selectedSubmissionFiles.length}
                            <div class="selected-files-list">
                                {#each selectedSubmissionFiles as file, i}
                                    <div class="selected-file-item">
                                        <div>
                                            <div class="selected-file-name">
                                                {file.name}
                                            </div>
                                            <div class="selected-file-meta">
                                                {formatBytes(file.size)}
                                            </div>
                                        </div>
                                        <button
                                            type="button"
                                            on:click={() =>
                                                removeSelectedFile(i)}
                                            class="remove-file-btn"
                                            ><i class="fa-solid fa-xmark"
                                            ></i></button
                                        >
                                    </div>
                                {/each}
                            </div>
                            <button
                                type="button"
                                class="secondary-button clear-files-btn"
                                on:click={clearSelectedFiles}
                                >Limpiar selección</button
                            >
                        {/if}

                        <button
                            class="action-button submit-task-btn"
                            on:click={submitTask}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? "Entregando..." : "Entregar tarea"}
                        </button>
                        <div class="student-work-note">
                            Puedes añadir archivos hasta un máximo de {task.max_files}.
                        </div>
                    </div>
                    <!--
          <div class="card">
            <div class="card-title">Profesorado</div>
            {#if teacherMembers.length}
              {#each teacherMembers as teacher}
                <div class="student-item task-member-item compact">
                  <div class="avatar">{initials(teacher)}</div>
                  <div class="student-info">
                    <div class="student-name">{getDisplayName(teacher)}</div>
                    {#if getSecondaryLine(teacher)}<div class="student-email">{getSecondaryLine(teacher)}</div>{/if}
                  </div>
                </div>
              {/each}
            {:else}<div class="student-work-empty">No hay profesorado cargado.</div>{/if}
          </div>
          -->
                {/if}
            </aside>
        </div>
    {:else}
        <div class="main-content task-state-card">
            <i class="fa-solid fa-inbox"></i>
            <p>No se encontró información.</p>
        </div>
    {/if}
</div>

{#if selectedImage}
    <div class="image-preview-overlay" on:click={closeImagePreview}>
        <div class="image-preview-modal" on:click|stopPropagation>
            <button class="image-preview-close" on:click={closeImagePreview}
                >×</button
            >
            <img src={selectedImage} alt="Imagen ampliada" />
        </div>
    </div>
{/if}
