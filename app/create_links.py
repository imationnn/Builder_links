BASE_URL = "https://www.wildberries.ru{}"
FILTER_URL = "https://catalog.wb.ru/catalog/{}/v6/filters?ab_testing=false&appType=1&{}&curr=rub&dest=-1255987&spp=30"
CATALOG_URL = "https://catalog.wb.ru/catalog/{0}/v2/catalog?ab_testing=false&appType=1&{1}&curr=rub&dest=-1255987&page={{}}&sort={sort}&spp=30"


def create_site_url(path: str) -> str:
    return BASE_URL.format(path)


def create_filter_url(shard: str, query: str) -> str:
    return FILTER_URL.format(shard, query)


def create_catalog_url(
        shard: str,
        query: str,
        sort: str,
        xsubject: str | int | None = None
) -> str:
    url = CATALOG_URL.format(shard, query, sort=sort)
    if xsubject is not None:
        url = url + f"&xsubject={xsubject}"
    return url
