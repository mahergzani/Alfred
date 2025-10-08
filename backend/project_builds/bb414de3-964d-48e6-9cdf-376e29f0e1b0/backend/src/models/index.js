const { Sequelize, DataTypes } = require('sequelize');
const config = require('../config/config'); // Assuming a config file for database settings

const env = process.env.NODE_ENV || 'development';
const dbConfig = config[env];

let sequelize;
if (dbConfig.use_env_variable) {
  sequelize = new Sequelize(process.env[dbConfig.use_env_variable], dbConfig);
} else {
  sequelize = new Sequelize(dbConfig.database, dbConfig.username, dbConfig.password, dbConfig);
}

const db = {};

db.sequelize = sequelize;
db.Sequelize = Sequelize;

// --- Model Definitions ---

// User Model
db.User = sequelize.define('User', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  username: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      is: /^[a-zA-Z0-9_]{3,20}$/i, // Alphanumeric and underscore, 3-20 chars
      notNull: { msg: 'Username cannot be null' },
      notEmpty: { msg: 'Username cannot be empty' }
    }
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      isEmail: true,
      notNull: { msg: 'Email cannot be null' },
      notEmpty: { msg: 'Email cannot be empty' }
    }
  },
  passwordHash: { // Store hashed password, never plain text
    type: DataTypes.STRING,
    allowNull: false,
    validate: {
      notNull: { msg: 'Password cannot be null' },
      notEmpty: { msg: 'Password cannot be empty' }
    }
  },
  firstName: {
    type: DataTypes.STRING,
    allowNull: true,
    validate: {
      isAlpha: true,
      len: [1, 50]
    }
  },
  lastName: {
    type: DataTypes.STRING,
    allowNull: true,
    validate: {
      isAlpha: true,
      len: [1, 50]
    }
  },
  dateOfBirth: {
    type: DataTypes.DATEONLY,
    allowNull: true,
    validate: {
      isBefore: {
        args: new Date().toISOString().split('T')[0], // Ensure date is not in the future
        msg: 'Date of birth cannot be in the future.'
      }
    }
  },
  gender: {
    type: DataTypes.ENUM('male', 'female', 'non-binary', 'prefer not to say'),
    allowNull: true
  },
  heightCm: {
    type: DataTypes.INTEGER,
    allowNull: true,
    validate: {
      min: 50, // Realistic minimum height
      max: 300 // Realistic maximum height
    }
  },
  weightKg: {
    type: DataTypes.FLOAT,
    allowNull: true,
    validate: {
      min: 20, // Realistic minimum weight
      max: 600 // Realistic maximum weight
    }
  },
  profilePictureUrl: {
    type: DataTypes.STRING,
    allowNull: true,
    validate: {
      isUrl: true
    }
  }
}, {
  tableName: 'users',
  timestamps: true, // `createdAt` and `updatedAt`
  indexes: [
    {
      fields: ['email'],
      unique: true
    },
    {
      fields: ['username'],
      unique: true
    }
  ]
});

// Exercise Model
db.Exercise = sequelize.define('Exercise', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      notNull: { msg: 'Exercise name cannot be null' },
      notEmpty: { msg: 'Exercise name cannot be empty' }
    }
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  muscleGroup: {
    type: DataTypes.STRING,
    allowNull: true // e.g., 'chest', 'back', 'legs', 'shoulders', 'arms', 'core'
  },
  equipment: {
    type: DataTypes.STRING,
    allowNull: true // e.g., 'dumbbell', 'barbell', 'machine', 'bodyweight'
  },
  difficulty: {
    type: DataTypes.ENUM('beginner', 'intermediate', 'advanced'),
    allowNull: true
  },
  isCustom: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    allowNull: false
  },
  // If isCustom is true, this field would link to the user who created it
  createdByUserId: {
    type: DataTypes.UUID,
    allowNull: true, // Null for pre-defined exercises
    references: {
      model: 'users',
      key: 'id'
    }
  }
}, {
  tableName: 'exercises',
  timestamps: true
});

// WorkoutPlan Model
db.WorkoutPlan = sequelize.define('WorkoutPlan', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
    validate: {
      notNull: { msg: 'Workout plan name cannot be null' },
      notEmpty: { msg: 'Workout plan name cannot be empty' }
    }
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  userId: { // Owner of the workout plan
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  isPublic: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    allowNull: false
  }
}, {
  tableName: 'workout_plans',
  timestamps: true
});

