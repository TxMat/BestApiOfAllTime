/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/**/*.{js,jsx,ts,tsx}",], theme: {
        extend: {},
    }, plugins: [require("daisyui"), require('tailwind-scrollbar')],
    variants: {
        scrollbar: ["rounded"]
    }, daisyui: {
        themes: [{
            dark: {
                ...require("daisyui/src/colors/themes")["[data-theme=dark]"],
                "base-100": "#374151",
                "success": "#34d399",
                "error": "#fb7185",
                "info": "#38bdf8",
                "warning": "#fb923c",
                "accent": "#8B85C1"
                // "neutral": "#c3baba",
            }, light: {
                ...require("daisyui/src/colors/themes")["[data-theme=light]"],
                "base-100": "#d1d5db",
                "success": "#34d399",
                "error": "#fb7185",
                "info": "#38bdf8",
                "warning": "#fb923c",
                "accent": "#8B85C1"
                // "neutral": "#c3baba",
            }
        }]
    }
}

