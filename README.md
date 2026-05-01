# LP Visualizer

Are you a visual learner? Want to understand linear programs but struggle to picture what's actually going on? LP Visualizer is for you.

Linear programs are the first thing you encounter when learning optimization — and for good reason.
They power real-world decisions like minimizing shipping costs, maximizing factory output, or balancing a diet.
But the textbook math can feel abstract.
This app makes it tangible: tweak a constraint, watch the line shift.
Move the objective, see the solution update instantly.
No prior knowledge required — just curiosity.

## Features

- **Live LP editor**:
  - [x] enter objective function coefficients and sense (`min` / `max`)
  - [x] add/remove constraints through a structured form
  - [x] the plot updates on every change
- **Feasible region**:
  - [ ] shaded semi-transparent polygon
  - [ ] with bold boundary segments
  - [ ] and vertex markers
- **Constraint lines**:
  - [x] drawn as infinite lines clipped to the plot bounds
  - [ ] rescale automatically as you zoom or pan
- **Objective vector**:
  - [x] fixed-length arrow showing the optimization direction
  - [ ] corner inset box
- **Optimal solution**:
  - [x] reports the optimal value as text below the plot
  - [x] detects and reports unbounded and infeasible problems
  - [ ] red marker placed at the optimal vertex
- **Per-constraint controls**:
  - [x] **Delete** (trash icon): permanently removes a constraint and updates the plot
  - [ ] **Toggle** (eye icon): disable a constraint without deleting it; disabled constraints shown as dashed lines and excluded from solving
- **Adaptive sign display**:
  - [ ] automatically show `−` instead of `+ −` when a coefficient is negative

## Usage

The interface is split into two panels:

- **Left panel: LP model**
  - Set the **objective sense** (`min` or `max`) using the dropdown at the top.
  - Enter `x` and `y` coefficients for the objective function.
  - For each constraint, fill in the `x` coefficient, `y` coefficient, sense (`≤`, `≥`, or `=`), and right-hand side value.
  - Click **Add Constraint** to append a new constraint row.
  - Use the **trash** button to delete a constraint. If only one constraint remains, deleting it resets it to the default trivial constraint `0x + 0y ≤ 0` instead of removing it entirely.

- **Right panel: plot**
  - Constraint lines are drawn as thin blue lines clipped to the plot bounds.
  - The objective vector is shown as a red arrow anchored at the origin.
  - The optimizaition result (optimal value and point, or infeasible/unbounded status) is displayed below the chart. It updates automatically whenever the model changes.

## React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

### React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

### Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

## License

This project is licensed under the [MIT License](LICENSE).

## Author

[Ivan Sergeev](https://github.com/Ivan-Sergeyev)
