import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

const production = !process.env.ROLLUP_WATCH;

export default {
  input: "src/main.ts",
  output: {
    file: "../custom_components/docker_marketplace/frontend/main.js",
    format: "es",
    sourcemap: !production,
  },
  plugins: [
    resolve(),
    typescript(),
    production && terser(),
  ],
};
