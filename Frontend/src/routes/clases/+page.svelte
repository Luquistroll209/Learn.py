<script lang="ts">
    import "$lib/style/clasesCards.css"
    import type { PageLoad } from './$types';
    import { browser } from '$app/environment';
    import { redirect } from '@sveltejs/kit';
    import { onMount } from 'svelte';
    import { urlip } from '$lib/config';
    let clases: any[] = [];
  /*
    let clases = [
        { name: "Matemáticas", teacher: "Juan Pérez", imagen: "https://ichef.bbci.co.uk/ace/ws/640/cpsprodpb/164EE/production/_109347319_gettyimages-611195980.jpg.webp" },
        { name: "Historia", profesor: "Ana Gómez", imagen: "https://i.blogs.es/a5c044/luthero/450_1000.jpg" },
        { name: "Programación", teacher: "Lucas Torres", imagen: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJmuyls7qbjekEs2p4BEA_i6sgNhsRCi4xxg&s" },
        { name: "Física", teacher: "Carla Ruiz", imagen: "https://images3.memedroid.com/images/UPLOADED372/66b8e9b940b6a.jpeg" }
    ];
*/
    let desplegado: number | null = null;

    function toggleMenu(index: number) {
        desplegado = desplegado === index ? null : index;
        
    }

    function abandonarClase(name: string) {
        alert(`Has elegido abandonar la clase "${name}"`);
        desplegado = null;
    }

    function verTareas(name: string) {
        alert(`Ver tareas de "${name}"`);
    }

    function abrirForo(name: string) {
        alert(`Abrir foro de "${name}"`);
    }

    function materiales(name: string) {
        alert(`Ver materiales de "${name}"`);
    }
    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                //throw redirect(302, '/auth/login');
                window.location.href = '/auth/login';

            } else {
              loadClass();
            }
        }
    });
    export const load: PageLoad = async () => {
      //alert("a");
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                throw redirect(302, '/auth/login');
            }
        }
        return {};
    };
    async function loadClass(){
        const token = localStorage.getItem('token');
        
        const respose = await fetch(`${urlip}class/obtainClass/`, {
                method: 'get',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'authorization': `${token}`
                },
            });

            const data = await respose.json();

            if (respose.ok){
              console.log(data);
              
              clases = data.clases || [];
              
            }/*else{
                showAlert("Error", "Error", "red");
            }*/
    }
</script>

<div class="header-container">
    <a href="clases/createClass/" class="create-class-btn">+ Crear una clase</a>
</div>

<div class="clases-grid">
  {#each clases as clase, i}
    <div class="clase-card">
      <div class="clase-img-container">
        <a href="clases/clase-{clase.id}" class="clase-link-overlay">
          <img src={clase.imagen_url} alt={clase.name} class="clase-img" />
          
          <div class="clase-header-overlay">
            <h3 class="clase-title">{clase.name}</h3>
            <p class="clase-section">Sección placeholder</p>
            <p class="clase-teacher">{clase.teacher}</p>
          </div>
        </a>
        <button class="clase-options" on:click|stopPropagation={() => toggleMenu(i)}>⋮</button>
        {#if desplegado === i}
          <div class="menu">
            <button on:click|stopPropagation={() => abandonarClase(clase.name)}>Abandonar clase</button>
            <button on:click|stopPropagation={() => abandonarClase(clase.name)}>Configurar</button>
            <button on:click|stopPropagation={() => abandonarClase(clase.name)}>Invitar</button>
          </div>
        {/if}
      </div>
      
      <div class="clase-footer">
        <button class="footer-icon-btn" on:click|stopPropagation={() => verTareas(clase.name)} title="Próximas tareas">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        </button>
        <button class="footer-icon-btn" on:click|stopPropagation={() => abrirForo(clase.name)} title="Carpeta de clase">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
          </svg>
        </button>
      </div>
    </div>
  {/each}
</div>