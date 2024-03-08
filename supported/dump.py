import json

# this file is to generate the category file.
with open("dump.json", "r") as file:
    json_data = file.read()
    new_data = str(json_data).replace("\n", "").replace("  ", "")
    new_data = json.loads(new_data)

l = []
m=[]
for i in new_data:
    for j in i["pdpBreadcrumbs"]:
        if j["url"].count("/p/") > 0:
            pass
        else:
            if j["url"] not in l:
                l.append(j["url"])
                url = j["url"]
                url = url.split("/c/")
                m.append({"_id": url[1],
                          "name": url[0]})

with open("../category.json", "w") as file:
    file.write(str(m).replace("\'", "\""))