// WorkoutPlanExercise (Junction table for WorkoutPlan <-> Exercise)
db.WorkoutPlanExercise = sequelize.define('WorkoutPlanExercise', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  workoutPlanId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'workout_plans',
      key: 'id'
    }
  },
  exerciseId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'exercises',
      key: 'id'
    }
  },
  sets: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 1
    }
  },
  reps: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 1
    }
  },
  weight: {
    type: DataTypes.FLOAT,
    allowNull: true,
    validate: {
      min: 0
    }
  },
  durationMinutes: {
    type: DataTypes.INTEGER,
    allowNull: true,
    validate: {
      min: 1
    }
  },
  order: { // Order of exercise within the workout plan
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  }
}, {
  tableName: 'workout_plan_exercises',
  timestamps: true,
  indexes: [
    // Each exercise within a workout plan must have a distinct order.
    {
      fields: ['workoutPlanId', 'order'],
      unique: true // FIX 1: Changed to unique: true as per feedback
    },
    // Prevent adding the same exercise multiple times to the same plan without distinct order/details
    {
      fields: ['workoutPlanId', 'exerciseId'],
      unique: false // Keep this false if an exercise can appear multiple times with different sets/reps (e.g., supersets or different types of sets for same exercise)
    }
  ]
});

// ScheduledWorkout Model
db.ScheduledWorkout = sequelize.define('ScheduledWorkout', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  workoutPlanId: {
    type: DataTypes.UUID,
    allowNull: true, // Can be null if it's an ad-hoc unsaved workout
    references: {
      model: 'workout_plans',
      key: 'id'
    }
  },
  date: {
    type: DataTypes.DATEONLY,
    allowNull: false,
    validate: {
      isAfter: { // Ensure date is not in the far past (e.g., more than 10 years ago)
        args: '2000-01-01',
        msg: 'Date cannot be before 2000-01-01'
      },
      isBefore: { // Ensure date is not in the far future (e.g., more than 1 year from now)
        args: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
        msg: 'Scheduled date cannot be more than 1 year in the future.'
      }
    }
  },
  time: { // Optional time for scheduling
    type: DataTypes.TIME,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('scheduled', 'completed', 'cancelled', 'skipped'),
    defaultValue: 'scheduled',
    allowNull: false
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  }
}, {
  tableName: 'scheduled_workouts',
  timestamps: true,
  indexes: [
    {
      fields: ['userId', 'date'],
      unique: false // A user can schedule multiple workouts on the same day
    }
  ]
});

// CompletedWorkout Model
db.CompletedWorkout = sequelize.define('CompletedWorkout', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  workoutPlanId: {
    type: DataTypes.UUID,
    allowNull: true, // Can be null if it was an ad-hoc workout not based on a plan
    references: {
      model: 'workout_plans',
      key: 'id'
    }
  },
  scheduledWorkoutId: {
    type: DataTypes.UUID,
    allowNull: true, // Links to a ScheduledWorkout if this completion is for one
    references: {
      model: 'scheduled_workouts',
      key: 'id'
    },
    unique: true // A scheduled workout can only be completed once
  },
  date: {
    type: DataTypes.DATEONLY,
    allowNull: false,
    validate: {
      isAfter: { // Ensure date is not too far in the past (e.g., 5 years)
        args: new Date(new Date().setFullYear(new Date().getFullYear() - 5)).toISOString().split('T')[0],
        msg: 'Date cannot be more than 5 years in the past.'
      },
      isBefore: {
        args: new Date().toISOString().split('T')[0], // FIX 3: Simplified date comparison for DATEONLY
        msg: 'Completed workout date cannot be in the future.'
      }
    }
  },
  durationMinutes: {
    type: DataTypes.INTEGER,
    allowNull: true,
    validate: {
      min: 1
    }
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  }
}, {
  tableName: 'completed_workouts',
  timestamps: true,
  indexes: [
    {
      fields: ['userId', 'date'],
      unique: false // A user can complete multiple workouts on the same day
    }
  ]
});

