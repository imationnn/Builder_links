from schemas_dto import CategoryDTO, QueryShardUrlDTO


NAME = "name"
CHILDS = "childs"
SHARD = "shard"
QUERY = "query"
URL = "url"
BLACKHOLE = "blackhole"


def get_all_data_from_main_menu_by_desired_categories(
        main_menu: list[dict],
        desired_categories: list[str],
) -> list[CategoryDTO]:
    result: list[CategoryDTO] = []
    for category in main_menu:
        if category[NAME] in desired_categories:
            data = _recursive_parse_category_main_menu(category[CHILDS])
            result.append(CategoryDTO(category[NAME], data))
    return result


def _recursive_parse_category_main_menu(category_childs: list[dict]) -> list[QueryShardUrlDTO]:
    query_shard = []
    for sub_category in category_childs:
        if childs := sub_category.get(CHILDS):
            query_shard.extend(_recursive_parse_category_main_menu(childs))
        else:
            if sub_category[SHARD] == BLACKHOLE:
                continue
            query_shard.append(QueryShardUrlDTO(sub_category[QUERY], sub_category[SHARD], sub_category[URL]))
    return query_shard
