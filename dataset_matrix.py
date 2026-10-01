1

import sqlite3
from pathlib import Path

# Folder where this Python file is located
BASE_DIR = Path(__file__).resolve().parent

# Save database in the same folder
DB_NAME = BASE_DIR / "roof_dataset_matrix.db"


# -----------------------------
# DATABASE SETUP
# -----------------------------
def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT,
            image_count INTEGER,
            damage_types TEXT,
            roof_materials TEXT,
            damaged_undamaged_balance TEXT,
            annotation_type TEXT,
            resolution TEXT,
            license TEXT,
            notes TEXT,

            scope_match INTEGER,
            drone_similarity INTEGER,
            annotation_quality INTEGER,
            image_quality INTEGER,
            class_balance INTEGER,

            total_score REAL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# SCORE CALCULATION
# -----------------------------
def calculate_score(
    scope_match,
    drone_similarity,
    annotation_quality,
    image_quality,
    class_balance
):
    """
    Weighted score out of 5.

    Weights:
    Scope Match = 30%
    Drone Similarity = 25%
    Annotation Quality = 20%
    Image Quality = 15%
    Class Balance = 10%
    """

    score = (
        scope_match * 0.30 +
        drone_similarity * 0.25 +
        annotation_quality * 0.20 +
        image_quality * 0.15 +
        class_balance * 0.10
    )

    return round(score, 2)


# -----------------------------
# ADD DATASET
# -----------------------------
def add_dataset():
    print("\n--- Add New Dataset ---")

    name = input("Dataset name: ")
    source = input("Source (Kaggle, Roboflow, Hugging Face, etc.): ")

    try:
        image_count = int(input("Number of images: "))
    except ValueError:
        image_count = 0

    damage_types = input("Damage types: ")
    roof_materials = input("Roof materials: ")
    damaged_undamaged_balance = input("Damaged / undamaged balance: ")
    annotation_type = input("Annotation type: ")
    resolution = input("Resolution: ")
    license_name = input("License: ")
    notes = input("Notes: ")

    print("\nScore each category from 1 to 5")
    print("1 = poor match")
    print("5 = excellent match\n")

    scope_match = get_score("Scope match")
    drone_similarity = get_score("Drone similarity")
    annotation_quality = get_score("Annotation quality")
    image_quality = get_score("Image quality")
    class_balance = get_score("Class balance")

    total_score = calculate_score(
        scope_match,
        drone_similarity,
        annotation_quality,
        image_quality,
        class_balance
    )

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO datasets (
            name,
            source,
            image_count,
            damage_types,
            roof_materials,
            damaged_undamaged_balance,
            annotation_type,
            resolution,
            license,
            notes,
            scope_match,
            drone_similarity,
            annotation_quality,
            image_quality,
            class_balance,
            total_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        source,
        image_count,
        damage_types,
        roof_materials,
        damaged_undamaged_balance,
        annotation_type,
        resolution,
        license_name,
        notes,
        scope_match,
        drone_similarity,
        annotation_quality,
        image_quality,
        class_balance,
        total_score
    ))

    conn.commit()
    conn.close()

    print(f"\nDataset saved.")
    print(f"Total score: {total_score}/5")


# -----------------------------
# SAFE SCORE INPUT
# -----------------------------
def get_score(category):
    while True:
        try:
            score = int(input(f"{category} (1-5): "))

            if 1 <= score <= 5:
                return score

            print("Enter a number from 1 to 5.")

        except ValueError:
            print("Enter a valid number.")


# -----------------------------
# VIEW ALL DATASETS
# -----------------------------
def view_datasets():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            source,
            image_count,
            damage_types,
            roof_materials,
            annotation_type,
            total_score
        FROM datasets
        ORDER BY total_score DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nNo datasets saved yet.")
        return

    print("\n--- Dataset Comparison Matrix ---\n")

    print(
        f"{'Rank':<6}"
        f"{'ID':<5}"
        f"{'Dataset':<30}"
        f"{'Source':<15}"
        f"{'Images':<10}"
        f"{'Score':<10}"
    )

    print("-" * 80)

    for rank, row in enumerate(rows, start=1):
        dataset_id, name, source, image_count, damage_types, roof_materials, annotation_type, total_score = row

        print(
            f"{rank:<6}"
            f"{dataset_id:<5}"
            f"{name[:28]:<30}"
            f"{source[:13]:<15}"
            f"{image_count:<10}"
            f"{total_score:<10}"
        )


# -----------------------------
# VIEW FULL DATASET DETAILS
# -----------------------------
def view_dataset_details():
    dataset_id = input("\nEnter dataset ID: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM datasets
        WHERE id = ?
    """, (dataset_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        print("Dataset not found.")
        return

    columns = [
        "ID",
        "Name",
        "Source",
        "Image Count",
        "Damage Types",
        "Roof Materials",
        "Damaged / Undamaged Balance",
        "Annotation Type",
        "Resolution",
        "License",
        "Notes",
        "Scope Match",
        "Drone Similarity",
        "Annotation Quality",
        "Image Quality",
        "Class Balance",
        "Total Score"
    ]

    print("\n--- Dataset Details ---\n")

    for column, value in zip(columns, row):
        print(f"{column}: {value}")


# -----------------------------
# DELETE DATASET
# -----------------------------
def delete_dataset():
    dataset_id = input("\nEnter dataset ID to delete: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM datasets WHERE id = ?",
        (dataset_id,)
    )

    conn.commit()
    conn.close()

    print("Dataset deleted.")


# -----------------------------
# UPDATE DATASET SCORE
# -----------------------------
def update_scores():
    dataset_id = input("\nEnter dataset ID to update scores: ")

    print("\nEnter new scores from 1 to 5")

    scope_match = get_score("Scope match")
    drone_similarity = get_score("Drone similarity")
    annotation_quality = get_score("Annotation quality")
    image_quality = get_score("Image quality")
    class_balance = get_score("Class balance")

    total_score = calculate_score(
        scope_match,
        drone_similarity,
        annotation_quality,
        image_quality,
        class_balance
    )

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE datasets
        SET
            scope_match = ?,
            drone_similarity = ?,
            annotation_quality = ?,
            image_quality = ?,
            class_balance = ?,
            total_score = ?
        WHERE id = ?
    """, (
        scope_match,
        drone_similarity,
        annotation_quality,
        image_quality,
        class_balance,
        total_score,
        dataset_id
    ))

    conn.commit()
    conn.close()

    print(f"Scores updated.")
    print(f"New score: {total_score}/5")


# -----------------------------
# MAIN MENU
# -----------------------------
def main():
    create_database()

    while True:
        print("\n==============================")
        print(" Roof Dataset Comparison Tool ")
        print("==============================")
        print("1. Add dataset")
        print("2. View ranked datasets")
        print("3. View dataset details")
        print("4. Update dataset scores")
        print("5. Delete dataset")
        print("6. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            add_dataset()

        elif choice == "2":
            view_datasets()

        elif choice == "3":
            view_dataset_details()

        elif choice == "4":
            update_scores()

        elif choice == "5":
            delete_dataset()

        elif choice == "6":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()