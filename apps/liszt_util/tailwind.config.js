/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/*.html",
    "./**/*.js",
    "../../**/templates/**/*.html",
    "../../**/templates/**/*.js",
  ],
  safelist: [
    'items-center',
    'form-control',
    'label',
    'label-text',
    'mb-10',
    'input',
    'input-bordered',
    'flex',
    'gap-2',
    'my-5',
    'flex-1',
    'flex-rows',
    'w-full',
    'gap-10',
    'grow',
    'autocomplete-select',
    'select',
    'select-bordered',
    'flex-0',
    'checkbox',
    'textarea',
    'textarea-bordered',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        liszt: {
          "primary": "#ff4208",
          "primary-content": "#fff",
          "secondary": "#f6f8f7",
          "accent": "#ff4208",
          "accent-content": "#fff",
          "neutral": "#5a6b75",
          "base-100": "#f9fcfd",
        },
      },
    ],
  },
}