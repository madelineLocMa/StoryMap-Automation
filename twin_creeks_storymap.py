
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.apps.storymap import StoryMap, Sidecar, Slide, Text, WebMap as SMWebMap, Button
from arcgis.features import FeatureLayerCollection

# 1. Authenticate GIS Session
gis = GIS("https://www.arcgis.com", "your_username", "your_password")  # ← Replace with your credentials

# 2. Create and Share Web Maps
def create_and_share_webmap(layer_url, title, description, tags):
    flc = FeatureLayerCollection(layer_url, gis)
    web_map = WebMap()
    web_map.add_layer(flc.layers[0], {"title": title})

    popup = {
        "title": title,
        "content": "{TRACT_NAME}: {AGE_55PLUS} residents age 55+"  # Replace field names
    }
    web_map.definition['operationalLayers'][0]['popupInfo'] = popup

    item = web_map.save({
        "title": title,
        "snippet": description,
        "tags": tags,
        "description": description,
        "folder": "TwinCreeks"
    })
    item.share(everyone=True)
    return item.id

# Replace with real URLs to your hosted feature layers
layer_url_demo = "https://services.arcgis.com/.../Age55PlusLayer/FeatureServer/0"
layer_url_walk = "https://services.arcgis.com/.../WalkBufferLayer/FeatureServer/0"
layer_url_market = "https://services.arcgis.com/.../MarketGrowthLayer/FeatureServer/0"

map_demo_id = create_and_share_webmap(layer_url_demo, "Twin Creeks – Age 55+", "Density of residents age 55+ in the DFW area", ["TwinCreeks", "Demographics"])
map_walk_id = create_and_share_webmap(layer_url_walk, "Twin Creeks – Walkability", "Walkable POIs within 15 minutes", ["TwinCreeks", "Access"])
map_market_id = create_and_share_webmap(layer_url_market, "Twin Creeks – Market Strength", "Household income and projected growth", ["TwinCreeks", "Market"])

# 3. Create StoryMap Object
story = StoryMap(gis=gis)
story.title = "Twin Creeks Active Adult – Investing in the Future of Senior Living"
story.subtitle = "A wellness-centered senior living community in Allen, Texas."

story.cover = {
    "title": story.title,
    "subtitle": story.subtitle,
    "image": {
        "source": "https://your-hosted-image-url.com/twincreeks_cover.jpg"  # Replace
    }
}

# 4. Build Sections (e.g., Sidecar)
sidecar = Sidecar(layout="float")

# 5. Insert Content (text, maps, media)
slide1 = Slide(title="Welcome to Twin Creeks Active Adult")
slide1.content.append(Text("Twin Creeks is a 176-unit community reimagining active adult living in Allen, Texas."))
slide1.content.append(SMWebMap(gis.content.get(map_demo_id)))
sidecar.slides.append(slide1)

slide2 = Slide(title="Walkable, Wellness-First Design")
slide2.content.append(Text("A 15-minute walkable community with direct access to parks, dining, and healthcare."))
slide2.content.append(SMWebMap(gis.content.get(map_walk_id)))
sidecar.slides.append(slide2)

slide3 = Slide(title="A Prime Investment Market")
slide3.content.append(Text("Allen’s household growth, income, and aging population create a strong investment case."))
slide3.content.append(SMWebMap(gis.content.get(map_market_id)))
sidecar.slides.append(slide3)

slide4 = Slide(title="Get Involved")
slide4.content.append(Text("Contact our team to discuss investment opportunities in Twin Creeks Active Adult."))
slide4.content.append(Button(label="Contact Us", url="mailto:david@davidhickscompany.com"))
sidecar.slides.append(slide4)

# 6. Add Sections to Story
story.sections.append(sidecar)

# 7. Save and Publish Story
story.save()
story.publish()
print("✅ StoryMap published at:", story.url)
