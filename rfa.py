import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Function to generate random data for a person
def generate_random_data():
    time = np.random.rand(5)
    angular_velocity = np.random.randint(0, 21, size=5)
    angles_of_movement = np.random.randint(0, 141, size=5)
    return {'time': time, 'angular_velocity': angular_velocity, 'angles_of_movement': angles_of_movement}

# Set the minimum and maximum angles
min_angle = 0
max_angle = 140

# Create DataFrames for 100 persons
persons_data = [generate_random_data() for _ in range(100)]
dfs = [pd.DataFrame(person_data) for person_data in persons_data]

# Calculate average angles for each person
avg_angles = [(df['angles_of_movement'].max() + df['angles_of_movement'].min()) / 2 for df in dfs]

# Add labels for each person (1 for normal, 0 for abnormal based on the average angle)
labels = [1 if avg_angle >= 60 else 0 for avg_angle in avg_angles]

# Concatenate DataFrames
df_combined = pd.concat([df.assign(label=label) for df, label in zip(dfs, labels)], ignore_index=True)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df_combined[['time', 'angular_velocity', 'angles_of_movement']], df_combined['label'], test_size=0.2, random_state=12)

# Create a Random Forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the Random Forest model
rf_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_classifier.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

# Output for each person
for i in range(100):
    print(f"Data for Person {i + 1}:")
    print(dfs[i])

    output = 'Normal' if avg_angles[i] >= 60 else 'Abnormal'
    print(f"Condition: {output}\n")
