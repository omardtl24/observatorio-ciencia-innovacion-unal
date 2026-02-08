/** @type {import('tailwindcss').Config} */

import colors from "./src/theme/colors.js";

export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        ancizar: ["AncizarSans"],
        ancizarItalic: ["AncizarSansItalic"],
      },
      colors: colors
    },
  },
  plugins: [],
};