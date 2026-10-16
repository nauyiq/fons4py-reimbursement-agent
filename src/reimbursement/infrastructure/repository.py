"""报销单仓储：封装两张核心表的读写。

对照 Java：≈ 手写版 Spring Data JPA Repository。

事务边界原则（AGENTS.md 红线）：仓储不开启、不提交事务，
只做 flush（拿主键）；会话与事务由调用方（未来的 application 用例）管理。
这样 Day 03 的领域服务可以在一个事务里编排多个仓储操作。
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from reimbursement.infrastructure.orm import (
    ReimbursementExpenseModel,
    ReimbursementOrderModel,
)


class ReimbursementRepository:
    """两张核心表的 CRUD 仓储。"""

    # ---------- 报销单 ----------

    async def create_order(
        self,
        session: AsyncSession,
        *,
        order_no: str,
        reimbursement_type: str,
        title: str,
        applicant_id: str,
        trip_source: str | None = None,
        trip_id: str | None = None,
        trip_no: str | None = None,
    ) -> ReimbursementOrderModel:
        order = ReimbursementOrderModel(
            order_no=order_no,
            reimbursement_type=reimbursement_type,
            title=title,
            applicant_id=applicant_id,
            trip_source=trip_source,
            trip_id=trip_id,
            trip_no=trip_no,
        )
        session.add(order)
        await session.flush()  # 取回自增主键，不提交事务
        return order

    async def get_order(
        self, session: AsyncSession, order_id: int
    ) -> ReimbursementOrderModel | None:
        return await session.get(ReimbursementOrderModel, order_id)

    async def get_order_by_no(
        self, session: AsyncSession, order_no: str
    ) -> ReimbursementOrderModel | None:
        result = await session.execute(
            select(ReimbursementOrderModel).where(
                ReimbursementOrderModel.order_no == order_no
            )
        )
        return result.scalar_one_or_none()

    # ---------- 费用明细 ----------

    async def add_expense(
        self,
        session: AsyncSession,
        *,
        order_id: int,
        expense_type: str,
        expense_date: date,
        amount: Decimal,
        description: str | None = None,
    ) -> ReimbursementExpenseModel:
        expense = ReimbursementExpenseModel(
            order_id=order_id,
            expense_type=expense_type,
            expense_date=expense_date,
            amount=amount,
            description=description,
        )
        session.add(expense)
        await session.flush()
        return expense

    async def list_expenses(
        self, session: AsyncSession, order_id: int
    ) -> list[ReimbursementExpenseModel]:
        result = await session.execute(
            select(ReimbursementExpenseModel)
            .where(ReimbursementExpenseModel.order_id == order_id)
            .order_by(ReimbursementExpenseModel.id)
        )
        return list(result.scalars().all())

    async def update_expense(
        self,
        session: AsyncSession,
        expense_id: int,
        *,
        amount: Decimal | None = None,
        description: str | None = None,
        expense_type: str | None = None,
        expense_date: date | None = None,
    ) -> ReimbursementExpenseModel | None:
        """修改费用明细。仅更新显式传入的字段（None 表示不改）。"""
        expense = await session.get(ReimbursementExpenseModel, expense_id)
        if expense is None:
            return None
        if amount is not None:
            expense.amount = amount
        if description is not None:
            expense.description = description
        if expense_type is not None:
            expense.expense_type = expense_type
        if expense_date is not None:
            expense.expense_date = expense_date
        await session.flush()
        return expense
