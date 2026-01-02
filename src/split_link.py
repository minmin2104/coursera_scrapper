import json
import os


MAX_BATCH_COUNT = 480


def write_batch(payload, batch_num):
    output_dir = "batches"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"batch_{batch_num:02}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


if __name__ == "__main__":
    input_path = "courses_link.json"
    with open(input_path, "r") as f:
        links = json.load(f)
    split_url = []
    count = 0
    batch_num = 0
    for link in links:
        split_url.append(link)
        count += 1
        if count >= MAX_BATCH_COUNT:
            write_batch(split_url, batch_num)
            split_url = []
            count = 0
            batch_num += 1
    write_batch(split_url, batch_num)
