from flask import Flask, request


def build_app(default_name: str) -> Flask:
    app = Flask('hello')

    @app.route('/')
    def hello():
        name = request.args.get('name', default_name)
        return f'Hello, {name}!'

    @app.route('/health')
    def health():
        return 'OK'

    return app
