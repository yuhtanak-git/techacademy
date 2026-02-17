# techacademy_yuhtanak

LLMアプリ開発コースの成果物管理リポジトリ

---

## 整形

### Python（black / ruff）

| 種類     | 内容                      | コマンド                   |
| -------- | ------------------------- | -------------------------- |
| 準備     | black / ruff インストール | `$ pip install black ruff` |
| 整形     | black によるフォーマット  | `$ black .`                |
| チェック | ruff によるLintチェック   | `$ ruff check .`           |
| 自動修正 | ruff による自動修正       | `$ ruff check . --fix`     |

---

### HTML / CSS / JS）

| 種類        | 内容                        | コマンド             |
| ----------- | --------------------------- | -------------------- |
| 準備        | 依存関係のインストール      | `$ npm install`      |
| 整形        | prettier によるフォーマット | `$ npm run format`   |
| JSチェック  | eslint（チェック）          | `$ npm run lint:js`  |
| CSSチェック | stylelint（チェック）       | `$ npm run lint:css` |
| まとめて    | JS/CSS をまとめてチェック   | `npm run lint`       |

---

## pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```
