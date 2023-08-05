/** @type {import('tailwindcss').Config} */

const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    colors: {
      ...colors,
      'brand': { DEFAULT: '#E91E63', 50: '#F9C5D7', 100: '#F8B3CA', 200: '#F48DB0', 300: '#F06897', 400: '#ED437D', 500: '#E91E63', 600: '#BC124C', 700: '#890D38', 800: '#560823', 900: '#23030E', 950: '#0A0104' },
    },
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}
