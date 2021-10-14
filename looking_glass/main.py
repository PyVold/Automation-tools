from flask import Flask
from flask_restful import Api
import resources.bgp_class as BGP # import our defined resources files
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from apispec import APISpec

app = Flask(__name__)
api = Api(app)
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Looking glass',
        version='v1.0',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)


# our resources to be allowed in the looking glass, ex(BGP, ping, traceroute, etc..)
api.add_resource(BGP.BGP, '/bgp/<string:location>/<string:ipaddress>/<string:mask>')
docs.register(BGP.BGP)


if __name__ == '__main__':
    # debug mode has to be turned off in production, it's only for testing.
    app.run(debug=True)
