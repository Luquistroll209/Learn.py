<script lang="ts">
    import "$lib/style/createClass.css"
    import type { PageLoad } from './$types';
    import { browser } from '$app/environment';
    import { error, redirect } from '@sveltejs/kit';
    import { onMount } from 'svelte';
    import { urlip } from '$lib/config';
    import { showAlert } from '$lib/store/alertStore.js';
    import Alert from '$lib/components/alert.svelte';

    let className = '';
    let classDescription = '';
    let selectedImage: File | null = null;
    let imagePreview = '';

    function handleImageSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files[0]) {
            selectedImage = target.files[0];
            
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview = e.target?.result as string;
            };
            reader.readAsDataURL(selectedImage);
        }
    }

    async function createClass(event: Event) {
        event.preventDefault();
        
        const token = localStorage.getItem('token');
        
        if (!className.trim()) {
            alert('El nombre de la clase es requerido');
            return;
        }
        
        const formData = new FormData();
        formData.append('name', className);
        formData.append('description', classDescription);
        
        if (selectedImage) {
            formData.append('imagen', selectedImage);
        }
        
        try {
            const response = await fetch(`${urlip}class/createClass/`, {
                method: 'POST',
                headers: {
                    'authorization': `${token}`
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showAlert("",'Clase creada exitosamente', "green");
                className = '';
                classDescription = '';
                selectedImage = null;
                imagePreview = '';
                window.location.href = '/clases';

                
                const fileInput = document.getElementById('classImage') as HTMLInputElement;
                if (fileInput) fileInput.value = '';
                
            } else {
                showAlert("Error", `${data.Error || 'No se pudo crear la clase'}`, "red");
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error al conectar con el servidor');
        }
    }

    function cancelCreation() {
        className = '';
        classDescription = '';
        selectedImage = null;
        imagePreview = '';
        const fileInput = document.getElementById('classImage') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
    }
</script>

<div class="contain">
    <div class="form-header">
        <h2>Nueva Clase</h2>
        <p>Comienza tu espacio de enseñanza</p>
    </div>
    
    <form on:submit={createClass}>
        <div class="form-group">
            <label for="className">Nombre de la Clase</label>
            <input 
                id="className" 
                placeholder="Introduce el nombre de la clase" 
                type="text" 
                bind:value={className}
                required
            >
        </div>
        
        <div class="form-group">
            <label for="classDescription">Descripción</label>
            <textarea 
                id="classDescription" 
                placeholder="Describe el propósito y contenido de esta clase..." 
                bind:value={classDescription}
                rows="4"
            ></textarea>
        </div>
        
        <div class="form-group">
            <label for="classImage">Imagen de Portada</label>
            <div class="image-upload-area" class:has-preview={imagePreview}>
                <input 
                    id="classImage" 
                    type="file" 
                    accept="image/*"
                    on:change={handleImageSelect}
                >
                <div class="upload-placeholder">
                    {#if imagePreview}
                        <img src={imagePreview} alt="Preview" class="image-preview">
                        <div class="change-image">Cambiar imagen</div>
                    {:else}
                        <div class="upload-icon">Subir imagen</div>
                        <div class="upload-text">Arrastra una imagen o haz clic para seleccionar</div>
                        <div class="upload-subtext">Recomendado: 1200x630px</div>
                    {/if}
                </div>
            </div>
        </div>
        
        <div class="form-actions">
            <button type="button" class="cancel-btn" on:click={cancelCreation}>Cancelar</button>
            <button class="send-btn" type="submit">Crear Clase</button>
        </div>
    </form>
</div>