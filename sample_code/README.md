# Breast Cancer Prediction with Ensembled Machine Learning 

## Project Overview
This project focuses on predicting breast cancer diagnoses using machine learning algorithms. By analyzing features from the Wisconsin Breast Cancer dataset, our models can classify tumors as benign or malignant with high accuracy. The project implements multiple machine learning approaches and culminates in a hybrid model that achieves superior performance through an ensemble technique.

## Dataset Description
The Wisconsin Breast Cancer dataset contains 569 instances with 32 features computed from digitized images of fine needle aspirates (FNA) of breast masses. The features characterize cell nuclei properties visible in the images.

Key features include:
- **Radius**: Mean of distances from center to points on the perimeter
- **Texture**: Standard deviation of gray-scale values
- **Perimeter**: Perimeter of the cell nucleus
- **Area**: Area of the cell nucleus
- **Smoothness**: Local variation in radius lengths
- **Compactness**: Perimeter² / area - 1.0
- **Concavity**: Severity of concave portions of the contour
- **Concave points**: Number of concave portions of the contour
- **Symmetry**: Symmetry of cell nuclei
- **Fractal dimension**: "Coastline approximation" - 1

The dataset provides these measurements as mean, standard error, and "worst" (mean of the three largest values) for each feature, resulting in 30 feature values per instance. The target variable is the diagnosis (M = malignant, B = benign).

## Data Preprocessing
The data preparation pipeline includes:
1. **Data Exploration**: Initial visualization and statistical analysis of the data
2. **Feature Extraction**: Working with the most relevant features 
3. **Data Transformation**: Converting categorical diagnosis values to binary (1 for malignant, 0 for benign)
4. **Train-Test Split**: Dividing the dataset into training (75%) and testing (25%) sets
5. **Type Conversion**: Converting to appropriate numerical types for model compatibility

## Machine Learning Models Implemented

### 1. Logistic Regression
A fundamental classification algorithm that models the probability of the tumor being malignant.
- Implementation: `LogisticRegression(random_state=0, class_weight="balanced")`
- Performance: 93% accuracy on test data
- Strengths: Good baseline model with interpretable results

### 2. Gradient Boosting Classifier
An ensemble technique that builds trees sequentially, with each tree correcting errors made by previous ones.
- Implementation: `GradientBoostingClassifier(random_state=0)`
- Performance: 96% accuracy on test data
- Strengths: Handles complex relationships, resistant to overfitting

### 3. Neural Network (Multi-layer Perceptron)
A deep learning approach that can model complex non-linear relationships.
- Implementation: `MLPClassifier(hidden_layer_sizes=(30, 30, 30), activation="logistic", random_state=0)`
- Architecture: 3 hidden layers with 30 neurons each
- Performance: 92% accuracy on test data
- Strengths: Captures complex patterns in the data

### 4. Hybrid Model (Ensemble Voting Classifier)
Combines the strengths of all three models through a weighted soft voting mechanism.
- Implementation: `EnsembleVoteClassifier(clfs=clfs, voting="soft", weights=[0.7, 1.2, 0.5])`
- Performance: 97% accuracy on test data
- Strengths: Leverages different learning algorithms to improve overall prediction accuracy

## Performance Evaluation
Each model was evaluated using:
1. **Accuracy Score**: Proportion of correct predictions among total predictions
2. **Confusion Matrix**: Visual representation of true vs. predicted values, normalized to show the proportion of correct and incorrect classifications

The hybrid model showed the best performance with 97% accuracy, demonstrating the value of ensemble methods in medical diagnostics.

## Visualization and Analysis
The project includes comprehensive visualization of:
- Model performance metrics
- Confusion matrices for each model
- Feature importance analysis
- Comparison of model predictions

## Implementation Details

### Dependencies
- Python 3.6+
- NumPy
- Pandas
- Scikit-learn
- Matplotlib
- mlxtend (for ensemble voting classifier)

