import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import relationship

# Assuming Base is defined in src/database.py
from src.database import Base


# Define MealType enum for meal classification
class MealType(enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class MealEntry(Base):
    __tablename__ = "meal_entries"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to the User model, establishing a many-to-one relationship.
    # ondelete="CASCADE" ensures that if a user is deleted, their meal entries are also removed.
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Timestamp of when the meal was consumed. Defaults to UTC now.
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Type of meal (e.g., breakfast, lunch). Uses an Enum for controlled values.
    meal_type = Column(Enum(MealType), default=MealType.OTHER, nullable=False)

    # --- Fields for referencing an existing FoodItem ---
    # Optional foreign key to the FoodItem model.
    # If set, this entry refers to a specific FoodItem from the database.
    # ondelete="SET NULL" means if a FoodItem is deleted, entries referencing it
    # will become "manual" entries (food_item_id becomes NULL) rather than being deleted.
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True)

    # Quantity of the referenced food_item, typically in grams.
    # Used to calculate total nutrition from a FoodItem's per-100g data.
    quantity_grams = Column(Numeric(10, 2), nullable=True)

    # --- Fields for manual or parsed entry ---
    # These fields are used if food_item_id is NULL, or for additional notes.
    # A general description for manual entries (e.g., "Homemade chicken salad sandwich").
    description = Column(String(255), nullable=True)

    # Manual nutritional data. These are used when no FoodItem is referenced
    # or to override/supplement FoodItem data (application logic dependent).
    # Numeric(10, 2) provides precision for nutritional values.
    manual_calories = Column(Numeric(10, 2), nullable=True)
    manual_protein_grams = Column(Numeric(10, 2), nullable=True)
    manual_carbohydrates_grams = Column(Numeric(10, 2), nullable=True)
    manual_fat_grams = Column(Numeric(10, 2), nullable=True)
    manual_fiber_grams = Column(Numeric(10, 2), nullable=True)
    manual_sugar_grams = Column(Numeric(10, 2), nullable=True)
    manual_sodium_mg = Column(Numeric(10, 2), nullable=True)

    # --- Relationships ---
    # Defines the relationship with the User model.
    # "User" refers to the class name of the User model.
    # back_populates creates a bidirectional relationship.
    user = relationship("User", back_populates="meal_entries")

    # Defines the relationship with the FoodItem model.
    # "FoodItem" refers to the class name of the FoodItem model.
    food_item = relationship("FoodItem", back_populates="meal_entries")

    def __repr__(self):
        """
        Provides a human-readable representation of a MealEntry object for debugging.
        Prioritizes FoodItem name if available, otherwise uses description.
        """
        food_representation = "N/A"
        if self.food_item:
            # If a FoodItem is linked, show its name and quantity.
            food_representation = f"{self.food_item.name} ({self.quantity_grams or 'N/A'}g)"
        elif self.description:
            # If no FoodItem, but a description is present, use that.
            food_representation = self.description
        else:
            # Fallback for manual entry without description.
            food_representation = "Manual Entry (No description)"

        return (
            f"<MealEntry(id={self.id}, user_id={self.user_id}, "
            f"timestamp='{self.timestamp.isoformat()}', meal_type='{self.meal_type.value}', "
            f"food='{food_representation}', calories={self.manual_calories or 'N/A'})>"
        )