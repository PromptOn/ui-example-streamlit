import openapi_client


configuration = openapi_client.Configuration(host="http://localhost")

api_client = openapi_client.ApiClient(configuration)

api_instance = openapi_client.ServerStatusApi(api_client)

api_instance.get_status()

inferences = openapi_client.InferencesApi(api_client)

infReq = openapi_client
# inferences.new_inference()
