from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FoodItem(Base):
    """
    Represents a single food item with its detailed nutritional information.
    """
    __tablename__ = 'food_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Serving information
    serving_size_g = Column(Float, nullable=False, default=0.0)
    serving_size_unit = Column(String, nullable=True) # e.g., "cup", "piece", "oz"
    
    # Macronutrients (per serving_size_g)
    calories = Column(Float, nullable=False, default=0.0)
    protein_g = Column(Float, nullable=False, default=0.0)
    carbohydrates_g = Column(Float, nullable=False, default=0.0)
    fat_g = Column(Float, nullable=False, default=0.0)
    
    # Detailed nutritional information (per serving_size_g)
    fiber_g = Column(Float, nullable=False, default=0.0)
    sugar_g = Column(Float, nullable=False, default=0.0)
    saturated_fat_g = Column(Float, nullable=False, default=0.0)
    trans_fat_g = Column(Float, nullable=False, default=0.0)
    cholesterol_mg = Column(Float, nullable=False, default=0.0)
    sodium_mg = Column(Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<FoodItem(id={self.id}, name='{self.name}', calories={self.calories})>"