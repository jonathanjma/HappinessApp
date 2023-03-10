/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx,html}"],
  theme: {
    fontFamily: {
      custom: ['Roboto', 'Roboto']
    },
    extend: {
      colors: {
        buff: {
          50: "#fdfaed",
          100: "#f9efc8",
          200: "#f7eab6",
          300: "#f3de8a",
          400: "#efd56b",
          500: "#eccb46",
          600: "#eac534",
          700: "#deb617",
          800: "#b99813",
          900: "#947910",
        },
        raisin: {
          50: "#b6b6ce",
          100: "#9191b6",
          200: "#6c6c9d",
          300: "#5a5a87",
          400: "#414162",
          500: "#272838",
          600: "#212230",
          700: "#191a24",
          800: "#111118",
          900: "#08080c",
        },
        tangerine: {
          50: "#fcefed",
          100: "#f6d0ca",
          200: "#f1b1a7",
          300: "#eea196",
          400: "#eb9486",
          500: "#e88273",
          600: "#e26350",
          700: "#dd442c",
          800: "#c1351f",
          900: "#8c2717",
        },
        rhythm: {
          50: "#f4f4f6",
          100: "#d1d2db",
          200: "#babbc9",
          300: "#a4a4b7",
          400: "#8d8ea5",
          500: "#7e7f9a",
          600: "#767793",
          700: "#63647e",
          800: "#515267",
          900: "#3f3f50",
        },
        cultured: {
          50: "#f6f4f4",
          100: "#d9d3d3",
          200: "#c7bdbd",
          300: "#b4a7a7",
          400: "#a19191",
          500: "#8e7b7b",
          600: "#796767",
          700: "#635454",
          800: "#4D4242",
          900: "#372f2f",
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/container-queries"),
    require("@tailwindcss/line-clamp"),
  ],
  corePlugins: { preflight: false },
};
