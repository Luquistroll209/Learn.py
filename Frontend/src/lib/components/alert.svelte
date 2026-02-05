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
  class:visible={alert.visible}
  style="border-left-color: {alert.color};"
>
  <h2>{alert.title}</h2>
  <p>{alert.description}</p>
</div>

