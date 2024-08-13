from app.config.categories import MAIN_CATEGORIES


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
    return MAIN_CATEGORIES.get(category.capitalize(), "")


def get_lst_category_name_without_underscore(categories: list[str]) -> list[str]:
    return [category_name_to_name_without_underscore(category) for category in categories]
