import js from '@eslint/js';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js'],
    ignores: ['node_modules/**', 'dist/**', 'build/**'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      // 学習用にうるさすぎるのを抑えるならここで調整
      // "no-unused-vars": "warn",
    },
  },
];
