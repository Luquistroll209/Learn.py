import { sveltekit } from '@sveltejs/kit/vite';
import { server } from 'typescript';
import { defineConfig } from 'vite';



export default defineConfig({
	
	plugins: [sveltekit()],
	server:{
		allowedHosts: true,
		proxy: {
		// Proxy para API
		'/api': {
			target: 'http://localhost:8000',
			changeOrigin: true,
		},
		// Proxy para archivos multimedia
		'/media': {
			target: 'http://localhost:8000',
			changeOrigin: true,
		}
		}
	}
});
