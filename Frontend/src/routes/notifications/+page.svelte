<script lang="ts">
    import "$lib/style/notificationsRedact.css"
    import type { PageLoad } from './$types';
    import { browser } from '$app/environment';
    import { error, redirect } from '@sveltejs/kit';
    import { onMount } from 'svelte';
    import { urlip } from '$lib/config';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';

    async function handleAuthSubmit(event: Event): Promise<void> {
        const token = localStorage.getItem('token');

        const form = event.target as HTMLFormElement;

        const subject = (form.querySelector('#subject') as HTMLInputElement).value;
        const email = (form.querySelector('#email') as HTMLInputElement).value;
        const message = (form.querySelector('#message') as HTMLInputElement).value;


        const respose = await fetch(`${urlip}notification/createNotification/`, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
                body: JSON.stringify({
                    subject: subject,
                    to: email,
                    message: message
                })
            });

            //const data = await respose.json();

            
            if (respose.ok){
                //showAlert("Correcto", "Mensaje enviado", "blue");
                alert("correcto");
                
            }else{
                //showAlert("Error", "Error", "red");
                alert("error");
            }
    }

</script>

<div class="contain">
    <div class="form-header">
        <h2>Enviar Notificación</h2>
        <p>Crea y envía notificaciones por correo electrónico</p>
    </div>
    
    <form on:submit={handleAuthSubmit}>
        <div class="form-group">
            <label for="email">Destinatario</label>
            <input id="email" placeholder="ejemplo@dominio.com" type="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="subject">Asunto</label>
            <input id="subject" placeholder="Asunto del mensaje" type="text" name="subject" required>
        </div>
        
        <div class="form-group">
            <label for="message">Mensaje</label>
            <textarea id="message" name="message" placeholder="Escribe tu mensaje aquí..." required></textarea>
            <div class="char-counter">
                <span id="char-count">0</span> caracteres
            </div>
        </div>
        
        <div class="form-actions">
            <button type="button" class="cancel-btn">Cancelar</button>
            <button class="send-btn" type="submit">Enviar Email</button>
        </div>
    </form>
</div>