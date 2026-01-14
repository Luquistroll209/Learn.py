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
			target: 'http://lt209.ddns.net:2001',
			changeOrigin: true,
		},
		// Proxy para archivos multimedia
		'/media': {
			target: 'http://lt209.ddns.net:2001',
			changeOrigin: true,
		}
		}
	}
});
