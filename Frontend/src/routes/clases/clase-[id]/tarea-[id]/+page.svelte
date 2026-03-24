<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';

    let id: string = '';

    $: id = $page.params.id;

    onMount(() => {
        console.log('ID:', id);
    });
    
</script>

<div>
    
</div>