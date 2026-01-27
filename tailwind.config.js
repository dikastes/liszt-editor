/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    //"./apps/**/*.html",
    //"./apps/**/*.js",
    "./apps/**/templates/**/*.html",
    "./apps/**/templates/**/*.js",
  ],
  safelist: [
    'text-primary-content',
    'items-center',
    'items-end',
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
    'toggle',
    'list',
    'list-row'
  ],
  theme: {
    extend: {
      minHeight: {
        'inherit': 'inherit',
      },
      fontFamily: {
        sans: ['BeausiteClassicWeb', 'ui-sans-serif', 'system-ui'],
        heading: ['MakeWayWeb', 'ui-sans-serif', 'system-ui'],
      }
    },
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
          // header background
          "base-100": "#f6f8f7",
          // graphics background
          "base-200": "#f9fcfd",
          // lines
          "base-300": "#c7c9c4",
          // version color
          "base-800": "#aaa"
        },
      },
    ],
  },
}
