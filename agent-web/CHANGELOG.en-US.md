# Changelog

## [0.1.0] - 2026-01-13

### Optimization

#### Dependency Cleanup

Removed unused redundant dependencies to reduce bundle size and improve build speed.

**Removed dependencies (14):**

| Package                   | Version | Reason                                    |
| ------------------------- | ------- | ----------------------------------------- |
| `array-move`              | 4.0.0   | Unused                                    |
| `buffer`                  | ^6.0.3  | Replaced by @rsbuild/plugin-node-polyfill |
| `codemirror`              | ^6.0.1  | Project uses Monaco Editor                |
| `events`                  | 3.3.0   | Replaced by @rsbuild/plugin-node-polyfill |
| `immer`                   | ^10.1.1 | Project uses mobx for state management    |
| `markdown-it`             | 14.0.0  | Already bundled in md-editor-rt           |
| `numeral`                 | 2.0.6   | Unused                                    |
| `prettier`                | 3.5.3   | Kept only in devDependencies              |
| `react-sortable-hoc`      | 2.0.0   | Project uses @dnd-kit for drag and drop   |
| `react-use`               | 17.6.0  | Unused                                    |
| `redoc`                   | 2.5.0   | Unused                                    |
| `stream`                  | 0.0.2   | Replaced by @rsbuild/plugin-node-polyfill |
| `use-deep-compare-effect` | 1.8.1   | Unused                                    |
| `uuid`                    | 11.1.0  | Unused                                    |
| `zustand`                 | 4.5.5   | Project uses mobx for state management    |

**Removed devDependencies (4):**

| Package              | Version  | Reason              |
| -------------------- | -------- | ------------------- |
| `@types/codemirror`  | ^5.60.15 | codemirror removed  |
| `@types/events`      | ^3.0.3   | events removed      |
| `@types/markdown-it` | 14.1.1   | markdown-it removed |

**Added devDependencies (1):**

| Package                         | Version | Description                                                |
| ------------------------------- | ------- | ---------------------------------------------------------- |
| `@rsbuild/plugin-node-polyfill` | ^1.4.2  | Auto-handles Node.js built-in module polyfills for browser |

### Impact

- Removed 15+ unused dependencies
- Reduced node_modules size
- Adopted official polyfill solution instead of manually installed Node.js polyfill packages
