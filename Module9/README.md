# Module 9: Grad Café K-Means Clustering

This project implements a machine learning pipeline to cluster academic program data from the Grad Café dataset. It uses TF-IDF vectorization, PCA for dimensionality reduction, and K-Means clustering to identify academic program groups.

## Contents
- `kmeans.py`: The main Python script that performs data cleaning, clustering analysis, and visualization generation.
- `initial_cluster.png`: Visualization of the initial 50-cluster grouping.
- `elbow.png`: The elbow method plot used to determine the optimal cluster count.
- `clustered_dataFrame.png`: A sample of the program data with assigned cluster labels.
- `computer_science.png`: Box plot comparison of GRE scores for the Computer Science cluster.
- `philosophy.png`: Box plot comparison of GRE scores for the Philosophy cluster.

## Prerequisites
The following Python libraries are required:
- pandas
- matplotlib
- scikit-learn

## How to Run
1. Ensure your dataset (`cleaned_gradcafe.json`) is located in the same directory as `kmeans.py`.
2. Install the required dependencies:
   ```bash
   pip install pandas matplotlib scikit