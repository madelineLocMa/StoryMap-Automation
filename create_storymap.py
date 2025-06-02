
import argparse
import logging
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.apps.storymap import StoryMap, Sidecar, Slide, Text, WebMap as SMWebMap, Button
from arcgis.features import FeatureLayerCollection
import arcgis

# ----------------------------------------
# Logging Configuration
# ----------------------------------------
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ----------------------------------------
# Global Constants (to be customized)
# ----------------------------------------
STORY_TITLE = "Twin Creeks Active Adult – Investing in the Future of Senior Living"
STORY_SUBTITLE = "A wellness-centered senior living community in Allen, Texas."
COVER_IMAGE_URL = "https://your-hosted-image-url.com/twincreeks_cover.jpg"  # TODO: Replace with actual URL

# TODO: Replace with actual hosted feature layer URLs
layer_url_demo = "https://services.arcgis.com/.../Age55PlusLayer/FeatureServer/0"
layer_url_walk = "https://services.arcgis.com/.../WalkBufferLayer/FeatureServer/0"
layer_url_market = "https://services.arcgis.com/.../MarketGrowthLayer/FeatureServer/0"

# ----------------------------------------
# Create and Share a Web Map Item
# ----------------------------------------
def create_and_share_webmap(gis, layer_url, title, description, tags):
    try:
        flc = FeatureLayerCollection(layer_url, gis)
        layer = flc.layers[0]

        # Optional: Configure pop-up (adjust fields to your schema)
        layer.popup_info = {
            "title": "{TRACT_NAME}",
            "content": "{AGE_55PLUS} residents age 55+"
        }

        web_map = WebMap()
        web_map.basemap = "gray-vector"
        web_map.add_layer(layer, {"title": title})

        # Optional: Set extent if known
        web_map.extent = {
            "spatialReference": {"wkid": 4326},
            "xmin": -97.0,
            "ymin": 32.5,
            "xmax": -96.5,
            "ymax": 33.0
        }

        item = web_map.save({
            "title": title,
            "snippet": description,
            "tags": tags,
            "description": description,
            "folder": "TwinCreeks"
        })
        item.share(everyone=True)
        logging.info(f"WebMap created and shared: {title}")
        return item.id
    except Exception as e:
        logging.error(f"Failed to create WebMap for {title}: {e}")
        return None

# ----------------------------------------
# Construct StoryMap Sidecar with Slides
# ----------------------------------------
def build_sidecar(gis, map_demo_id, map_walk_id, map_market_id):
    try:
        demo_map = SMWebMap(gis.content.get(map_demo_id))
        walk_map = SMWebMap(gis.content.get(map_walk_id))
        market_map = SMWebMap(gis.content.get(map_market_id))

        sidecar = Sidecar(layout="floating")

        slide1 = Slide(title="Welcome to Twin Creeks Active Adult")
        slide1.content.append(Text("Twin Creeks is a 176-unit community reimagining active adult living in Allen, Texas."))
        slide1.content.append(demo_map)
        sidecar.slides.append(slide1)

        slide2 = Slide(title="Walkable, Wellness-First Design")
        slide2.content.append(Text("A 15-minute walkable community with direct access to parks, dining, and healthcare."))
        slide2.content.append(walk_map)
        sidecar.slides.append(slide2)

        slide3 = Slide(title="A Prime Investment Market")
        slide3.content.append(Text("Allen’s household growth, income, and aging population create a strong investment case."))
        slide3.content.append(market_map)
        sidecar.slides.append(slide3)

        slide4 = Slide(title="Get Involved")
        slide4.content.append(Text("Contact our team to discuss investment opportunities in Twin Creeks Active Adult."))
        slide4.content.append(Button(label="Contact Us", url="mailto:david@davidhickscompany.com"))
        sidecar.slides.append(slide4)

        return sidecar
    except Exception as e:
        logging.error(f"Failed to build sidecar slides: {e}")
        raise

# ----------------------------------------
# Save and Publish the Final StoryMap
# ----------------------------------------
def publish_storymap(gis, sidecar):
    try:
        story = StoryMap(gis=gis)
        story.title = STORY_TITLE
        story.subtitle = STORY_SUBTITLE

        story.cover(
            title=story.title,
            type="full",
            summary=story.subtitle,
            by_line="David Hicks Company",
            image=COVER_IMAGE_URL
        )

        story.sections.append(sidecar)
        story.save()

        story.item.update({
            "tags": ["TwinCreeks", "Senior Living", "Wellness", "DFW"],
            "snippet": "An automated story about wellness-focused senior living in Allen, TX",
            "description": "This StoryMap was created automatically using the ArcGIS Python API."
        })

        story.publish()
        logging.info("StoryMap published successfully.")
        logging.info(f"URL: {story.item.homepage}")
    except Exception as e:
        logging.error(f"Failed to publish StoryMap: {e}")

# ----------------------------------------
# Main Workflow
# ----------------------------------------
def main(username, password):
    logging.info("Authenticating with ArcGIS Online...")
    gis = GIS("https://www.arcgis.com", username, password)
    logging.info(f"ArcGIS Python API version: {arcgis.__version__}")

    logging.info("Creating and sharing WebMaps...")
    demo_id = create_and_share_webmap(gis, layer_url_demo, "Twin Creeks – Age 55+", "Density of residents age 55+ in the DFW area", ["TwinCreeks", "Demographics"])
    walk_id = create_and_share_webmap(gis, layer_url_walk, "Twin Creeks – Walkability", "Walkable POIs within 15 minutes", ["TwinCreeks", "Access"])
    market_id = create_and_share_webmap(gis, layer_url_market, "Twin Creeks – Market Strength", "Household income and projected growth", ["TwinCreeks", "Market"])

    if not all([demo_id, walk_id, market_id]):
        logging.error("One or more WebMaps failed to create. Exiting.")
        return

    logging.info("Building StoryMap structure...")
    sidecar = build_sidecar(gis, demo_id, walk_id, market_id)

    logging.info("Publishing StoryMap...")
    publish_storymap(gis, sidecar)

# ----------------------------------------
# Command-Line Interface
# ----------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate ArcGIS StoryMap creation.")
    parser.add_argument("--username", required=True, help="ArcGIS Online username")
    parser.add_argument("--password", required=True, help="ArcGIS Online password")
    args = parser.parse_args()

    main(args.username, args.password)
