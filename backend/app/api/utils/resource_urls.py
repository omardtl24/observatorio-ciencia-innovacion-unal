from flask import current_app


def build_resource_url(file) -> str:
    #TODO: It receives a file. It saves it in the resources shared folder and returns the URL to access it.
    return f"{current_app.config['RESOURCES_BASE_URL']}/{file}"

def delete_resource_file(file_path) -> None:
    #TODO: Deletes a file from the resources shared folder given its path.
    return
