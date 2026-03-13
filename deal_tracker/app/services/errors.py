# START_MODULE_CONTRACT
# Module: services.errors
# Intent: Доменные ошибки бизнес-логики.
# Возвращаются сервисами, НЕ HTTP-коды.
# END_MODULE_CONTRACT

from app.models.deal import DealStage


class NotFoundError(Exception):
    """
    [START_CONTRACT_NOT_FOUND_ERROR]
    Intent: Сущность не найдена в БД.
    Input: entity_name - имя сущности, entity_id - UUID.
    Output: Exception с сообщением "{entity_name} with id {entity_id} not found".
    [END_CONTRACT_NOT_FOUND_ERROR]
    """

    def __init__(self, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} not found")


class InvalidStageTransitionError(Exception):
    """
    [START_CONTRACT_INVALID_STAGE_TRANSITION]
    Intent: Недопустимый переход стадии сделки.
    Input: current_stage - текущая стадия, target_stage - целевая стадия, allowed - список допустимых.
    Output: Exception с сообщением о недопустимом переходе и допустимых стадиях.
    [END_CONTRACT_INVALID_STAGE_TRANSITION]
    """

    def __init__(
        self,
        current_stage: DealStage,
        target_stage: DealStage,
        allowed: list[DealStage],
    ):
        self.current_stage = current_stage
        self.target_stage = target_stage
        self.allowed = allowed
        allowed_str = ", ".join(s.value for s in allowed)
        super().__init__(
            f"Cannot transition from {current_stage.value} to {target_stage.value}. "
            f"Allowed stages: {allowed_str}"
        )


class ForeignKeyValidationError(Exception):
    """
    [START_CONTRACT_FK_VALIDATION_ERROR]
    Intent: Нарушение внешнего ключа при создании/обновлении.
    Input: field_name - имя поля FK, entity_name - имя связанной сущности.
    Output: Exception с сообщением о несуществующей связанной сущности.
    [END_CONTRACT_FK_VALIDATION_ERROR]
    """

    def __init__(self, field_name: str, entity_name: str):
        self.field_name = field_name
        self.entity_name = entity_name
        super().__init__(f"{field_name} references non-existent {entity_name}")


class DuplicateEmailError(Exception):
    """
    [START_CONTRACT_DUPLICATE_EMAIL]
    Intent: Дублирование email при создании пользователя.
    Input: email - дублирующийся email.
    Output: Exception с сообщением о дублировании.
    [END_CONTRACT_DUPLICATE_EMAIL]
    """

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists")


class HasRelatedEntitiesError(Exception):
    """
    [START_CONTRACT_HAS_RELATED]
    Intent: Невозможно удалить сущность из-за связанных записей.
    Input: entity_name - имя удаляемой сущности, related_name - имя связанных сущностей.
    Output: Exception с сообщением о невозможности удаления.
    [END_CONTRACT_HAS_RELATED]
    """

    def __init__(self, entity_name: str, related_name: str):
        self.entity_name = entity_name
        self.related_name = related_name
        super().__init__(
            f"Cannot delete {entity_name} because it has associated {related_name}"
        )