import random
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Operator, OperatorSourceWeight
from app.infrastructure.repositories import (
    OperatorRepository,
    OperatorSourceWeightRepository
)


class DistributionService:
    """Сервис для распределения обращений между операторами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.operator_repo = OperatorRepository(session)
        self.weight_repo = OperatorSourceWeightRepository(session)
    
    async def select_operator(
        self, source_id: int
    ) -> Optional[Operator]:
        """
        Выбрать оператора для источника с учётом весов и лимитов.
        
        Алгоритм:
        1. Получаем всех активных операторов для источника
        2. Фильтруем по лимиту нагрузки
        3. Выбираем оператора с учётом весов (вероятностный выбор)
        """
        # Получаем активных операторов для источника
        operators = await self.operator_repo.get_active_operators_for_source(source_id)
        
        if not operators:
            return None
        
        # Получаем веса для этих операторов
        weights = await self.weight_repo.get_weights_for_source(source_id)
        weight_map = {w.operator_id: w.weight for w in weights}
        
        # Фильтруем операторов по лимиту нагрузки
        available_operators: List[tuple[Operator, int]] = []
        for operator in operators:
            current_load = await self.operator_repo.get_operator_load(operator.id)
            if current_load < operator.max_load:
                weight = weight_map.get(operator.id, 1)
                available_operators.append((operator, weight))
        
        if not available_operators:
            return None
        
        # Выбираем оператора с учётом весов (вероятностный выбор)
        return self._weighted_random_choice(available_operators)
    
    def _weighted_random_choice(
        self, operators_with_weights: List[tuple[Operator, int]]
    ) -> Operator:
        """
        Вероятностный выбор оператора на основе весов.
        
        Пример: оператор1 с весом 10, оператор2 с весом 30
        Вероятности: 10/(10+30)=25% и 30/(10+30)=75%
        """
        operators = [op for op, _ in operators_with_weights]
        weights = [w for _, w in operators_with_weights]
        
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(operators)
        
        # Генерируем случайное число от 0 до total_weight
        random_value = random.uniform(0, total_weight)
        
        # Выбираем оператора на основе накопленных весов
        cumulative_weight = 0
        for operator, weight in operators_with_weights:
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return operator
        
        # На случай ошибки округления возвращаем последнего
        return operators[-1]

