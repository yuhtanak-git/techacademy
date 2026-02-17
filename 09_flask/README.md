# 動作確認

## 起動コマンド

```bash
# basic
$ python 09_flask/basic/app.py

# route
$ python 09_flask/route/app.py

# view
$ python 09_flask/view/app.py

# webform
$ python 09_flask/webform/app.py

# todo
$ python 09_flask/todo/app.py
```

---

## アクセス方法

サーバー起動後、ブラウザで以下にアクセスします。

### basic

http://127.0.0.1:5000

### route

http://127.0.0.1:5000  
http://127.0.0.1:5000/about  
http://127.0.0.1:5000/hello/Alice  
http://127.0.0.1:5000/user/123  
http://127.0.0.1:5000/search?query=flask

### view

http://127.0.0.1:5000/Alice  
http://127.0.0.1:5000/Bob

### webform

http://127.0.0.1:5000

### todo

http://127.0.0.1:5000

---

## 期待する結果

### basic

トップページに「Hello, Flask!!」と表示される。

### route

- `/` で「Hello, Flask!」が表示される。
- `/about` で「This is the about page.」が表示される。
- `/hello/Alice` で「Hello, Alice!」が表示される。
- `/user/123` で「User ID is 123」が表示される。
- `/search?query=flask` で「Search results for: flask」が表示される。

### view

- `/Alice` で「Welcome back, Alice!」が表示される。
- `/Bob` で「Hello, Bob!」が表示される。
- Items リスト（Apple / Banana / Cherry）が表示される。

### webform

- フォームが表示される。
- 名前とメールアドレスを入力して Submit を押すと、入力内容が表示される。
- 未入力の場合はエラーが表示される。

### todo

- TODOを入力して「追加」を押すとリストに表示される。
- 「削除」を押すと対象のTODOが削除される。
- アプリ再起動後もTODOが保持されている。