// CompletedExercise (Junction table for CompletedWorkout <-> Exercise, with actual performance data)
db.CompletedExercise = sequelize.define('CompletedExercise', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  completedWorkoutId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'completed_workouts',
      key: 'id'
    }
  },
  exerciseId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'exercises',
      key: 'id'
    }
  },
  setsCompleted: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  repsCompleted: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  weightUsedKg: {
    type: DataTypes.FLOAT,
    allowNull: true,
    validate: {
      min: 0
    }
  },
  durationMinutes: { // For cardio or timed exercises
    type: DataTypes.INTEGER,
    allowNull: true,
    validate: {
      min: 0
    }
  },
  order: { // Order of exercise within the completed workout
    type: DataTypes.INTEGER,
    allowNull: true, // Can be null if order isn't strictly tracked for ad-hoc
    validate: {
      min: 0
    }
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  }
}, {
  tableName: 'completed_exercises',
  timestamps: true,
  indexes: [
    // Each exercise can appear multiple times within a single completed workout (e.g., different sets/weights, or even multiple instances if logging sets individually)
    // If the intention is one entry per *distinct* exercise, then this should be unique: true.
    // Based on common fitness app logging, allowing multiple entries for the same exercise (e.g., if each set is a separate log) is plausible.
    // However, if setsCompleted/repsCompleted/weightUsedKg are intended to be aggregated for one 'instance' of an exercise, then unique: true is better.
    // Given the fields are singular (setsCompleted, repsCompleted), it implies aggregation per exercise instance.
    // Therefore, making this unique to prevent multiple entries for the same exercise within a single completed workout.
    {
      fields: ['completedWorkoutId', 'exerciseId'],
      unique: true // FIX 2: Changed to unique: true as per feedback for distinct exercise entries
    }
  ]
});

// FoodItem Model
db.FoodItem = sequelize.define('FoodItem', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true, // Food items typically have unique names
    validate: {
      notNull: { msg: 'Food item name cannot be null' },
      notEmpty: { msg: 'Food item name cannot be empty' }
    }
  },
  caloriesPer100g: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  proteinPer100g: {
    type: DataTypes.FLOAT,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  carbsPer100g: {
    type: DataTypes.FLOAT,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  fatPer100g: {
    type: DataTypes.FLOAT,
    allowNull: false,
    validate: {
      min: 0
    }
  },
  isCustom: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    allowNull: false
  },
  createdByUserId: {
    type: DataTypes.UUID,
    allowNull: true, // Null for pre-defined food items
    references: {
      model: 'users',
      key: 'id'
    }
  }
}, {
  tableName: 'food_items',
  timestamps: true
});

// LoggedFood Model
db.LoggedFood = sequelize.define('LoggedFood', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    allowNull: false
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  foodItemId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'food_items',
      key: 'id'
    }
  },
  date: {
    type: DataTypes.DATEONLY,
    allowNull: false,
    validate: {
      isAfter: { // Ensure date is not too far in the past (e.g., 5 years)
        args: new Date(new Date().setFullYear(new Date().getFullYear() - 5)).toISOString().split('T')[0],
        msg: 'Date cannot be more than 5 years in the past.'
      },
      isBefore: {
        args: new Date().toISOString().split('T')[0], // FIX 3: Simplified date comparison for DATEONLY
        msg: 'Logged food date cannot be in the future.'
      }
    }
  },
  mealType: {
    type: DataTypes.ENUM('breakfast', 'lunch', 'dinner', 'snack', 'other'),
    allowNull: true
  },
  quantityGrams: {
    type: DataTypes.FLOAT,
    allowNull: false,
    validate: {
      min: 0.1 // Minimum quantity, e.g., 0.1g
    }
  }
}, {
  tableName: 'logged_foods',
  timestamps: true,
  indexes: [
    {
      fields: ['userId', 'date', 'foodItemId'],
      unique: false // A user can log the same food multiple times on the same day (e.g., for different meals or multiple servings)
    }
  ]
});


// --- Model Associations ---

