# Can the Price of a Diamond Be Determined Based Upon Its Features?

The main question of this project is asking about whether the price of a diamond can be predicted based on it's carat weight, cut, color, and clarity.

## Dataset and Data Cleaning

**Source:** [Kaggle Diamonds Dataset](https://www.kaggle.com/datasets/shivam2503/diamonds)

The dataset was chosen because it has 53,940 diamonds with a variety of features that can be used to answer the research question.

The data was cleaned as such
    -Dropped a leftover index column from the CSV export
    -Removed 23 rows with impossible dimensions in the x y and z values
    -Set Cut, Color and Clarity as ordered categoricals so plots can follow with this order rather than alphabetically

## Visualizations

### 1. Carat vs Price by Cut Quality
![Carat vs Price by Cut](assets/carat_vs_price_by_cut_quality.png)

The price rises with the carat in a non linear fashion with there being a lot of clustering around the 1.0, 1.5 and 2.0 carat weights. The Cut quality is fairly mixed throught the price levels which shows that cut by itself does not indicate the differences in price

### 2. Price Distribution by Clarity Grade
![Price by Clarity](assets/price_by_clarity.png)

The median price decreases as clarity improves, which is because the lower clarity stones tend to be larger higher carat pieces. This shows that clarity and carat are tied together when trying to determine the price of the Diamond.

### 3. Interactive: Carat vs. Price, Animated by Color Grade
[Interactive Visualization](assets/carat_price_interactive.html)

Going through the color grades (J→D) shows the same non-linear carat-price relationship holds throughout, reinforcing carat as the dominant price
driver regardless of color. But it also cannot be proven that just carat alone is enought to determine the price

## Conclusion

Yes, price can reasonably be estimated from a diamond's features, but no single feature is enough to determine it fully. Even though Carat is the strongest feature in terms of estimating the price, it relies on the cut, color and clarity to support it. 

## Setup and Running the Project
1. Create the virtual enviornment and install the dependencies
    pip install -r requirements.txt
2. Generate the plots
    python visualization.py
3. Run the dashboard
    python dashboard.py
    Click on the url

