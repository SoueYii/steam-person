/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#f8f9fb',
        border: '#e8ecf0',
        accent: '#059669',
        'accent-light': 'rgba(5, 150, 105, 0.08)',
      },
    },
  },
  plugins: [],
}
