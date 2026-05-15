<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { browser } from "$app/environment";
    import { urlip } from "$lib/config";
    import { showAlert } from "$lib/store/alertStore.js";
    import Alert from "$lib/components/alert.svelte";
    import "$lib/style/inClass.css";
    import "$lib/style/task.css";
    import { fetchWithRateLimit } from "$lib/utils/fetchWithRateLimit";

    let id = $page.params.id ?? "";
    let isLoading = true;
    let loadError = "";
    let announcement: any = null;
    let comments: any[] = [];
    let commentsSort = "top";

    let newComment = "";
    let isSendingComment = false;

    let editingCommentId: number | null = null;
    let editingCommentContent = "";

    let replyingToCommentId: number | null = null;
    let replyDraftByComment: Record<number, string> = {};

    $: classId = announcement?.clase_public_id || "";
    $: canDeleteAnnouncement = Boolean(announcement?.can_delete);
    $: threadComments = buildThreadComments(comments, commentsSort);

    onMount(async () => {
        if (!browser) return;
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "/auth/login";
            return;
        }
        await loadAnnouncement();
    });

    function formatDate(dateValue: string | null | undefined) {
        if (!dateValue) return "Sin fecha";
        const date = new Date(dateValue);
        if (Number.isNaN(date.getTime())) return dateValue;
        return date.toLocaleString("es-ES");
    }

    function displayName(userInfo: any) {
        if (!userInfo) return "Usuario";
        const fullName =
            `${userInfo.first_name || ""} ${userInfo.last_name || ""}`.trim();
        return fullName || userInfo.username || "Usuario";
    }

    function dateToMillis(dateValue: string | null | undefined): number {
        if (!dateValue) return 0;
        const date = new Date(dateValue);
        if (Number.isNaN(date.getTime())) return 0;
        return date.getTime();
    }

    function getAnnouncementPhotoSource(photo: string): string {
        const value = String(photo || "");
        const apiBase = urlip.replace(/\/+$/, "");

        if (!value) return value;
        if (value.startsWith(`${apiBase}/media/`)) return value;
        if (value.startsWith("/api/media/")) {
            return `${apiBase.replace(/\/api$/, "")}${value}`;
        }
        if (value.startsWith("/media/")) return `${apiBase}${value}`;
        if (value.startsWith("media/")) return `${apiBase}/${value}`;

        try {
            const photoUrl = new URL(value);
            const apiUrl = new URL(apiBase);
            if (
                photoUrl.origin === apiUrl.origin &&
                photoUrl.pathname.startsWith("/media/")
            ) {
                return `${apiBase}${photoUrl.pathname}${photoUrl.search}${photoUrl.hash}`;
            }
        } catch {
            return value;
        }

        return value;
    }

    function buildThreadComments(rawComments: any[], sortMode: string): any[] {
        if (!Array.isArray(rawComments) || rawComments.length === 0) return [];

        const byId = new Map<number, any>();
        const roots: any[] = [];

        for (const item of rawComments) {
            byId.set(Number(item.id), {
                ...item,
                id: Number(item.id),
                parent_id:
                    item.parent_id !== null && item.parent_id !== undefined
                        ? Number(item.parent_id)
                        : null,
                replies: [],
            });
        }

        for (const comment of byId.values()) {
            if (comment.parent_id && byId.has(comment.parent_id)) {
                byId.get(comment.parent_id).replies.push(comment);
            } else {
                roots.push(comment);
            }
        }

        const sortByCreatedAsc = (a: any, b: any) =>
            dateToMillis(a.created_at) - dateToMillis(b.created_at);
        const sortByCreatedDesc = (a: any, b: any) =>
            dateToMillis(b.created_at) - dateToMillis(a.created_at);

        const sortChildren = (node: any) => {
            node.replies.sort(sortByCreatedAsc);
            for (const child of node.replies) {
                sortChildren(child);
            }
        };

        for (const root of roots) {
            sortChildren(root);
        }

        if (sortMode === "new") {
            roots.sort(sortByCreatedDesc);
        } else if (sortMode === "old") {
            roots.sort(sortByCreatedAsc);
        } else {
            roots.sort((a: any, b: any) => {
                const repliesDiff =
                    Number(b.replies_count || 0) - Number(a.replies_count || 0);
                if (repliesDiff !== 0) return repliesDiff;
                return sortByCreatedAsc(a, b);
            });
        }

        const flat: any[] = [];
        const walk = (node: any, depth: number) => {
            flat.push({ ...node, depth });
            for (const child of node.replies) {
                walk(child, depth + 1);
            }
        };

        for (const root of roots) {
            walk(root, 0);
        }

        return flat;
    }

    async function loadAnnouncement() {
        const token = localStorage.getItem("token");
        if (!token) return;

        isLoading = true;
        loadError = "";
        try {
            const response = await fetch(
                `${urlip}class/obtainAnnouncementDetail/${id}/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        authorization: `${token}`,
                    },
                },
            );
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data?.Error || "No se pudo cargar el anuncio");
            }

            announcement = data.announcement || null;
            comments = data.comments || [];
        } catch (error: any) {
            loadError = error?.message || "Error de conexión";
        } finally {
            isLoading = false;
        }
    }

    async function createComment(parentId: number | null = null) {
        const content = parentId
            ? (replyDraftByComment[parentId] || "").trim()
            : newComment.trim();

        if (!content) return;

        const token = localStorage.getItem("token");
        if (!token) return;

        isSendingComment = true;
        const payload: any = { content };
        if (parentId) payload.parent_id = parentId;

        const response = await fetch(
            `${urlip}class/createAnnouncementComment/${id}/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    authorization: `${token}`,
                },
                body: JSON.stringify(payload),
            },
        );
        const data = await response.json();
        isSendingComment = false;

        if (!response.ok) {
            showAlert("Error", data?.Error || "No se pudo comentar", "red");
            return;
        }

        if (parentId) {
            replyDraftByComment = { ...replyDraftByComment, [parentId]: "" };
            replyingToCommentId = null;
        } else {
            newComment = "";
        }
        await loadAnnouncement();
    }

    function startEditComment(comment: any) {
        editingCommentId = Number(comment.id);
        editingCommentContent = comment.content || "";
    }

    async function saveEditedComment() {
        if (!editingCommentId || !editingCommentContent.trim()) return;
        const token = localStorage.getItem("token");
        if (!token) return;

        const response = await fetch(
            `${urlip}class/manageAnnouncementComment/${editingCommentId}/`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    authorization: `${token}`,
                },
                body: JSON.stringify({ content: editingCommentContent.trim() }),
            },
        );
        const data = await response.json();
        if (!response.ok) {
            showAlert(
                "Error",
                data?.Error || "No se pudo editar el comentario",
                "red",
            );
            return;
        }

        editingCommentId = null;
        editingCommentContent = "";
        await loadAnnouncement();
    }

    async function deleteComment(commentId: number) {
        if (!confirm("¿Eliminar este comentario?")) return;
        const token = localStorage.getItem("token");
        if (!token) return;

        const response = await fetch(
            `${urlip}class/manageAnnouncementComment/${commentId}/`,
            {
                method: "DELETE",
                headers: {
                    authorization: `${token}`,
                },
            },
        );
        const data = await response.json();
        if (!response.ok) {
            showAlert(
                "Error",
                data?.Error || "No se pudo eliminar el comentario",
                "red",
            );
            return;
        }
        await loadAnnouncement();
    }

    async function deleteAnnouncement() {
        if (!announcement?.id) return;
        if (!confirm("¿Eliminar este anuncio?")) return;
        const token = localStorage.getItem("token");
        if (!token) return;

        const response = await fetch(
            `${urlip}class/manageAnnouncement/${announcement.id}/`,
            {
                method: "DELETE",
                headers: {
                    authorization: `${token}`,
                },
            },
        );
        const data = await response.json();
        if (!response.ok) {
            showAlert(
                "Error",
                data?.Error || "No se pudo eliminar el anuncio",
                "red",
            );
            return;
        }

        showAlert("Listo", "Anuncio eliminado", "green");
        window.location.href = classId ? `/clases/clase-${classId}` : "/clases";
    }
