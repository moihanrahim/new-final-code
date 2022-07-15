from flask import Flask, request, abort
from algo_trading import algo

app = Flask(__name__)


@app.route('/')
def root():
    return 'online'



@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = eval(request.get_data(as_text=True))
        print(data)
        if data['entry']=="0":
            en = True
        else:
            en = False

        algo(option=data["option"], strategy=data["strategy"], quantity=data["quantity"],normal_order=en)
        return '', 200
    else:
        abort(400)


if __name__ == '__main__':
    # scheduler run
    app.run(host = "0.0.0.0", port = 80 )
