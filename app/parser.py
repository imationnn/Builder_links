from app.request.httpx_client import DataResponse
from app.schemas.schemas_dto import CategoryDTO, SubCategoryDTO, XsubjectDTO

NAME = "name"
CHILDS = "childs"
SHARD = "shard"
BLACKHOLE = "blackhole"
DATA = "data"
FILTERS = "filters"
KEY = "key"
XSUBJECT = "xsubject"
ITEMS = "items"
TOTAL = "total"


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


def _recursive_parse_category_main_menu(category_childs: list[dict]) -> list[SubCategoryDTO]:
    sub_cat_lst = []
    for sub_category in category_childs:
        if childs := sub_category.get(CHILDS):
            sub_cat_lst.extend(_recursive_parse_category_main_menu(childs))
        else:
            if sub_category[SHARD] == BLACKHOLE:
                continue
            sub_cat_lst.append(SubCategoryDTO.from_dict(sub_category))
    return sub_cat_lst


def get_xsubjects_from_response(lst_responses: list[DataResponse]) -> list[SubCategoryDTO]:
    sub_cat_lst = []
    for response in lst_responses:
        if not (response_data := response.data.get(DATA)):
            continue
        for data_filter in response_data[FILTERS]:
            if data_filter[KEY] == XSUBJECT:
                response.args.xsubjects = [XsubjectDTO.from_dict(item) for item in data_filter[ITEMS]]
                break
        response.args.total = response_data.get(TOTAL, 0)
        sub_cat_lst.append(response.args)
    return sub_cat_lst
