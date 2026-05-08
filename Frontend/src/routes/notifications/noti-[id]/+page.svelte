<script lang="ts">
    import "$lib/style/notificationsRedact.css";
    import { fetchWithRateLimit } from "$lib/utils/fetchWithRateLimit";

    import { browser } from "$app/environment";
    import { onMount } from "svelte";
    import { urlip } from "$lib/config";
    import { page } from "$app/stores";

    let notifications: any[] = [];
    let selectedNotification: any = null;
    let loading = false;
    let is404 = true;

    // Datos de invitación
    let isInvitation = false;
    let classId: string | null = null;
    let className: string | null = null;
    let professorName: string | null = null;

    let id: any = null;
    $: id = $page.params.id;

    onMount(() => {
        if (browser) {
            const token = localStorage.getItem("token");
            if (!token) {
                window.location.href = "/auth/login";
            } else {
                checkNotification();
            }
        }
    });

    async function checkNotification() {
        const token = localStorage.getItem("token");
        const response = await fetchWithRateLimit(
            `${urlip}notification/obtainNotifications/${id}`,
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
            selectedNotification = data;
            loading = false;
            is404 = false;
            processInvitationMessage(selectedNotification.message);
        }
    }

    function processInvitationMessage(message: string) {
        // Detectar si contiene "invitado a unirte a la clase"
        const invitationPattern = /invitado a unirte a la clase "([^"]+)"/i;
        const matchInvitation = message.match(invitationPattern);
        if (matchInvitation) {
            isInvitation = true;
            className = matchInvitation[1];

            // Extraer ID de clase
            const idPattern = /ID de la clase:\s*([A-Za-z0-9]+)/;
            const idMatch = message.match(idPattern);
            if (idMatch) classId = idMatch[1];

            // Extraer nombre del profesor: después de "Profesor:" hasta fin de línea
            const profPattern = /Profesor:\s*(.+?)(?:\n|$)/;
            const profMatch = message.match(profPattern);
            if (profMatch) professorName = profMatch[1].trim();
        }
    }

    function goBack() {
        window.history.back();
    }
</script>

<div class="redact-page-container">
    {#if loading}
        <div class="redact-noticontainer">
            <div class="redact-notifications-header">
                <h2>Cargando...</h2>
            </div>
            <div class="redact-loading-state">Cargando notificaciones...</div>
        </div>
    {:else if is404}
        <div class="redact-noticontainer">
            <div class="redact-notifications-header">
                <h2>Notificación</h2>
                <button
                    class="redact-compose-btn redact-back-btn"
                    on:click={goBack}
                >
                    ← Volver
                </button>
            </div>
            <div class="redact-empty-state">
                <p>404 notificacion no encontrada</p>
            </div>
        </div>
    {:else if selectedNotification}
        <div class="redact-noticontainer">
            <div class="redact-notifications-header">
                <h2>Notificación</h2>
                <button
                    class="redact-compose-btn redact-back-btn"
                    on:click={goBack}
                >
                    ← Volver
                </button>
            </div>

            <div class="redact-notification-detail">
                <!-- Cabecera (título, fechas, estado) -->
                <div class="redact-detail-header">
                    <div class="redact-detail-title-row">
                        <h3 class="redact-detail-title">
                            {selectedNotification.subject}
                        </h3>
                        <span class="redact-notification-time">
                            {new Date(
                                selectedNotification.created_at,
                            ).toLocaleDateString()}
                            {new Date(
                                selectedNotification.created_at,
                            ).toLocaleTimeString()}
                        </span>
                    </div>
                    <div class="redact-detail-status">
                        <div
                            class="redact-status-indicator {selectedNotification.is_read
                                ? 'read'
                                : 'unread'}"
                        ></div>
                        <span class="redact-status-text"
                            >{selectedNotification.is_read
                                ? "Leída"
                                : "No leída"}</span
                        >
                    </div>
                </div>

                <!-- Remitente -->
                <div class="redact-detail-section">
                    <h4 class="redact-section-title">De:</h4>
                    <div class="redact-user-card">
                        <div class="redact-user-avatar redact-sender-avatar">
                            {selectedNotification.created_by_info?.username?.charAt(
                                0,
                            ) || "U"}
                        </div>
                        <div class="redact-user-info">
                            <div class="redact-user-name">
                                {selectedNotification.created_by_info
                                    ?.username || "Usuario"}
                            </div>
                            <div class="redact-user-email">
                                {selectedNotification.created_by_info?.email ||
                                    "No especificado"}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Destinatario -->
                <div class="redact-detail-section">
                    <h4 class="redact-section-title">Para:</h4>
                    <div class="redact-user-card">
                        <div class="redact-user-avatar redact-receiver-avatar">
                            {selectedNotification.to_info?.username?.charAt(
                                0,
                            ) || "U"}
                        </div>
                        <div class="redact-user-info">
                            <div class="redact-user-name">
                                {selectedNotification.to_info?.username ||
                                    "Usuario"}
                            </div>
                            <div class="redact-user-email">
                                {selectedNotification.to_info?.email ||
                                    "No especificado"}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- CUERPO: Si es invitación mostramos tarjeta especial, si no, mensaje normal -->
                {#if isInvitation && classId && className}
                    <div class="redact-invitation-card">
                        <div class="redact-invitation-icon">📩</div>
                        <div class="redact-invitation-text">
                            <span class="redact-invitation-professor"
                                >{professorName || "El profesor"}</span
                            >
                            te ha invitado a la clase
                        </div>
                        <div class="redact-invitation-class-name">
                            "{className}"
                        </div>
                        <div class="redact-invitation-id">ID: {classId}</div>
                        <a
                            href={`/clases/join-${classId}`}
                            class="redact-invitation-button"
                        >
                            Aceptar invitación →
                        </a>
                    </div>
                {:else}
                    <!-- Mensaje normal (no invitación) -->
                    <div class="redact-detail-section">
                        <h4 class="redact-section-title">Mensaje:</h4>
                        <div class="redact-message-container">
                            <p
                                class="redact-message-content"
                                style="white-space: pre-wrap;"
                            >
                                {selectedNotification.message}
                            </p>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>
