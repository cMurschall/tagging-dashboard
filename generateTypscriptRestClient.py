import json
import os
import urllib

from uvicorn.importer import import_from_string

if __name__ == "__main__":

    # if openapi-generator-cli.jar is not present in the current directory, download it
    if not os.path.exists("openapi-generator-cli.jar"):
        print("Downloading openapi-generator-cli.jar")
        url = "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.10.0/openapi-generator-cli-7.10.0.jar"
        urllib.request.urlretrieve(url, "openapi-generator-cli.jar")

    app = import_from_string("app.main:app")
    openapi = app.openapi()
    version = openapi.get("openapi", "unknown version")

    print(f"writing openapi spec v{version}")
    with open("openapi.json", "w") as f:
        json.dump(openapi, f, indent=2)

    print("generating client")
    #  generate -i openapi.json -g typescript-fetch -o ./typescript-client
    os.system(
        "java -jar openapi-generator-cli.jar generate -i openapi.json -g typescript-fetch -o ./app.ui/services/restclient")
