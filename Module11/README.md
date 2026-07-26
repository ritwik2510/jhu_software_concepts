Module 11: MLOps Tracking for KMeans Clustering

This folder contains kmeans_mlops_pipeline.py, which extends the Module 9
KMeans clustering pipeline with MLflow experiment tracking.

Setup
1. Install dependencies: pip install -r requirements.txt
2. Start the MLflow tracking server: mlflow server --host 127.0.0.1 --port 8080
3. In a separate terminal, run: python kmeans_mlops_pipeline.py

What gets tracked
A KMeans model is trained on the 2-component PCA-reduced TF-IDF matrix of
program names, using the required parameters: max_iter=500, n_clusters=25,
n_init=5, random_state=42. The run logs these parameters, the model's
inertia_ as a metric, and saves the trained model as an artifact registered
under the name "Clustering".

Where to find results
- MLflow UI: http://127.0.0.1:8080
- Run details and parameters: Experiments > Default > run name
- Registered model: Models > Clustering
- Screenshots: cluster_run.png, cluster_details.png, model_details.png