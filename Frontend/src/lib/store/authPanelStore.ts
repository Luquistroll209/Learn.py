
import { writable } from 'svelte/store';
export const authPanelTrigger = writable<'login' | 'register' | null>(null);
