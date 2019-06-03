

def replace_image(user_data):
    for data in user_data:
        for header, info in data.items():
            if header == "image":
                data["image"] = "<img src=\"" + info + "\" alt= \"" + info + "\" />"
