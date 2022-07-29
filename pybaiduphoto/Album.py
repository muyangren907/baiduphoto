import logging
from .OnlineItem import OnlineItem


class Album:
    def __init__(self, info, req):
        self.info = info
        self.req = req

    def append(self, itemObjs):
        if type(itemObjs) is not list:
            itemObjlist = [itemObjs]
        else:
            itemObjlist = itemObjs

        url = "https://photo.baidu.com/youai/album/v1/addfile"
        params = dict(
            (
                ("clienttype", "70"),
                # ('bdstoken', '26.....'),
                ("album_id", self.getID()),
                ("tid", self._getTID()),
                (
                    "list",
                    "[{}]".format(
                        ",".join(
                            [
                                """{{"fsid":{}}}""".format(item.getID())
                                for item in itemObjlist
                            ]
                        )
                    ),
                ),
            )
        )
        logging.debug("Album-append, getParams=[{}]".format(params))
        response = self.req.getReqJson(url, params=params)
        return response

    def deleteItem(self, items, isOrigin=False):
        # item = item or itemlist
        if type(items) is not list:
            items = [items]
        uk = self.info["cover_info"]["uk"]  # what is this????
        data = {
            "album_id": self.getID(),
            "tid": self._getTID(),
            "list": "[{}]".format(
                ",".join(
                    [
                        """{{"fsid":{},"uk":{}}}""".format(item.getID(), uk)
                        for item in items
                    ]
                )
            ),
            "del_origin": "1" if isOrigin else "0",
        }
        url = "https://photo.baidu.com/youai/album/v1/delfile"
        resDict = self.req.postReqJson(url, data=data)
        return resDict

        # https://photo.baidu.com/youai/album/v1/delfile

    def delete(self, isWithItems=True):
        data = {
            "album_id": self.getID(),
            "delete_origin_image": {True: "1", False: "0"}[isWithItems],
            "tid": self._getTID(),
        }
        url = "https://photo.baidu.com/youai/album/v1/delete"
        return self.req.postReqJson(url, data=data)

    def get_OnlineItems(self, cursor=""):
        data = {
            "cursor": cursor,
            "album_id": self.info["album_id"],
            "need_amount": "1",
            "limit": "100",
            "passwd": "",
        }
        url = "https://photo.baidu.com/youai/album/v1/listfile"
        res = self.req.postReqJson(url=url, data=data)
        return {
            "items": [
                OnlineItem(info=itemInfo, req=self.req) for itemInfo in res["list"]
            ],
            "has_more": res["has_more"] == 1,
            "cursor": res["cursor"],
        }

    def get_AllOnlineItems(self, max=0) -> list:
        cursor = None
        r = []
        c = 0
        while True:
            page = self.get_OnlineItems(cursor=cursor)
            r += page["items"]
            if page["has_more"]:
                cursor = page["cursor"]
                if max > 0:
                    if len(r) >= max:
                        break
            else:
                break
        if max <= 0:
            return r
        else:
            return r[:max]

    def getName(self):
        return self.info["title"]

    def getID(self):
        return self.info["album_id"]

    def _getTID(self):
        return self.info["tid"]

    def getInfo(self):
        # as a backup, not use for read directly
        return self.info
