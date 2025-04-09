/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['templates/bib/*.html', 'static/bib/*.js'],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('daisyui')
  ],
  daisyui: {
    themes: [
      {
        'liszt': {
          "primary": "#ff4208",
          "primary-content": "#fff",
          "secondary": "#f6f8f7",
          "accent": "#ff4208",
          "accent-content": "#fff",
          "neutral": "#5a6b75",
          "base-100": "#f9fcfd",
        }
      }
    ]
  }
}