// User Associations
db.User.hasMany(db.WorkoutPlan, { foreignKey: 'userId', as: 'workoutPlans' });
db.User.hasMany(db.ScheduledWorkout, { foreignKey: 'userId', as: 'scheduledWorkouts' });
db.User.hasMany(db.CompletedWorkout, { foreignKey: 'userId', as: 'completedWorkouts' });
db.User.hasMany(db.Exercise, { foreignKey: 'createdByUserId', as: 'customExercises' });
db.User.hasMany(db.FoodItem, { foreignKey: 'createdByUserId', as: 'customFoodItems' });
db.User.hasMany(db.LoggedFood, { foreignKey: 'userId', as: 'loggedFoods' });

// Exercise Associations
db.Exercise.belongsTo(db.User, { foreignKey: 'createdByUserId', as: 'createdBy' });
db.Exercise.belongsToMany(db.WorkoutPlan, { through: db.WorkoutPlanExercise, foreignKey: 'exerciseId', as: 'inWorkoutPlans' });
db.Exercise.hasMany(db.WorkoutPlanExercise, { foreignKey: 'exerciseId', as: 'workoutPlanDetails' });
db.Exercise.belongsToMany(db.CompletedWorkout, { through: db.CompletedExercise, foreignKey: 'exerciseId', as: 'inCompletedWorkouts' });
db.Exercise.hasMany(db.CompletedExercise, { foreignKey: 'exerciseId', as: 'completedExerciseDetails' });

// WorkoutPlan Associations
db.WorkoutPlan.belongsTo(db.User, { foreignKey: 'userId', as: 'owner' });
db.WorkoutPlan.belongsToMany(db.Exercise, { through: db.WorkoutPlanExercise, foreignKey: 'workoutPlanId', as: 'exercises' });
db.WorkoutPlan.hasMany(db.WorkoutPlanExercise, { foreignKey: 'workoutPlanId', as: 'planExercises' });
db.WorkoutPlan.hasMany(db.ScheduledWorkout, { foreignKey: 'workoutPlanId', as: 'scheduledInstances' });
db.WorkoutPlan.hasMany(db.CompletedWorkout, { foreignKey: 'workoutPlanId', as: 'completedInstances' });

// WorkoutPlanExercise Associations (junction model)
db.WorkoutPlanExercise.belongsTo(db.WorkoutPlan, { foreignKey: 'workoutPlanId' });
db.WorkoutPlanExercise.belongsTo(db.Exercise, { foreignKey: 'exerciseId' });

// ScheduledWorkout Associations
db.ScheduledWorkout.belongsTo(db.User, { foreignKey: 'userId', as: 'user' });
db.ScheduledWorkout.belongsTo(db.WorkoutPlan, { foreignKey: 'workoutPlanId', as: 'workoutPlan' });
db.ScheduledWorkout.hasOne(db.CompletedWorkout, { foreignKey: 'scheduledWorkoutId', as: 'completionRecord' });

// CompletedWorkout Associations
db.CompletedWorkout.belongsTo(db.User, { foreignKey: 'userId', as: 'user' });
db.CompletedWorkout.belongsTo(db.WorkoutPlan, { foreignKey: 'workoutPlanId', as: 'workoutPlan' });
db.CompletedWorkout.belongsTo(db.ScheduledWorkout, { foreignKey: 'scheduledWorkoutId', as: 'scheduledWorkout' });
db.CompletedWorkout.belongsToMany(db.Exercise, { through: db.CompletedExercise, foreignKey: 'completedWorkoutId', as: 'exercisesPerformed' });
db.CompletedWorkout.hasMany(db.CompletedExercise, { foreignKey: 'completedWorkoutId', as: 'performedExerciseDetails' });

// CompletedExercise Associations (junction model)
db.CompletedExercise.belongsTo(db.CompletedWorkout, { foreignKey: 'completedWorkoutId' });
db.CompletedExercise.belongsTo(db.Exercise, { foreignKey: 'exerciseId' });

// FoodItem Associations
db.FoodItem.belongsTo(db.User, { foreignKey: 'createdByUserId', as: 'createdBy' });
db.FoodItem.hasMany(db.LoggedFood, { foreignKey: 'foodItemId', as: 'loggedEntries' });

// LoggedFood Associations
db.LoggedFood.belongsTo(db.User, { foreignKey: 'userId', as: 'user' });
db.LoggedFood.belongsTo(db.FoodItem, { foreignKey: 'foodItemId', as: 'foodItem' });

module.exports = db;