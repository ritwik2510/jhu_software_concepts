"""
Module 9: K-Means clustering for Grad Café data.
"""
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def get_cluster_data(df, column_name, keyword):
    """Returns the mode cluster ID for a given keyword."""
    return df[df[column_name].str.contains(keyword, case=False)]['final_cluster'].mode()[0]

def create_boxplot(df, cluster_id, filename):
    """Generates and saves a boxplot for GRE scores."""
    subset = df[df['final_cluster'] == cluster_id]
    plt.figure()


    gre_v = pd.to_numeric(subset['GRE V'], errors='coerce').dropna()
    gre = pd.to_numeric(subset['GRE'], errors='coerce').dropna()


    box = plt.boxplot([gre_v, gre], tick_labels=['GRE V', 'GRE'], patch_artist=True)

    plt.title(f"GRE Scores for Cluster {cluster_id}")
    plt.xlabel("Test Type")
    plt.ylabel("Score (Points, 130-170 Scale)")
    plt.legend([box["boxes"][0]], ["Score Distribution"])
    plt.savefig(filename)
    plt.close()

def save_cluster_preview(df, filename):
    """Saves a 100-row Program/University/cluster table as a PNG."""
    preview = df[['Program', 'University', 'initial_cluster']].head(100)
    fig, axis = plt.subplots(figsize=(10, 22))
    axis.axis('off')
    table = axis.table(cellText=preview.values, colLabels=preview.columns,
                        loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    plt.title("Program / University by Initial Cluster (First 100 Rows)")
    fig.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close(fig)

def run_analysis():
    """Main execution function for clustering."""
    df = pd.read_json('llm_extend_applicant_data_run.jsonl', lines=True)
    df = df.rename(columns={
    'llm-generated-program': 'Program',
    'llm-generated-university': 'University'
    })
    df = df.dropna(subset=['Program'])

    print(f"Number of Entries: {len(df):,}")
    print(f"Number of Program Input Names: {df['Program'].nunique():,}")

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['Program'])
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}, type: {type(tfidf_matrix)}")

    pca_init = PCA(n_components=2)
    reduced = pca_init.fit_transform(tfidf_matrix.toarray())
    print(f"Initial PCA output shape: {reduced.shape}")
    print(pca_init)
    labels = KMeans(n_clusters=50, max_iter=100, n_init=5, random_state=42).fit_predict(reduced)

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='viridis')
    plt.title("Initial Clustering (50 Clusters)")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    handles, _ = scatter.legend_elements()
    plt.legend(handles[:1], ["Cluster assignment (color)"])
    plt.savefig('initial_cluster.png')
    plt.close()

    df['initial_cluster'] = labels
    save_cluster_preview(df, 'clustered_dataFrame.png')


    pca_l = PCA(n_components=85)
    data_l = pca_l.fit_transform(tfidf_matrix.toarray())
    inertia = [KMeans(n_clusters=k, max_iter=100, n_init=5, random_state=42).fit(data_l).inertia_
               for k in range(1, 101)]

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 101), inertia, marker='o', label="Inertia")
    plt.title("Elbow Method")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia (Within-Cluster Sum of Squares)")
    plt.legend()
    plt.savefig('elbow.png')
    plt.close()

    df['final_cluster'] = KMeans(n_clusters=85, max_iter=100, n_init=5,
                                 random_state=42).fit_predict(data_l)

    cs_id = get_cluster_data(df, 'Program', 'Computer Science')
    phil_id = get_cluster_data(df, 'Program', 'Philosophy')

    create_boxplot(df, cs_id, 'computer_science.png')
    create_boxplot(df, phil_id, 'philosophy.png')

if __name__ == "__main__":
    run_analysis()
