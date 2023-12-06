"""Text-to-speech media source."""
from __future__ import annotations

import mimetypes
import logging

from homeassistant.components.media_player import BrowseError, MediaClass, MediaType
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    MEDIA_CLASS_MAP
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, LOGO_URL

_LOGGER = logging.getLogger(__name__)

async def async_get_media_source(hass: HomeAssistant) -> MediaSource:
    """Set up Synology media source."""
    return AlistMediaSource(hass)


class AlistMediaSource(MediaSource):

    name: str = "Alist"

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve media to a url."""
        entry_id, _, path = item.identifier.partition("/")
        alist = self.hass.data[DOMAIN][entry_id]
        url = await alist.async_resolve_download_url(path)
        mime_type, _ = mimetypes.guess_type(path.split("?sign=")[0])
        return PlayMedia(url, mime_type or "")

    async def async_guest_media_type(self, path):
        mime_type, _ = mimetypes.guess_type(path)
        media_class = MediaClass.DIRECTORY
        if mime_type:
            media_class = MEDIA_CLASS_MAP.get(
                mime_type.split("/")[0], MediaClass.DIRECTORY
            )
        return mime_type or "", media_class

    async def async_browse_media(
        self,
        item: MediaSourceItem,
    ) -> BrowseMediaSource:
        if item.identifier:
            entry_id, _, path = item.identifier.partition("/")
            alist = self.hass.data[DOMAIN][entry_id]

            children = []
            for file in await alist.async_list(path):
                file_path = f"{path}/{file.get('name')}"
                if (not file.get('is_dir')) and (sign:=file.get('sign')):
                    file_path += f"?sign={sign}"
                
                mime_type, media_class = await self.async_guest_media_type(file.get("name"))

                children.append(
                    BrowseMediaSource(
                        domain=DOMAIN,
                        identifier=f"{entry_id}/{file_path}",
                        media_class=media_class,
                        media_content_type=mime_type,
                        title=file.get("name"),
                        thumbnail=file.get("thumb"),
                        can_play=not file.get('is_dir'),
                        can_expand=file.get('is_dir'),
                    )
                )

            return BrowseMediaSource(
                domain=DOMAIN,
                identifier=item.identifier,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=alist.name,
                thumbnail=LOGO_URL,
                can_play=False,
                can_expand=True,
                children_media_class=MediaClass.DIRECTORY,
                children=children,
            )


        children = []
        for entry_id, alist in self.hass.data[DOMAIN].items():
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"{entry_id}",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=alist.name,
                    thumbnail=LOGO_URL,
                    can_play=False,
                    can_expand=True,
                )
            )

        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=None,
            media_class=MediaClass.APP,
            media_content_type="",
            title=self.name,
            thumbnail=LOGO_URL,
            can_play=False,
            can_expand=True,
            children_media_class=MediaClass.APP,
            children=children,
        )

