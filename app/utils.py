
MAIN_CATEGORIES = {
    "Женщинам": "woman",
    "Обувь": "shoes",
    "Детям": "kids",
    "Мужчинам": "man",
    "Дом": "house",
    "Электроника": "elect",
    "Бытовая техника": "technique",
    "Спорт": "sport",
    "Для ремонта": "repair",
    "Сад и дача": "village",
    "Продукты": "food"
}


def category_name_to_name_with_underscore(name: str) -> str:
    """
    Converts a category name into a category name with underscores
    :param name:
    :return:
    """
    return name.replace(" ", "_").capitalize()


def category_name_to_name_without_underscore(name: str) -> str:
    """
    Converts a category name into a category name without underscores
    :param name:
    :return:
    """
    return name.replace("_", " ").capitalize()


def get_translate_category_name(category: str) -> str:
    if "_" in category:
        category = category_name_to_name_without_underscore(category)
    return MAIN_CATEGORIES.get(category.capitalize())
