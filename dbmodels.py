from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# establish database classes
class Base(DeclarativeBase):
    pass

class Robot(Base):
    __tablename__ = "robots"
    id: Mapped[int] = mapped_column(primary_key=True)
    robot_key: Mapped[str]
    robot: Mapped[str]
    year_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))
    type: Mapped[str] = mapped_column(nullable=True)
    UniqueConstraint("robot", "year_id", name="uniq1")

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    robot_id: Mapped[str] = mapped_column(ForeignKey("robots.id"))
    #builder: Mapped[str]
    team: Mapped[str]
    members: Mapped[str]
    hometown: Mapped[str]

class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[int] = mapped_column(unique=True)
    year: Mapped[int] = mapped_column(unique=True)

class Stat(Base):
    __tablename__ = "stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    robot_id: Mapped[int] = mapped_column(ForeignKey("robots.id"))
    matches: Mapped[str]
    wins: Mapped[str] 
    losses: Mapped[str]
    knockouts: Mapped[str]
    avg_ko_time: Mapped[str]
    knocked_out: Mapped[str]
    judged_win: Mapped[str]