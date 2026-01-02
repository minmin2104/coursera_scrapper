from botasaurus.browser import browser, Driver
from my_log import MyLog
import json
from botasaurus.soupify import soupify
import coursera_util
import time
import os


MAX_RUNTIME_SECONDS = 3 * 60 * 60
START_TIME = time.time()
mylog = MyLog()
log = mylog.log
BATCH_NUM = os.getenv("BATCH_NUM")


def get_links(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


@browser(
        cache=True,
        parallel=5,
        output=f"batch_{BATCH_NUM}",
        reuse_driver=True,
        max_retry=5,
        )
def scrape_data(driver: Driver, data):
    if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
        log("Time limit reached. Skipping remaining task")
        return None
    log(f"Scraping: {data}")
    slug = data.split("/learn/")[1]
    link1 = f"https://www.coursera.org/api/courses.v1/?q=slug&slug={slug}&fields=description,instructorIds,partnerIds,primaryLanguages"  # noqa
    link2 = f"https://www.coursera.org/api/onDemandCourseMaterials.v2/?q=slug&slug={slug}&includes=modules,lessons,items"  # noqa

    # Get data from the website itself
    driver.short_random_sleep()
    driver.google_get(data)
    html = driver.page_html
    soup = soupify(html)
    estimate_complete_time = coursera_util.get_hours_to_complete(soup)
    skills_gain = coursera_util.get_skill_gain(soup)
    objectives = coursera_util.get_objective(soup)
    outcomes = coursera_util.get_outcomes(soup)
    rating = coursera_util.get_ratings(soup)
    difficulty_level = coursera_util.get_difficulty_level(soup)
    instructor = coursera_util.get_instructor(soup)
    partner = coursera_util.get_partner(soup)

    # Get data from the courses v1 api
    driver.short_random_sleep()
    driver.google_get(link1)
    courses_json_str = driver.get_text("pre")
    courses_json = json.loads(courses_json_str)
    coursesapi_data = coursera_util.filter_courses_json(courses_json)

    # Get data from the materials v2 api
    driver.short_random_sleep()
    driver.google_get(link2)
    material_json_str = driver.get_text("pre")
    material_json = json.loads(material_json_str)
    curriculum_data = coursera_util.filter_material_json(material_json)

    return {
            "url": data,
            "title": coursesapi_data["title"],
            "description": coursesapi_data["description"],
            "primaryLanguages": coursesapi_data["primaryLanguages"],
            "estimateCompleteTime": estimate_complete_time,
            "skillsGain": skills_gain,
            "objectives": objectives,
            "outcomes": outcomes,
            "rating": rating,
            "difficultyLevel": difficulty_level,
            "instructor": instructor,
            "partner": partner,
            "modules": curriculum_data
            }


@mylog.log_time
def main():
    filename = f"batches/batch_{BATCH_NUM}.json"
    links = get_links(filename)
    scrape_data(links)


if __name__ == "__main__":
    main()
