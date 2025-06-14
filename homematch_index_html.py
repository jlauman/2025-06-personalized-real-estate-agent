import json
import base64


def page_html(homes: list[dict], images: dict[str, str]):
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
    <table>
        <tbody>
        {''.join(home_html(home, images[home['record_uuid']]) for home in homes)}
        </tbody>
    </table>
  </body>
</html>
    """


def home_html(home: dict, data_url: str):
    return f"""
        <tr>
            <td><img src="{data_url}" width="512"/></td>
            <td>
                <table>
                    <tbody>
                        <tr><td>Best Feature: </td><td>{home['best_description']}</div></td></tr>
                        <tr><td>Home ID: </td><td>{home['record_uuid']}</div></td></tr>
                        <tr><td colspan="2"></td></tr>
                        <tr><td>Price: </td><td>${home['price_us_dollars']:,}</div></td></tr>
                        <tr><td>Lot Size: </td><td>{home['lot_size_acres']} acres</div></td></tr>
                        <tr><td>Home Size: </td><td>{home['house_size_sq_ft']:,} sq. ft.</div></td></tr>
                        <tr><td>Bedrooms: </td><td>{home['bedroom_count']}</div></td></tr>
                        <tr><td>Bathrooms: </td><td>{home['bathroom_count']}</div></td></tr>
                        <tr><td>Description: </td><td>{home['home_description']}</div></td></tr>
                        <tr><td>Neighborhood: </td><td>{home['area_description']}</div></td></tr>
                    </tbody>
                </table>
            </td>
        </tr>
    """


def get_data_urls(record_uuids: list[str]) -> dict:
    images = {}
    for record_uuid in record_uuids:
        with open(f"listing_images/{record_uuid}.jpg", "rb") as image:
            image_base64 = base64.b64encode(image.read()).decode("ascii")
        data_url = f"data:image/jpeg;base64,{image_base64}"
        images[record_uuid] = data_url
    return images


def main():
    homes = []
    with open("listings.json", "r") as file:
        homes = json.load(file)

    record_uuids = [x["record_uuid"] for x in homes]
    images = get_data_urls(record_uuids)

    html = page_html(homes, images)
    with open("index.html", "w") as file:
        print(html, file=file)


if __name__ == "__main__":
    main()
