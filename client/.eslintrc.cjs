module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    "plugin:prettier/recommended"
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs','build','node_modules'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh','import'],
  rules: {
    "no-console": [
      "error",
      {
        "allow": ["error","warn","info"]
      }
    ],
    "@typescript-eslint/no-unused-vars": ["error"],
    "no-use-before-define": "warn",
    "react-hooks/exhaustive-deps": "error",
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    "import/order": [
      2,
      {
        "groups": ["builtin", "external", "internal", ["parent", "sibling", "index"]],
        "newlines-between": "always"
      }
    ],
  },
}
