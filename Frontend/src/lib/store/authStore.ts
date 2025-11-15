
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export const isAuthenticated = writable(false);

if (browser) {
    const token = localStorage.getItem('token');
    isAuthenticated.set(!!token);
}