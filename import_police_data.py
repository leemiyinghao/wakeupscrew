from MediaWarehouse import MediaWarehouse
import json
import os

if __name__ == "__main__":
    with open("polices.json") as file:
        datas = json.load(file)
        for data in datas:
            img = None
            path = ""
            if os.path.exists("polices/{}.jpg".format(data["name"])):
                path = "polices/{}.jpg".format(data["name"])
            else:
                path = "polices/default.jpg"
            with open(path, "rb") as imgfile:
                img = imgfile.read()
            media = MediaWarehouse.create(
                sourceType="POLICEDEP",
                mainDescription=data["name"],
                data=img,
                thumbnail=img,
                tags=['policedepartment', data["name"]],
                extension='jpg',
                additionalData=json.dumps({"link": data["link"]})
            )
