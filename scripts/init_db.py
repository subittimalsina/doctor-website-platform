from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Base, engine
from app.models import *  # noqa: F401,F403


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")


if __name__ == "__main__":
    main()
