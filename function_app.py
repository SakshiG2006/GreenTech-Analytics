import azure.functions as func
from app import handle

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="", methods=["GET"])
def climate(req: func.HttpRequest) -> func.HttpResponse:
    result = handle(req.params.get("city"), dict(req.headers))
    return func.HttpResponse(body=result["body"], status_code=result["statusCode"],
                             headers=result["headers"], mimetype="application/json")
