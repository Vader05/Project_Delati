import paralleldots


def compare_text(text_a, text_b):
    print("{} {}".format("text_a: ", text_a))
    print("{} {}".format("text_b: ", text_b))
    paralleldots.set_api_key('VTpYXtJtNEOrPA2uqvLknLpAANMrbgEYOzyDxE7DmYg')
    score = paralleldots.similarity(text_a, text_b)
    print(score)
    similarity_score = score['similarity_score']
    print(similarity_score)
    return similarity_score


def compare_text_array(array_a, array_b):
    for element_a in array_a:
        score_max = 0
        element_max = None
        if len(element_a.split()) > 1:
            for element_b in array_b:
                score = compare_text(element_a, element_b["descripcion"])
                print("{} {}".format("score_max: ", score_max))
                if score > score_max:
                    score_max = score
                    element_max = element_b
            print("=========")
            print(element_max)
            element_max["cant"] = element_max["cant"] + 1
