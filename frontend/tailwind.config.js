/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#0066CC',
          dark: '#0052A3',
          light: '#3385D6',
        },
      },
    },
  },
  plugins: [],
}

