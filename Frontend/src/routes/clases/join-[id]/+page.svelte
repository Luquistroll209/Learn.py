<script lang="ts">
    import { onMount } from 'svelte';
    import type { PageLoad } from './$types';
    import { showAlert } from '$lib/store/alertStore.js';


    import "$lib/style/inClass.css"
    
    import { browser } from '$app/environment';
    import { urlip } from '$lib/config';
    
    //Variable y objetos para obtener la id
    import { page } from '$app/stores';
 
    let id;
    $: id = $page.params.id;


    let estaEnClase = false;
    
    let nombreClase = "";
    let nombreProfesor = "";
    let role = "";

    let date;
    
    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                //throw redirect(302, '/auth/login');
                window.location.href = '/auth/login';

            } else {
                join();
            }
        }
    });

    
    async function join(){
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('userData');
        /*
        if (userData) {
            const user = JSON.parse(userData);
            username = `${user.name}`;
        }  
        console.log(username);
        */
        const respose = await fetch(`${urlip}class/join/${id}/`, {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
            });

            const data = await respose.json();

            if (respose.ok){
                if (data.message === "Ya estás en esta clase"){
                    estaEnClase = true;
                } else{
                    estaEnClase = false;

                }
                date = data.unionDate.split("T")[0];
                if (data.role === "student"){
                    role = "Estudiante";
                } else if (data.role === "teacher"){
                    role = "profesor";
                } else {
                    role = data.role;
                }
                nombreClase = data.className
                nombreProfesor = data.teacherName
                
            
            }else{
            window.location.href = `/`;
                
                
            }

    }
    function llevarClase() {
        if (browser) {
            window.location.href = `../clases/clase-${id}`;
            
        }
    }
</script>

{#if !estaEnClase}
<div class="card" style="max-width: 500px; margin: 40px auto; text-align: center;">
    <div class="card-title" style="justify-content: center; margin-bottom: 8px;">
        <i class="fas fa-check-circle" style="color: var(--success-color); font-size: 24px; margin-right: 10px;"></i>
        <span>Confirmación de Inscripción</span>
    </div>
    
    <div style="padding: 20px;">
        <div style="margin-bottom: 20px;">
            <h3 style="color: var(--text-color); margin-bottom: 10px; font-size: 18px;">
                Te has unido exitosamente a la clase
            </h3>
            <p style="color: var(--text-light); font-size: 16px; margin-bottom: 8px;">
                <strong>{nombreClase}</strong>
            </p>
            <p style="color: var(--text-light); font-size: 14px;">
                <i class="fas fa-chalkboard-teacher" style="margin-right: 8px;"></i>
                {nombreProfesor}
            </p>
        </div>
        
        <div style="background-color: #f0f7ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="color: var(--text-light); font-size: 13px;">
                <i class="fas fa-id-card" style="margin-right: 8px;"></i>
                Tu rol en la clase: <strong>{role}</strong>
            </p>
            <p style="color: var(--text-light); font-size: 13px;">
                <i class="fas fa-calendar-alt" style="margin-right: 8px;"></i>
                {date}
            </p>
        </div>
        
        <button on:click={llevarClase()} class="action-button" style="margin-top: 10px;">
            <i class="fas fa-arrow-right" style="margin-right: 8px;"></i>
            Ir al aula virtual
        </button>
    </div>
</div>
{:else}
<div class="card" style="max-width: 500px; margin: 40px auto; text-align: center; border: 2px solid var(--error-color);">
    <div class="card-title" style="justify-content: center; margin-bottom: 8px; color: var(--error-color);">
        <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-right: 10px;"></i>
        <span>Advertencia</span>
    </div>
    
    <div style="padding: 20px;">
        <div style="margin-bottom: 20px;">
            <h3 style="color: var(--error-color); margin-bottom: 10px; font-size: 18px;">
                Ya estás inscrito en esta clase
            </h3>
            <p style="color: var(--text-light); font-size: 16px; margin-bottom: 8px;">
                <strong>{nombreClase}</strong>
            </p>
            <p style="color: var(--text-light); font-size: 14px;">
                <i class="fas fa-chalkboard-teacher" style="margin-right: 8px;"></i>
                {nombreProfesor}
            </p>
        </div>
        
        <div style="background-color: #ffebee; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="color: var(--text-color); margin-bottom: 8px; font-size: 14px;">
                <i class="fas fa-user-check" style="color: var(--error-color); margin-right: 8px;"></i>
                Tu inscripción fue confirmada el: <strong>{date}</strong>
            </p>
            <p style="color: var(--text-light); font-size: 13px;">
                <i class="fas fa-id-card" style="margin-right: 8px;"></i>
                Tu rol en la clase: <strong>{role}</strong>
            </p>
        </div>
        
        <div style="display: flex; gap: 10px; justify-content: center;">
            <button on:click={llevarClase} class="secondary-button">
                <i class="fas fa-external-link-alt" style="margin-right: 8px;"></i>
                Ver detalles
            </button>
        </div>
    </div>
</div>
{/if}