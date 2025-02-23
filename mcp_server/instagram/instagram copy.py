import dotenv
import json
import os
from instagrapi import Client
from mcp.server.fastmcp import FastMCP
from typing import Any


# Initialize FastMCP server
mcp = FastMCP("instagram")

dotenv.load_dotenv()
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


def login_user():
    cl = Client()
    cl.delay_range = [1, 3]  # Increase delay to 1 to 3 seconds between requests.
    
    session_file = "instagrapi_session.json"
    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            if os.path.exists(session_file):
                session = cl.load_settings(session_file)
                cl.set_settings(session)
                cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                cl.get_timeline_feed()  # Test if session is valid.
            else:
                cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                cl.dump_settings(session_file)
            print(f"Successfully logged in")
            return cl
        except Exception as e:
            print(f"Login attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"Max login attempts reached")
    
    raise Exception(f"Couldn't login user")


cl = login_user()
INSIGHTS_ACCOUNT: dict = cl.insights_account()
INSIGHTS_MEDIA_FEED_ALL: list[dict] = cl.insights_media_feed_all(time_frame="TWO_YEARS", data_ordering="REACH_COUNT")
cl.logout()


@mcp.tool()
async def get_insights_account() -> str:
    """
    Get Instagram account insights, such as:
      * profile_visits_metric_count
      * impressions_metric_count
      * last_week_impressions
      * followers_unit
      * gender_graph
      * all_followers_age_graph
      * followers_top_cities_graph
      * top_posts_unit
      * last_week_posts_count
      * week_over_week_posts_delta
      * stories_unit
      * last_week_stories_count
      * week_over_week_stories_delta
      * summary_stories
      * promotions_unit
      * summary_promotions
    """
    result = json.dumps(INSIGHTS_ACCOUNT)
    return result


@mcp.tool()
async def get_insights_media_feed_all() -> str:
    """
    Get Instagram top-reach-count media insights, such as:
      * instagram_media_type
      * uri
      * like_count
      * save_count
      * video_view_count
      * shopping_product_click_count
      * impressions
      * attributed_follows
      * attributed_profile_visits
      * reach_count
      * profile_actions
    """
    max_medias = 10
    insights_medias = [json.dumps(insights_media) for insights_media in INSIGHTS_MEDIA_FEED_ALL[:max_medias]]
    result = "\n---\n".join(insights_medias)
    return result


# @mcp.tool()
# async def get_user_medias():
#     """Get the Instagram user medias."""
#     cl = login_user()
#     user_id = cl.user_id_from_username(INSTAGRAM_USERNAME)
#     user_medias = cl.user_medias(user_id)
#     cl.logout()
#     return user_medias


if __name__ == "__main__":
    # Initialize and run the server.
    mcp.run(transport='stdio')
