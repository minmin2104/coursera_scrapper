from bs4 import BeautifulSoup


def contain_to_complete_str(s: str):
    return "to complete" in s


def get_hours_to_complete(soup: BeautifulSoup):
    elem = soup.find("div", attrs={"data-e2e": "key-information"})
    if not elem:
        return ""
    estimated_complete = elem.find("div", string=contain_to_complete_str).get_text()  # noqa
    return estimated_complete


def span_aria_hidden(tag):
    aria_hidden = tag.name == "span" and tag.has_attr("aria-hidden")
    inside_a_tag = tag.name == "a"
    return aria_hidden or inside_a_tag


def get_skill_gain(soup: BeautifulSoup):
    """
    Skills you'll gain section in Coursera
    """
    skills_gain = []
    h2_skill_gain = soup.find("h2", string="Skills you'll gain")
    if not h2_skill_gain:
        return skills_gain
    parent_div = h2_skill_gain.parent.parent
    skills_gain_ul = parent_div.find("ul")
    if not skills_gain_ul:
        return skills_gain
    skills_li = skills_gain_ul.find_all("li")
    if not skills_li:
        return skills_gain
    for li in skills_li:
        span_has_text = li.find(span_aria_hidden)
        if span_has_text is None:
            continue
        skill = span_has_text.get_text()
        skills_gain.append(skill)
    return skills_gain


def get_objective(soup: BeautifulSoup):
    """
    What you'll learn section in Coursera
    """
    objectives = []
    h2_learn = soup.find("h2", string="What you'll learn")
    if not h2_learn:
        return objectives
    parent_div = h2_learn.parent.parent
    objective_ul = parent_div.find("ul")
    if not objective_ul:
        return objectives
    objective_lis = objective_ul.find_all("li")
    if not objective_lis:
        return objectives
    for li in objective_lis:
        span_has_text = li.find("span", string=True)
        objective = span_has_text.get_text()
        objectives.append(objective)
    return objectives


def get_outcomes(soup: BeautifulSoup):
    """
    Get outcomes section on Coursera
    """
    outcomes = []
    outcomes_div = soup.find("div", attrs={"id": "outcomes"})
    if not outcomes_div:
        return outcomes
    outcomes_lis = outcomes_div.find_all("li")
    if not outcomes_lis:
        return outcomes
    for li in outcomes_lis:
        outcome = li.get_text()
        outcomes.append(outcome)
    return outcomes


def is_star_div(tag):
    return tag.name == "div" and tag.has_attr("aria-label") \
        and "stars" in tag.get("aria-label")


def get_ratings(soup: BeautifulSoup):
    """
    Get ratings if available
    """
    rating_div = soup.find(is_star_div)
    if not rating_div:
        return "N/A"
    rating = rating_div.get_text()
    return rating


def contain_level_str(s: str):
    return "level" in s


def get_difficulty_level(soup: BeautifulSoup):
    """
    Get difficulty level from Coursera
    - Beginner Level
    - Intermediate Level
    - Advanced Level
    - Mixed Level
    """
    div = soup.find("div", string=contain_level_str)
    if not div:
        return "N/A"
    return div.get_text()


def get_instructor(soup: BeautifulSoup):
    target_a = soup.find("a", attrs={"data-track-component": "hero-instructor"})  # noqa
    if not target_a:
        return "N/A"
    instructor = target_a.find("span").get_text()
    return instructor


def get_partner(soup: BeautifulSoup):
    target_a = soup.find("a", attrs={"data-track-component": "partner"})
    if not target_a:
        return "N/A"
    partner = target_a.find("span").get_text()
    return partner


def filter_courses_json(courses_json: dict):
    elements = courses_json["elements"]
    element = elements[0]
    title = element["name"]
    description = element["description"]
    primary_lang = element["primaryLanguages"][0]
    return {
            "title": title,
            "description": description,
            "primaryLanguages": primary_lang
            }


def filter_material_json(material_json: dict):
    linked = material_json.get("linked", {})

    # 1. Create lookups for quick access
    # Map items by ID
    items_map = {
        item["id"]: {
            "name": item["name"],
            "id": item["id"],
            "slug": item["slug"],
            "time_mins": round(item["timeCommitment"] / 60000, 2)
        }
        for item in linked.get("onDemandCourseMaterialItems.v2", [])
    }

    # Map lessons by ID
    lessons_map = {
        lesson["id"]: {
            "name": lesson["name"],
            "id": lesson["id"],
            "slug": lesson["slug"],
            "total_time_mins": round(lesson["timeCommitment"] / 60000, 2),
            "items": [items_map[iid] for iid in lesson["itemIds"] if iid in items_map]
        }
        for lesson in linked.get("onDemandCourseMaterialLessons.v1", [])
    }

    # 2. Build the final nested structure starting from Modules
    filtered_modules = []
    for module in linked.get("onDemandCourseMaterialModules.v1", []):
        filtered_modules.append({
            "module_name": module["name"],
            "module_id": module["id"],
            "description": module.get("description", ""),
            "total_duration_mins": round(module["timeCommitment"] / 60000, 2),
            "lessons": [lessons_map[lid] for lid in module["lessonIds"] if lid in lessons_map]
        })

    return filtered_modules

