import logging

from jinja2 import Template

from app.repository.redis_storage import RedisStorage
from app.create_links import create_site_url
from app.schemas.schemas_dto import NotifyItem, SubCategoryDTO, XsubjectDTO, CategoryDTO
from app.request.httpx_client import HTTPXClient
from app.config.settings import settings


logger = logging.getLogger(__name__)


NOTIFY_TEMPLATE = """{% for category in categories -%}
Новые категории в разделе {{ category.category }}:
{% for subcat in category.sub_cat_dto -%}
{{ subcat.url }}
{% if not subcat.xsubjects -%}
db id: {{ subcat.id }} - {{ subcat.name }}
{% endif -%}
{% for xsub in subcat.xsubjects -%}
db id: {{ xsub.id }} - {{ xsub.name }}
{% endfor %}
{% endfor %}
{% endfor %}"""


class Notification:
    def __init__(self, repository: RedisStorage):
        self.repository = repository
        self.client = HTTPXClient()
        self.template = Template(NOTIFY_TEMPLATE)

    @staticmethod
    async def _add_notify_item(
            obj: SubCategoryDTO | XsubjectDTO,
            category_name: str,
            notify_id: int,
            notify_data: dict,
            notify_items: list,
            url: str,
            subcat_query: str | int = None,
            xsubject: str | int = None
    ) -> int:
        notify_id += 1
        obj.id = notify_id
        notify_data[notify_id] = NotifyItem(
            category_name,
            xsubject=xsubject,
            subcategory=subcat_query,
            item_name=obj.name,
            url=url
        )
        notify_items.append(subcat_query or xsubject)
        return notify_id

    async def _parse_notification(self, category_notification: list[CategoryDTO]):
        notify_id = await self.repository.get_last_item_alert_key()
        notify_data = {}
        notify_items = []
        for category in category_notification:
            for subcategory in category.sub_cat_dto:
                subcategory.url = create_site_url(subcategory.url)
                if not subcategory.xsubjects:
                    notify_id = await self._add_notify_item(
                        subcategory,
                        category.category,
                        notify_id,
                        notify_data,
                        notify_items,
                        subcategory.url,
                        subcat_query=subcategory.query,
                    )
                for xsubject in subcategory.xsubjects:
                    notify_id = await self._add_notify_item(
                        xsubject,
                        category.category,
                        notify_id,
                        notify_data,
                        notify_items,
                        subcategory.url,
                        xsubject=xsubject.id
                    )
        return notify_data, notify_items

    async def start_notify(self) -> None:
        category_notification = await self.repository.get_category_for_notification()

        if not category_notification:
            return

        notify_data, notify_items = await self._parse_notification(category_notification)
        notification = self.template.render(categories=category_notification)

        if settings.use_notify_log:
            logger.warning(notification)

        await self.send_notification(notification)
        await self.repository.add_items_for_sent_alerts(notify_data, notify_items)
        await self.repository.delete_category_for_notification()

    async def send_notification(self, message: str) -> None:
        if settings.use_notify_send:
            await self.client.post(settings.notify_config.notify_url, message)
            await self.client.close_client()