### Code Structure
The implementation follows a structured workflow:
1. **Data Loading and Preprocessing**
   ```python
   Data = pd.read_csv("data.csv")
   Data.loc[Data["diagnosis"] == "M", "diagnosis"] = 1  # Cancer -> yes
   Data.loc[Data["diagnosis"] == "B", "diagnosis"] = 0  # Cancer -> no
   ```

2. **Model Training**
   ```python
   model_lrc = LogisticRegression(random_state=0, class_weight="balanced").fit(train[features], train[target])
   model_gbc = GradientBoostingClassifier(random_state=0).fit(train[features], train[target])
   model_nnc = MLPClassifier(hidden_layer_sizes=(30, 30, 30), activation="logistic", random_state=0).fit(train[features], train[target])
   ```

3. **Hybrid Model Construction**
   ```python
   clfs = [model_lrc, model_gbc, model_nnc]
   model_clfs = EnsembleVoteClassifier(
       clfs=clfs,
       voting="soft",
       weights=[0.7, 1.2, 0.5]
   ).fit(train[features], train[target])
   ```

4. **Performance Evaluation**
   ```python
   print("HYBRID accuracy score: ", round(accuracy_score(test[target], pred_clfs), 2))
   cm = confusion_matrix(test[target], pred_clfs, normalize="true")
   disp = ConfusionMatrixDisplay(confusion_matrix=cm)
   disp.plot()
   ```

## Results Summary
| Model                   | Accuracy | Key Characteristics                               |
|-------------------------|---------|----------------------------------------------------|
| Logistic Regression     | 93%     | Simple, interpretable baseline                     |
| Gradient Boosting       | 96%     | Strong performance, captures complex relationships |
| Neural Network          | 92%     | Good with non-linear patterns                      |
| Hybrid Ensemble Model   | 97%     | Best overall performance, combines model strengths |

## Clinical Significance
The high accuracy of these models, particularly the hybrid approach, demonstrates potential for:
- Supporting clinical decision-making in breast cancer diagnosis
- Reducing false negatives in cancer screening
- Providing a quantitative second opinion for medical professionals
- Potentially reducing unnecessary biopsies by accurately identifying benign cases

## Limitations and Considerations
- The dataset is relatively small (569 instances), which may limit generalizability
- Real-world implementation would require additional validation on external datasets
- Feature selection could be further optimized
- Model interpretability varies (with logistic regression being most interpretable)

## Future Directions
1. **Model Improvement**:
   - Hyperparameter optimization through grid search
   - Feature selection techniques to identify most important predictors
   - Testing additional algorithms like XGBoost, LightGBM, or deep learning architectures

2. **Validation and Testing**:
   - Cross-validation with different splitting strategies
   - External validation on independent datasets
   - Prospective clinical testing

3. **Explainability**:
   - Implementing SHAP (SHapley Additive exPlanations) or LIME for model interpretability
   - Identifying key features that influence predictions

4. **Deployment Considerations**:
   - Creating a user-friendly interface for clinical use
   - Model monitoring and maintenance strategies
   - Integration with existing healthcare systems

## Conclusion
This project demonstrates the power of machine learning, particularly ensemble methods, in breast cancer prediction. The hybrid model achieved an impressive 97% accuracy, showing significant potential for supporting clinical diagnostics. Through careful feature analysis and model combination, we've created a robust prediction system that could help improve breast cancer diagnosis accuracy and efficiency.

## References
- Wisconsin Breast Cancer Dataset: UCI Machine Learning Repository
- Scikit-learn Documentation: https://scikit-learn.org/
- mlxtend Documentation: http://rasbt.github.io/mlxtend/
- Breast Cancer Diagnosis using Machine Learning: A systematic literature review

## Acknowledgements
Special thanks to the University of Wisconsin for providing the original dataset and to the open-source community for developing the tools and libraries that made this analysis possible.
