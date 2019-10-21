import random


def gen_collection(object_generator_func, start_element=0, count=None,
                   object_type="campaigns"):
    if count is None:
        random.randrange(10000)
    result = []
    i = 0
    volume = count - start_element
    for i in range(volume // 100):
        page = gen_page(object_generator_func, count=count,
                        object_type=object_type,
                        start_element=start_element + i * 100)
        result.append(page)
    if volume % 100 != 0:
        i = i + 1 if len(result) else 0
        page = gen_page(object_generator_func, count=count,
                        object_type=object_type,
                        start_element=start_element + i * 100,
                        num_elements=volume % 100)
        result.append(page)
    return result


def gen_page(object_generator_func, start_element=0, num_elements=None,
             count=None, object_type="campaigns"):
    if not object_generator_func or not callable(object_generator_func):
        raise ValueError("object_generator_func has to be set and callable")
    if count is None:
        count = random.randrange(10000)
    if num_elements is None:
        num_elements = min(count, 100)

    return {
        "status": "OK",
        "start_element": start_element,
        "num_elements": num_elements,
        "count": count,
        object_type: [object_generator_func(start_element + index)
                      for index in range(num_elements)]
    }


def gen_random_collection(start_element=0, count=None,
                          object_type="campaigns"):
    return gen_collection(
        object_generator_func=lambda index: {"id": random.randrange(1000000)},
        start_element=start_element, count=count, object_type=object_type)


def gen_ordered_collection(start_element, count, object_type="campaigns"):
    return gen_collection(
        object_generator_func=lambda index: {"id": index},
        start_element=start_element, count=count, object_type=object_type)
