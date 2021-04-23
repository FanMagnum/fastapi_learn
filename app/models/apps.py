from typing import Optional, List

from odmantic import EmbeddedModel, Model


class Cve(EmbeddedModel):
    cve: str
    summary: str
    detail: str
    level: str
    published: str
    score: str


class AppSpider(Model):
    product: str
    version: str
    vendor: Optional[str]
    cves: Optional[List[Cve]]
