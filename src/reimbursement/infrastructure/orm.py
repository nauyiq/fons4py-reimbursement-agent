"""核心业务表 ORM 映射（对照 JPA 实体类）。

严格对应 docs/03-domain-and-data.md 的 MySQL V1 最小表结构：
- reimbursement_order / reimbursement_expense 两张核心表
- 金额列用 Numeric(18,2)，Python 侧映射为 Decimal（红线：禁止 float）
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有 ORM 模型的声明基类（对照 @MappedSuperclass）。"""


class ReimbursementOrderModel(Base):
    """报销单（聚合根）的持久化映射。

    对照 JPA：@Table(name="reimbursement_order") + @Column 注解的实体类。
    CHECK 约束与索引通过 __table_args__ 声明（对照 DDL 里的 CONSTRAINT/INDEX）。
    """

    __tablename__ = "reimbursement_order"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    reimbursement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    applicant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    trip_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    trip_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    trip_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency: Mapped[str] = mapped_column(
        CHAR(3), nullable=False, server_default=text("'CNY'")
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0.00")
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'DRAFT'")
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    submitted_at: Mapped[datetime | None] = mapped_column(
        DATETIME(fsp=3), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=3), nullable=False, server_default=text("CURRENT_TIMESTAMP(3)")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=3), nullable=False, server_default=text("CURRENT_TIMESTAMP(3)")
    )

    #: 费用明细（聚合内实体）。delete-orphan：订单删除时明细级联删除。
    expenses: Mapped[list["ReimbursementExpenseModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "reimbursement_type IN ('TRAVEL', 'DAILY')", name="chk_reimbursement_type"
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'SUBMITTED', 'CANCELLED')", name="chk_reimbursement_status"
        ),
        CheckConstraint("total_amount >= 0", name="chk_reimbursement_amount"),
        Index("idx_applicant_status", "applicant_id", "status"),
        Index("idx_trip", "trip_source", "trip_id"),
    )


class ReimbursementExpenseModel(Base):
    """费用明细（聚合内实体）的持久化映射。"""

    __tablename__ = "reimbursement_expense"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("reimbursement_order.id"), nullable=False
    )
    expense_type: Mapped[str] = mapped_column(String(32), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=3), nullable=False, server_default=text("CURRENT_TIMESTAMP(3)")
    )

    order: Mapped[ReimbursementOrderModel] = relationship(back_populates="expenses")

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_expense_amount"),
        Index("idx_order", "order_id"),
    )
