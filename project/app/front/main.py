from flask import Flask, render_template, request
import os

from .queries import _get_raw_data, _get_grouped_data


app = Flask(__name__)


@app.route("/")
def index():
    request_params = request.args.to_dict()

    hosts: dict = {}
    if request_params.get('view_type') == 'grouped':
        hosts = _get_grouped_data(request_params)
    else:
        hosts = _get_raw_data(request_params)

    return render_template("index.html", hosts=hosts, request_params=request_params)


if __name__ == "__main__":
    port = os.environ.get("FRONT_PORT")
    app.run(debug=True, host="0.0.0.0", port=port)
