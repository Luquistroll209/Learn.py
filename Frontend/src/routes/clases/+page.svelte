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

<a href="clases/createClass/">Crear una clase</a>
<div class="clases-grid">
  {#each clases as clase, i}
    <div class="clase-card">
      <div class="clase-img-container">
        <img src={clase.imagen} alt={clase.name} class="clase-img" />
        <button class="clase-options" on:click={() => toggleMenu(i)}>⋮</button>
        {#if desplegado === i}
          <div class="menu">
            <button on:click={() => abandonarClase(clase.name)}>Abandonar clase</button>
          </div>
        {/if}
      </div>
      <div class="clase-info">
        <h3>{clase.name}</h3>
        <p>Profesor: {clase.teacher}</p>
      </div>
      <div class="clase-buttons">
        <button on:click={() => verTareas(clase.name)}>Tareas</button>
        <button on:click={() => abrirForo(clase.name)}>Foro</button>
        <button on:click={() => materiales(clase.name)}>Materiales</button>
      </div>
    </div>
  {/each}
</div>