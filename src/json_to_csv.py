import csv
import json


def json_to_csv(json_list, output_filename="detailed_course_data.csv"):
    # Define comprehensive headers
    fieldnames = [
        "course_title", "url", "difficulty", "estimate_total", "partner",
        "skills_gain", "objectives", "outcomes",
        "module_name", "module_description", "module_duration_mins",
        "lesson_name", "lesson_slug", "lesson_duration_mins",
        "item_name", "item_id", "item_duration_mins"
    ]

    flattened_rows = []

    for course in json_list:
        # Join lists into strings for CSV compatibility
        skills = "; ".join(course.get("skillsGain", []))
        objectives = "; ".join(course.get("objectives", []))
        outcomes = "; ".join(course.get("outcomes", []))

        course_meta = {
            "course_title": course.get("title", ""),
            "url": course.get("url", ""),
            "difficulty": course.get("difficultyLevel", ""),
            "estimate_total": course.get("estimateCompleteTime", ""),
            "partner": course.get("partner", ""),
            "skills_gain": skills,
            "objectives": objectives,
            "outcomes": outcomes
        }

        for module in course.get("modules", []):
            module_meta = {
                "module_name": module.get("module_name", ""),
                "module_description": module.get("description", "").replace("\n", " "),
                "module_duration_mins": module.get("total_duration_mins", 0)
            }

            for lesson in module.get("lessons", []):
                lesson_meta = {
                    "lesson_name": lesson.get("name", ""),
                    "lesson_slug": lesson.get("slug", ""),
                    "lesson_duration_mins": lesson.get("total_time_mins", 0)
                }

                # Check if there are items, otherwise create a row for the lesson itself
                items = lesson.get("items", [])
                if not items:
                    row = {**course_meta, **module_meta, **lesson_meta, 
                           "item_name": "N/A", "item_id": "N/A", "item_duration_mins": 0}
                    flattened_rows.append(row)
                else:
                    for item in items:
                        row = {
                            **course_meta,
                            **module_meta,
                            **lesson_meta,
                            "item_name": item.get("name", ""),
                            "item_id": item.get("id", ""),
                            "item_duration_mins": item.get("time_mins", 0)
                        }
                        flattened_rows.append(row)

    # Write the file
    with open(output_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_rows)

    return f"Exported {len(flattened_rows)} rows to {output_filename}"


if __name__ == "__main__":
    # Usage:
    with open('output/test.json', 'r') as f:
        data = json.load(f)
        json_to_csv(data)
