<script lang="ts">
    import "$lib/style/notificationsRedact.css"
    import { browser } from '$app/environment';
    import { onMount } from 'svelte';
    import { urlip } from '$lib/config';

    let notifications: any[] = [];
    let selectedNotification: any = null;
    let loading = false;
    let is404 = true; 

    //variables y objetos para obtener la ID
    import { page } from '$app/stores';
    let id;
    $: id = $page.params.id;

    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = '/auth/login';
            } else {
                checkNotification();
            }
        }
    });
    
    async function checkNotification(){
        const token = localStorage.getItem('token');
        
        const response = await fetch(`${urlip}notification/obtainNotifications/${id}`, {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'authorization': `${token}`
            },
        });
        const data = await response.json();
        if (response.ok){
            selectedNotification = data;
            console.log(selectedNotification);
            loading = false;
            is404 = false;
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
            <div class="redact-loading-state">
                Cargando notificaciones...
            </div>
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
                <div class="redact-detail-header">
                    <div class="redact-detail-title-row">
                        <h3 class="redact-detail-title">
                            {selectedNotification.subject}
                        </h3>
                        <span class="redact-notification-time">
                            {new Date(selectedNotification.created_at).toLocaleDateString()} 
                            {new Date(selectedNotification.created_at).toLocaleTimeString()}
                        </span>
                    </div>
                    
                    <div class="redact-detail-status">
                        <div class="redact-status-indicator {selectedNotification.is_read ? 'read' : 'unread'}"></div>
                        <span class="redact-status-text">
                            {selectedNotification.is_read ? 'Leída' : 'No leída'}
                        </span>
                    </div>
                </div>
                
                <!-- Remitente -->
                <div class="redact-detail-section">
                    <h4 class="redact-section-title">De:</h4>
                    <div class="redact-user-card">
                        <div class="redact-user-avatar redact-sender-avatar">
                            {selectedNotification.created_by_info?.username?.charAt(0) || 'U'}
                        </div>
                        <div class="redact-user-info">
                            <div class="redact-user-name">
                                {selectedNotification.created_by_info?.username || 'Usuario'}
                            </div>
                            <div class="redact-user-email">
                                {selectedNotification.created_by_info?.email || 'No especificado'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="redact-detail-section">
                    <h4 class="redact-section-title">Para:</h4>
                    <div class="redact-user-card">
                        <div class="redact-user-avatar redact-receiver-avatar">
                            {selectedNotification.to_info?.username?.charAt(0) || 'U'}
                        </div>
                        <div class="redact-user-info">
                            <div class="redact-user-name">
                                {selectedNotification.to_info?.username || 'Usuario'}
                            </div>
                            <div class="redact-user-email">
                                {selectedNotification.to_info?.email || 'No especificado'}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="redact-detail-section">
                    <h4 class="redact-section-title">Mensaje:</h4>
                    <div class="redact-message-container">
                        <p class="redact-message-content">
                            {selectedNotification.message}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>