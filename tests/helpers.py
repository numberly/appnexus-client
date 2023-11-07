import random


def default_object_generator_func(index, randomize=False):
    if randomize:
        return {"id": random.randrange(1000000)}
    return {"id": index}


def gen_page(start_element=0, count=None, num_elements=None,
             object_type="campaigns",
             object_generator_func=default_object_generator_func,
             randomize=False):
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
        object_type: [object_generator_func(start_element + index, randomize)
                      for index in range(num_elements)]
    }


def gen_collection(start_element=0, count=None, object_type="campaigns",
                   object_generator_func=default_object_generator_func,
                   randomize=False):
    if count is None:
        random.randrange(10000)

    result = []
    i = 0
    volume = count - start_element
    for i in range(volume // 100):
        page = gen_page(
            start_element=start_element + i * 100,
            count=count,
            object_type=object_type,
            object_generator_func=object_generator_func,
            randomize=randomize
        )
        result.append(page)

    if volume % 100 != 0:
        i = i + 1 if len(result) else 0
        page = gen_page(
            start_element=start_element + i * 100,
            count=count,
            num_elements=volume % 100,
            object_type=object_type,
            object_generator_func=object_generator_func,
            randomize=randomize
        )
        result.append(page)

    return result
