
import { writable } from 'svelte/store';

export const alertStore = writable({
  title: '',
  description: '',
  color: 'gray',
  visible: false
});

export function showAlert(title, description, color = 'gray') {
  alertStore.set({ title, description, color, visible: true });
  setTimeout(() => {
    alertStore.update(a => ({ ...a, visible: false }));
  }, 10000);
}
