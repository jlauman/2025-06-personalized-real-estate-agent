import json
import base64

from typing import Callable


def page_html(body: Callable):
    return f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>HomeMatch</title>
  </head>
  <body>
    {body()}
  </body>
</html>
"""


def main():
    homes = []
    with open("home_profiles.json", "r") as file:
        homes = json.load(file)

    def body():
        lines = []
        lines.append("<table>")
        for home in homes:
            with open(f"home_images/{home['record_uuid']}.jpg", "rb") as image:
              data_url = base64.b64encode(image.read()).decode("ascii")
            lines.append("<tr>")
            lines.append(f"""<td><img src="data:image/jpeg;base64,{data_url}" width="512"/></td>""")
            lines.append("<td>")
            lines.append(f"""<div>{home['home_description']}</div>""")
            lines.append(f"""<div>home ID: {home['record_uuid']}</div>""")
            lines.append(f"""<div>price: {home['price_us_dollars']}</div>""")
            lines.append(f"""<div>lot size: {home['lot_size_acres']}</div>""")
            lines.append(f"""<div>home size: {home['house_size_sq_ft']}</div>""")
            lines.append(f"""<div>bedrooms: {home['bedroom_count']}</div>""")
            lines.append(f"""<div>bathrooms: {home['bathroom_count']}</div>""")
            lines.append(f"""<div>neighborhood: {home['area_description']}</div>""")            
            lines.append("</td>")
            lines.append("</tr>")
        lines.append("</table>")
        return "".join(lines)

    html = page_html(body)
    with open("index.html", "w") as file:
        print(html, file=file)


if __name__ == "__main__":
    main()