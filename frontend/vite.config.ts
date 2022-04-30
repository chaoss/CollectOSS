// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from "url";

export default defineConfig({
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src/", import.meta.url)),
            "~": fileURLToPath(new URL("./node_modules/", import.meta.url)),
            'vue': '@vue/compat'
        }
    },
    server: {
        proxy: {
            "/api": "http://backend:5000/"
        }
    },
    preview: {
        proxy: {
            "/api": "http://backend:5000/"
        }
    }
    plugins: [
        vue({
            template: {
                compilerOptions: {
                    compatConfig: {
                        MODE: 2
                    }
                }
            }
        })
    ]
})
