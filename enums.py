from enum import Enum

class JobTTL(Enum):
    TODAY = 1
    THREE_DAYS = 3
    FIVE_DAYS = 5
    SEVEN_DAYS = 7
    TWO_WEEKS = 14
    ONE_MONTH = 30
    @classmethod
    def convert_enum_in_hours(cls,val):
        map={
            cls.TODAY: 24,
           cls.THREE_DAYS: 72,
                        cls.FIVE_DAYS: 120,
                        cls.SEVEN_DAYS: 168,
                        cls.TWO_WEEKS: 336,
                        cls.ONE_MONTH: 720,

        }
        return map.get(val,168)
    @classmethod
    def get_display_name(cls,val):
        map={
            cls.TODAY: "Astăzi",
                        cls.THREE_DAYS: "Last 3 days",
                        cls.FIVE_DAYS: "Last 5 days",
                        cls.SEVEN_DAYS: "Last week",
                        cls.TWO_WEEKS: "Last two weeks",
                        cls.ONE_MONTH: "Last month",
        }
