/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        jarvis: {
          50:  '#eef4ff',
          100: '#dbe7ff',
          200: '#bfd4ff',
          300: '#92b4ff',
          400: '#5e8aff',
          500: '#3865ff',
          600: '#1f47f4',
          700: '#1936da',
          800: '#192fa5',
          900: '#1a2c80',
          950: '#0e1547'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace']
      }
    }
  },
  plugins: []
};
