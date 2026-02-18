from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

TODOS_FILE = "todos.txt"


def load_todos():
    """
    ファイルからTODOリストを読み込む関数

    :return: TODO のリスト
    """
    try:
        with open(TODOS_FILE, "r") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []


def save_todos(todos):
    """
    TODOリストをファイルに保存する関数

    :param todos: 保存する TODO リスト
    """
    with open(TODOS_FILE, "w") as file:
        file.write("\n".join(todos))


def redirect_to_index():
    """
    indexページへリダイレクトする共通関数
    """
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    """
    ルートページ。

    GET:
        TODO一覧を表示する。
    POST:
        フォームから送信されたTODOを追加して、ファイルへ保存後にリダイレクトする。
    """
    todos = load_todos()

    if request.method == "POST":
        new_todo = request.form.get("todo")
        if new_todo:
            todos.append(new_todo)
            save_todos(todos)
        return redirect_to_index()

    return render_template("index.html", todos=todos)


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    """
    指定されたIDのTODOを削除する。

    :param todo_id: 削除対象のTODOのインデックス
    """
    todos = load_todos()

    if 0 <= todo_id < len(todos):
        todos.pop(todo_id)
        save_todos(todos)

    return redirect_to_index()


if __name__ == "__main__":
    app.run(debug=True)
