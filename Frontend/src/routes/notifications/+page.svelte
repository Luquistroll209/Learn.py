<script lang="ts">
    import "$lib/style/notificationsRedact.css"
    import type { PageLoad } from './$types';
    import { browser } from '$app/environment';
    import { error, redirect } from '@sveltejs/kit';
    import { onMount } from 'svelte';
    import { urlip } from '$lib/config';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';

    
    let notifications: any[] = [];
    let sentNotifications: any[] = [];
    let activeTab: 'received' | 'sent' = 'received';
    let showCompose = false;
    let composeSubject = '';
    let composeEmail = '';
    let composeMessage = '';


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

    async function handleAuthSubmit(event: Event): Promise<void> {
        event.preventDefault();
        const token = localStorage.getItem('token');

        const respose = await fetch(`${urlip}notification/createNotification/`, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
                body: JSON.stringify({
                    subject: composeSubject,
                    to: composeEmail,
                    message: composeMessage
                })
            });
            
            if (respose.ok){
                showAlert("", "mensaje enviado", "green");
                closeCompose();
            }else{
                showAlert("Error", "Usuario inexistente", "error");

            }
    }
    
    async function checkNotification(){
        const token = localStorage.getItem('token');
        const respose = await fetch(`${urlip}notification/obtainNotifications/`, {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
            });

            const data = await respose.json();
            notifications = data.notifications;
            if (respose.ok){
            }
    }
    
    function goNoti(id){
        window.location.href = `/notifications/noti-${id}`;
    }
    
    function switchTab(tab: 'received' | 'sent') {
        activeTab = tab;
    }
    
    function openCompose() {
        composeSubject = '';
        composeEmail = '';
        composeMessage = '';
        showCompose = true;
    }
    
    function closeCompose() {
        showCompose = false;
        composeSubject = '';
        composeEmail = '';
        composeMessage = '';
    }

</script>

<div class="redact-page-container">
    <div class="redact-containerAll">
        <div class="redact-noticontainer">
            <div class="redact-notifications-header">
                <h2>Notificaciones</h2>
                <button class="redact-compose-btn" on:click={openCompose}>
                    <svg width="20" height="20" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M3 3v18h18v-6h-2v4H5V5h4V3H3zm9 0v2h5.59L9 10.59l1.41 1.41L19 6.41V12h2V3h-7z"/>
                    </svg>
                    Redactar
                </button>
            </div>
            
            <div class="redact-tabs">
                <button 
                    class:redact-active={activeTab === 'received'} 
                    on:click={() => switchTab('received')}
                >
                    <svg width="18" height="18" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                    Recibidos
                    {#if notifications.length > 0}
                        <span class="redact-notification-badge">{notifications.length}</span>
                    {/if}
                </button>
                <button 
                    class:redact-active={activeTab === 'sent'} 
                    on:click={() => switchTab('sent')}
                >
                    <svg width="18" height="18" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                    Enviados
                </button>
            </div>
            
            <div class="redact-Noticontainer2">
                {#if activeTab === 'received'}
                    {#each notifications as notification (notification.id)}
                        {#if notification.notification_type === "received"}
                            <buton type="button" class="redact-notification-item" on:click={() => goNoti(notification.id)}>
                                <div class="redact-notification-select">
                                    <input type="checkbox">
                                </div>
                                <div class="redact-notification-content">
                                    <div class="redact-notification-header">
                                        <span class="redact-sender-name">{notification.created_by_info.username} {notification.created_by_info.last_name}</span>
                                        <span class="redact-notification-time">{notification.created_at}</span>
                                    </div>
                                    <div class="redact-notification-subject">{notification.subject}</div>
                                    <div class="redact-notification-preview">{notification.message.substring(0, 120)}{#if notification.message.length > 120}...{/if}</div>
                                    <div class="redact-notification-email">{notification.created_by_info.email}</div>
                                </div>
                            </buton>
                        {/if}
                    {:else}
                        <div class="redact-empty-state">
                            <svg width="64" height="64" viewBox="0 0 24 24">
                                <path fill="#dadce0" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                            </svg>
                            <p>No hay notificaciones recibidas</p>
                        </div>
                    {/each}
                {:else}
                    {#each notifications as notification (notification.id)}
                        {#if notification.notification_type === "sent"}
                            <buton type="button" class="redact-notification-item" on:click={() => goNoti(notification.id)}>
                                <div class="redact-notification-select">
                                    <input type="checkbox">
                                </div>
                                <div class="redact-notification-content">
                                    <div class="redact-notification-header">
                                        <span class="redact-sender-name">{notification.created_by_info.username} {notification.created_by_info.last_name}</span>
                                        <span class="redact-notification-time">{notification.created_at}</span>
                                    </div>
                                    <div class="redact-notification-subject">{notification.subject}</div>
                                    <div class="redact-notification-preview">{notification.message.substring(0, 120)}{#if notification.message.length > 120}...{/if}</div>
                                    <div class="redact-notification-email">{notification.created_by_info.email}</div>
                                </div>
                            </buton>
                        {/if}
                    {:else}
                        <div class="redact-empty-state">
                            <svg width="64" height="64" viewBox="0 0 24 24">
                                <path fill="#dadce0" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                            </svg>
                            <p>No hay notificaciones recibidas</p>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
        
        {#if showCompose}
            <div class="redact-compose-overlay" on:click={closeCompose}>
                <div class="redact-compose-window" on:click|stopPropagation>
                    <div class="redact-compose-header">
                        <h3>Nuevo Mensaje</h3>
                        <div class="redact-compose-actions">
                            <button class="redact-compose-close" on:click={closeCompose}>
                                <svg width="16" height="16" viewBox="0 0 24 24">
                                    <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <form on:submit|preventDefault={handleAuthSubmit}>
                        <div class="redact-compose-recipient">
                            <input 
                                bind:value={composeEmail}
                                placeholder="Para:" 
                                type="email" 
                                required
                            >
                        </div>
                        
                        <div class="redact-compose-subject">
                            <input 
                                bind:value={composeSubject}
                                placeholder="Asunto" 
                                type="text" 
                                required
                            >
                        </div>
                        
                        <div class="redact-compose-body">
                            <textarea 
                                bind:value={composeMessage}
                                placeholder="Escribe tu mensaje aquí..." 
                                required
                            ></textarea>
                        </div>
                        
                        <div class="redact-compose-footer">
                            <button type="submit" class="redact-send-btn">
                                <svg width="18" height="18" viewBox="0 0 24 24">
                                    <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                                Enviar
                            </button>
                            <button type="button" class="redact-compose-cancel" on:click={closeCompose}>
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        {/if}
    </div>
</div>