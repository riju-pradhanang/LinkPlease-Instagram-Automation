# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError
# from app.models import WebhookEvent, Rule, SendJob
# from app.schemas import WebhookPayload, WebhookResponse


# def process_webhook_event(db: Session, payload: WebhookPayload) -> WebhookResponse:
#     # 1. Deduplication check via database transaction and unique constraint
#     event = WebhookEvent(
#         event_id=payload.event_id,
#         user_id=payload.user_id,
#         comment_text=payload.comment_text
#     )

#     try:
#         db.add(event)
#         db.commit()
#     except IntegrityError:
#         db.rollback()
#         return WebhookResponse(
#             status="duplicate",
#             event_id=payload.event_id,
#             job_created=False,
#             message="Event already processed"
#         )

#     # 2. Rule matching logic
#     comment_lower = payload.comment_text.lower()
#     rules = db.query(Rule).all()

#     matched_rule = None
#     for rule in rules:
#         if rule.keyword.lower() in comment_lower:
#             matched_rule = rule
#             break

#     if not matched_rule:
#         return WebhookResponse(
#             status="processed",
#             event_id=payload.event_id,
#             job_created=False,
#             message="No matching rule found for comment text"
#         )

#     # 3. Create send job
#     job = SendJob(
#         event_id=payload.event_id,
#         user_id=payload.user_id,
#         link=matched_rule.response_link,
#         status="PENDING"
#     )
#     db.add(job)
#     db.commit()

#     return WebhookResponse(
#         status="processed",
#         event_id=payload.event_id,
#         job_created=True,
#         message=f"Send job created for rule keyword '{matched_rule.keyword}'"
#     )


async def process_event(event_id: str):
    pass