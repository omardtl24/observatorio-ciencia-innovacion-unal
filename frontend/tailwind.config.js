/** @type {import('tailwindcss').Config} */

import colors from "./src/theme/colors.js";

export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Ancizar Sans"],
        serif: ["Ancizar Serif"],
      },
      colors: colors
    },
  },
  plugins: [],
};