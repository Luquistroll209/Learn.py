<script>
import { browser } from '$app/environment';
import { fly } from 'svelte/transition';
import '$lib/style/module/alert.css';
let alert = { title: '', description: '', color: 'gray', visible: false };

if (browser) {
  import('$lib/store/alertStore').then(module => {
    module.alertStore.subscribe(value => alert = value);
  });
}
</script>


<div
  class="AlertModule"
  style="border-left-color: {alert.color}; right: {alert.visible ? '60px' : '-500px'}"
>
  <h2>{alert.title}</h2>
  <p>{alert.description}</p>
</div>

