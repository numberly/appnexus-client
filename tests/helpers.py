import random


def gen_random_object():
    return {"id": random.randrange(1000000)}


def gen_random_page(num_elements=None, start_element=0, count=None,
                    object_type="campaigns"):
    if count is None:
        count = random.randrange(10000)
    if num_elements is None:
        num_elements = min(count, 100)

    return {
        "status": "OK",
        "start_element": start_element,
        "num_elements": num_elements,
        "count": count,
        object_type: [gen_random_object() for _ in range(num_elements)]
    }


def gen_random_collection(count=None, object_type="campaigns"):
    if count is None:
        count = random.randrange(10000)
    result = []
    i = 0
    for i in range(count // 100):
        random_page = gen_random_page(count=count, object_type=object_type,
                                      start_element=i * 100)
        result.append(random_page)
    if count % 100 != 0:
        random_page = gen_random_page(count=count, object_type=object_type,
                                      start_element=i * 100,
                                      num_elements=count % 100)
        result.append(random_page)
    return result
