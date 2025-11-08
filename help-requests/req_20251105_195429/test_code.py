
def slow_function():
    # この関数が遅い
    result = []
    for i in range(10000):
        for j in range(10000):
            result.append(i * j)
    return result