</script>

<Alert />

<div class="class-container forum-page">
    {#if isLoading}
        <div class="main-content task-state-card"><p>Cargando hilo...</p></div>
    {:else if loadError}
        <div class="main-content task-state-card">
            <p>{loadError}</p>
            <button class="secondary-button" on:click={loadAnnouncement}
                >Reintentar</button
            >
        </div>
    {:else if announcement}
        <div class="task-layout-grid forum-layout">
            <section class="main-content classroom-main">
                <article class="card forum-post">
                    <div class="task-title-row">
                        <div class="task-icon-circle">
                            <i class="fa-solid fa-comments"></i>
                        </div>
                        <div class="task-title-block">
                            <h1>{announcement.title}</h1>
                            <p>
                                {displayName(announcement.creator_info)} • publicado
                                {formatDate(announcement.created_at)}
                            </p>
                        </div>
                        {#if classId}
                            <a
                                class="secondary-button task-back-link"
                                href={`/clases/clase-${classId}`}>Volver</a
                            >
                        {/if}
                    </div>

                    <div class="task-divider"></div>
                    <div class="task-description forum-post-body">
                        {announcement.description || "Sin descripción."}
                    </div>

                    {#if announcement.photos?.length}
                        <div class="task-section-title">Adjuntos</div>
                        <div class="announcement-photos">
                            {#each announcement.photos as photo (photo)}
                                <img
                                    src={getAnnouncementPhotoSource(photo)}
                                    alt="foto anuncio"
                                />
                            {/each}
                        </div>
                    {/if}

                    {#if announcement.urls?.length}
                        <div class="task-section-title">Enlaces</div>
                        <div class="announcement-urls">
                            {#each announcement.urls as link (link)}
                                <a href={link} target="_blank" rel="noreferrer"
                                    >{link}</a
                                >
                            {/each}
                        </div>
                    {/if}
                </article>

                <section class="card forum-comments-block">
                    <div class="forum-comments-header">
                        <div class="card-title">
                            Discusión ({comments.length})
                        </div>
                        <select
                            class="forum-sort-select"
                            bind:value={commentsSort}
                        >
                            <option value="top">Top (más respuestas)</option>
                            <option value="new">Nuevos</option>
                            <option value="old">Antiguos</option>
                        </select>
                    </div>

                    <div class="forum-new-comment">
                        <textarea
                            rows="3"
                            bind:value={newComment}
                            placeholder="Comparte tu opinión..."
                        ></textarea>
                        <button
                            class="action-button"
                            on:click={() => createComment(null)}
                            disabled={isSendingComment}
                        >
                            {isSendingComment
                                ? "Publicando..."
                                : "Publicar comentario"}
                        </button>
                    </div>

                    {#if threadComments.length === 0}
                        <div
                            class="student-work-empty"
                            style="margin-top: 12px;"
                        >
                            Sé el primero en comentar.
                        </div>
                    {:else}
                        <div class="forum-thread-list">
                            {#each threadComments as comment (comment.id)}
                                <article
                                    class="forum-comment"
                                    style:margin-left={`${Math.min(comment.depth, 6) * 24}px`}
                                >
                                    <div class="forum-comment-head">
                                        <div class="announcement-author">
                                            {displayName(comment.author_info)}
                                        </div>
                                        <div class="forum-comment-meta">
                                            <span
                                                >{formatDate(
                                                    comment.created_at,
                                                )}</span
                                            >
                                            {#if Number(comment.replies_count || 0) > 0}
                                                <span
                                                    >• {comment.replies_count} respuesta(s)</span
                                                >
                                            {/if}
                                        </div>
                                    </div>

                                    {#if editingCommentId === comment.id}
                                        <div
                                            class="form-group"
                                            style="margin-top: 8px;"
                                        >
                                            <textarea
                                                rows="3"
                                                bind:value={
                                                    editingCommentContent
                                                }
                                            ></textarea>
                                        </div>
                                        <div class="forum-comment-actions">
                                            <button
                                                class="secondary-button"
                                                on:click={() => {
                                                    editingCommentId = null;
                                                    editingCommentContent = "";
                                                }}>Cancelar</button
                                            >
                                            <button
                                                class="action-button"
                                                on:click={saveEditedComment}
                                                >Guardar</button
                                            >
                                        </div>
                                    {:else}
                                        <div
                                            class="announcement-content forum-comment-content"
                                        >
                                            {comment.content}
                                        </div>
                                        <div class="forum-comment-actions">
                                            <button
                                                class="secondary-button"
                                                on:click={() => {
                                                    replyingToCommentId =
                                                        replyingToCommentId ===
                                                        comment.id
                                                            ? null
                                                            : comment.id;
                                                }}
                                            >
                                                Responder
                                            </button>
                                            {#if comment.can_edit}
                                                <button
                                                    class="secondary-button"
                                                    on:click={() =>
                                                        startEditComment(
                                                            comment,
                                                        )}>Editar</button
                                                >
                                            {/if}
                                            {#if comment.can_delete}
                                                <button
                                                    class="secondary-button forum-danger"
                                                    on:click={() =>
                                                        deleteComment(
                                                            comment.id,
                                                        )}>Eliminar</button
                                                >
                                            {/if}
                                        </div>
                                    {/if}

                                    {#if replyingToCommentId === comment.id}
                                        <div class="forum-reply-box">
                                            <textarea
                                                rows="2"
                                                bind:value={
                                                    replyDraftByComment[
                                                        comment.id
                                                    ]
                                                }
                                                placeholder="Responder a este comentario..."
                                            ></textarea>
                                            <div class="forum-comment-actions">
                                                <button
                                                    class="secondary-button"
                                                    on:click={() => {
                                                        replyingToCommentId =
                                                            null;
                                                        replyDraftByComment = {
                                                            ...replyDraftByComment,
                                                            [comment.id]: "",
                                                        };
                                                    }}
                                                >
                                                    Cancelar
                                                </button>
                                                <button
                                                    class="action-button"
                                                    on:click={() =>
                                                        createComment(
                                                            comment.id,
                                                        )}
                                                    disabled={isSendingComment}
                                                >
                                                    Responder
                                                </button>
                                            </div>
                                        </div>
                                    {/if}
                                </article>
                            {/each}
                        </div>
                    {/if}
                </section>
            </section>

            <aside class="sidebar classroom-sidebar">
                <div class="card">
                    <div class="card-title">Hilo</div>
                    <div class="task-due">
                        <strong>Comentarios:</strong>
                        {comments.length}
                    </div>
                    <div class="task-due">
                        <strong>Última actividad:</strong>
                        {formatDate(
                            announcement.last_activity_at ||
                                announcement.updated_at ||
                                announcement.created_at,
                        )}
                    </div>
                </div>

                {#if canDeleteAnnouncement}
                    <div class="card">
                        <div class="card-title">Gestión</div>
                        <button
                            class="secondary-button forum-danger"
                            on:click={deleteAnnouncement}
                        >
                            Eliminar anuncio
                        </button>
                    </div>
                {/if}
            </aside>
        </div>
    {/if}
</div>

<style>
    .forum-page {
        background: linear-gradient(180deg, #f5f7fb 0%, #eef3fa 100%);
    }

    .forum-layout {
        align-items: flex-start;
    }

    .forum-post {
        border: 1px solid #dbe3ef;
    }

    .forum-post-body {
        font-size: 1rem;
        line-height: 1.65;
    }

    .forum-comments-block {
        margin-top: 16px;
    }

    .forum-comments-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 10px;
    }

    .forum-sort-select {
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 8px 10px;
        background: #fff;
    }

    .forum-new-comment textarea,
    .forum-reply-box textarea {
        width: 100%;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        font: inherit;
    }

    .forum-thread-list {
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .forum-comment {
        border: 1px solid #dde4f0;
        border-radius: 12px;
        background: #fff;
        padding: 12px;
    }

    .forum-comment-head {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        flex-wrap: wrap;
    }

    .forum-comment-meta {
        color: #667085;
        font-size: 0.86rem;
        display: inline-flex;
        gap: 6px;
        align-items: center;
    }

    .forum-comment-content {
        margin-top: 6px;
    }

    .forum-comment-actions {
        margin-top: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .forum-reply-box {
        margin-top: 10px;
        border-top: 1px dashed #d0d9e7;
        padding-top: 10px;
    }

    .forum-danger {
        border-color: #f2b8b5;
        color: #b42318;
        background: #fff5f5;
    }
</style>
