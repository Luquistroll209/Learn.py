<script lang="ts">
    import "$lib/style/clasesCards.css"
    import type { PageLoad } from './$types';
    import { browser } from '$app/environment';
    import { redirect } from '@sveltejs/kit';
    import { onMount } from 'svelte';

    let clases = [
        { nombre: "Matemáticas", profesor: "Juan Pérez", imagen: "https://ichef.bbci.co.uk/ace/ws/640/cpsprodpb/164EE/production/_109347319_gettyimages-611195980.jpg.webp" },
        { nombre: "Historia", profesor: "Ana Gómez", imagen: "https://i.blogs.es/a5c044/luthero/450_1000.jpg" },
        { nombre: "Programación", profesor: "Lucas Torres", imagen: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJmuyls7qbjekEs2p4BEA_i6sgNhsRCi4xxg&s" },
        { nombre: "Física", profesor: "Carla Ruiz", imagen: "https://images3.memedroid.com/images/UPLOADED372/66b8e9b940b6a.jpeg" }
    ];

    let desplegado: number | null = null;

    function toggleMenu(index: number) {
        desplegado = desplegado === index ? null : index;
    }

    function abandonarClase(nombre: string) {
        alert(`Has elegido abandonar la clase "${nombre}"`);
        desplegado = null;
    }

    function verTareas(nombre: string) {
        alert(`Ver tareas de "${nombre}"`);
    }

    function abrirForo(nombre: string) {
        alert(`Abrir foro de "${nombre}"`);
    }

    function materiales(nombre: string) {
        alert(`Ver materiales de "${nombre}"`);
    }
    onMount(() => {
        if (browser) {
            const token = localStorage.getItem('token');
            if (!token) {
                //throw redirect(302, '/auth/login');
                window.location.href = '/auth/login';

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
</script>

<div class="clases-grid">
  <h2>Las clases aun no estan conectadas a la base de datos</h2>
  {#each clases as clase, i}
    <div class="clase-card">
      <div class="clase-img-container">
        <img src={clase.imagen} alt={clase.nombre} class="clase-img" />
        <button class="clase-options" on:click={() => toggleMenu(i)}>⋮</button>
        {#if desplegado === i}
          <div class="menu">
            <button on:click={() => abandonarClase(clase.nombre)}>Abandonar clase</button>
          </div>
        {/if}
      </div>
      <div class="clase-info">
        <h3>{clase.nombre}</h3>
        <p>Profesor: {clase.profesor}</p>
      </div>
      <div class="clase-buttons">
        <button on:click={() => verTareas(clase.nombre)}>Tareas</button>
        <button on:click={() => abrirForo(clase.nombre)}>Foro</button>
        <button on:click={() => materiales(clase.nombre)}>Materiales</button>
      </div>
    </div>
  {/each}
</div>