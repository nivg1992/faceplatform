// @ts-check

import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.js", "src/**/*.tsx"],
  }
);

// export default [
//     js.configs.recommended,
//     {
//         files: ["src/**/*.js", "src/**/*.tsx"],
//         rules: {
//             'no-console': [
//               'error',
//               {
//                 allow: ['error', 'warn', 'info']
//               }
//             ],
//             '@typescript-eslint/no-unused-vars': ['error'],
//             'no-use-before-define': 'warn',
//             'react-hooks/exhaustive-deps': 'error',
//             'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
//             'import/order': [
//               2,
//               {
//                 groups: ['builtin', 'external', 'internal', ['parent', 'sibling', 'index']],
//                 'newlines-between': 'always'
//               }
//             ]
//           }
//     }
// ];