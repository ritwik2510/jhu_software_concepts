# Module 9: Grad Café K-Means Clustering

This project implements a machine learning pipeline to cluster academic program data from the Grad Café dataset. It uses TF-IDF vectorization, PCA for dimensionality reduction, and K-Means clustering to identify groups of similar academic programs.

The analysis focuses on identifying clusters associated with specific academic programs, particularly Computer Science and Philosophy, and examining the GRE V score distributions within those clusters.

## Contents

- `kmeans.py`: Main Python script that performs TF-IDF vectorization, PCA dimensionality reduction, K-Means clustering, and visualization generation.
- `requirements.txt`: Python dependencies required to run the analysis.
- `initial_cluster.png`: Visualization of the initial 50-cluster grouping.
- `elbow.png`: Elbow-method plot showing K-Means inertia across different cluster counts.
- `clustered_data.csv`: Final dataset containing the assigned `final_cluster` labels.
- `clustered_dataFrame.png`: Preview of program, university, and cluster assignments.
- `computer_science.png`: GRE V distribution for the identified Computer Science cluster.
- `philosophy.png`: GRE V distribution for the identified Philosophy cluster.

## Methodology

### 1. TF-IDF Vectorization

The `Program` field is converted into numerical features using Term Frequency-Inverse Document Frequency (TF-IDF).

TF-IDF was selected because academic program names are text data, and TF-IDF allows programs containing similar terms to receive similar numerical representations.

For example, programs containing terms such as:

- Computer Science
- Computer Engineering
- Data Science
- Philosophy

can be represented based on the words that occur within their program names.

### 2. PCA Dimensionality Reduction

Principal Component Analysis (PCA) is used to reduce the high-dimensional TF-IDF representation into a smaller numerical feature space.

An initial two-component PCA transformation is used to visualize the initial clustering.

A second PCA transformation using 85 components is used for the final K-Means analysis.

### 3. Initial K-Means Clustering

An initial K-Means model is created using 50 clusters.

The purpose of this initial clustering is to visualize how the academic programs naturally separate into groups.

The initial clustering uses:

- 50 clusters
- `random_state=42`
- `n_init=10`
- `max_iter=100`

The cluster centers are also displayed in the initial clustering visualization.

### 4. Elbow Analysis

The elbow method is used to examine K-Means inertia for cluster counts from 1 through 100.

The resulting `elbow.png` visualization shows how within-cluster variation changes as the number of clusters increases.

The final analysis uses 85 clusters as the selected clustering configuration.

### 5. Final K-Means Clustering

The final K-Means model uses:

- 85 clusters
- `random_state=42`
- `n_init=10`
- `max_iter=100`

The resulting cluster labels are stored in the `final_cluster` column.

The final labeled dataset is saved as:

```text
clustered_data.csv