from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request
from pydantic import ValidationError

from group_split.prompt import Groups, Introductions, split_groups


load_dotenv()

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route("/follow_up", methods=["GET"])
def follow_up():

    return render_template("follow_up.html")

@app.route('/group_split', methods=['GET', 'POST'])
def group_split():
    if request.method == 'GET':
        return render_template('group_split.html')
    else:
        try:
            data = request.get_json()
            intros = Introductions(**data["intros"])
        except ValidationError:
            abort(500, description="原因不明のエラーが発生しました。時間を空けて実行して下さい。")

        groups: Groups | None = split_groups(intros)
        if groups is None:
            abort(500, description="原因不明のエラーが発生しました。時間を空けて実行して下さい。")
        return jsonify(groups.model_dump())


if __name__ == '__main__':
    app.run(debug=True)