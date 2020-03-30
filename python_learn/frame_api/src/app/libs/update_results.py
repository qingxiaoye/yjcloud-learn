# -*- coding: utf-8 -*-
from sqlalchemy import and_

from app.libs.calculate_score import qia_score
from app.models.base import db_v1
from app.models.qi_qia_models import QiResultsDetail, QiInfoTraffic


def update_hit_status(update_id, call_id):
    list_id = update_id.split(',')
    ud_id = []
    for i in list_id:
        ud_id.append(int(i))
    with db_v1.auto_commit():
        db_v1.session.query(QiResultsDetail).filter(QiResultsDetail.id.in_(ud_id)).update({"hit_status": 0,
                                                                                             "review_status": 2})
        # 审核正确
        db_v1.session.query(QiResultsDetail).filter(and_(QiResultsDetail.call_id == call_id,
                                                         QiResultsDetail.review_status == 0,
                                                         QiResultsDetail.id.notin_(ud_id))).update(
            {"review_status": 1}, synchronize_session=False)

        db_v1.session.query(QiInfoTraffic).filter(QiInfoTraffic.call_id == call_id).update({"review_status": 2})
    # qia_score(call_id)