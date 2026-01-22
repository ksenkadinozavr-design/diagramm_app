from __future__ import annotations

from collections.abc import Iterable


def classify_text(lines: Iterable[str]) -> str:
    content = " ".join(line.strip().lower() for line in lines if line.strip())
    if not content:
        return "activity"

    if any(keyword in content for keyword in ("класс", "атрибут", "поле", "метод")):
        return "uml_class"
    if any(keyword in content for keyword in ("актер", "use case", "сценарий")):
        return "uml_use_case"
    if any(keyword in content for keyword in ("вход", "выход", "механизм", "контроль")):
        return "idef0"
    if any(keyword in content for keyword in ("данные", "хранилище", "dfd")):
        return "dfd"
    if any(keyword in content for keyword in ("если", "иначе", "шаг", "после")):
        return "activity"
    return "flowchart"
