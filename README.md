# Crop Disease Detection and Recommendation System

## Overview

The **Crop Disease Detection and Recommendation System** is an innovative project designed to assist farmers in identifying crop diseases and providing personalized recommendations for crop and fertilizer selection. By leveraging advanced machine learning algorithms and deep learning techniques, this system aims to enhance agricultural productivity and sustainability.

## Features

- **Disease Detection:** Utilizes Convolutional Neural Networks (CNNs) to analyze crop images and accurately identify diseases.
- **Crop Recommendation:** Employs Random Forest and Naive Bayes algorithms to suggest suitable crops based on soil nutrient levels and climate conditions.
- **Fertilizer Recommendation:** Provides tailored fertilizer recommendations to optimize soil fertility and improve crop yields.

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Django (Python)
- **Machine Learning:** Python, TensorFlow, scikit-learn
- **Database:** SQLite (or any preferred database supported by Django)
- **Tools and Libraries:** CNN for image processing, Pandas and NumPy for data manipulation, Matplotlib for data visualization

## Installation

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/Sampreeth-DS/Crop-Disease-Detection-and-Recommendation-System.git
   cd crop-disease-detection
2. **Create a Virtual Environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
3. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
4. **Run Migrations:**
   ```sh
   python manage.py migrate
5. **Start the Server:**
   ```sh
   python manage.py runserver

## Usage

1. **User Authentication:** Sign up or log in to access the system.
2. **Disease Detection:** Upload images of crop leaves to detect diseases.
3. **Crop Recommendation:** Input soil nutrient levels and climate conditions to receive crop recommendations.
4. **Fertilizer Recommendation:** Enter soil nutrient values and desired crops to get tailored fertilizer advice.

## Dataset

The system uses a curated dataset containing thousands of annotated images representing various crop diseases, including but not limited to apple, corn, grape, potato, and tomato. The dataset is collected from diverse agricultural settings to ensure a comprehensive representation of different crop diseases. Additionally, agronomic data related to soil composition, nutrient levels, and climate conditions is used for crop and fertilizer recommendations, ensuring the accuracy and relevance of the insights provided.

## Algorithms

1. **Convolutional Neural Network (CNN):** 
   - Used for image classification to detect crop diseases. The CNN processes the input images, extracts relevant features, and classifies the images as healthy or diseased with high accuracy.

2. **Random Forest Classifier:** 
   - Utilized for recommending suitable crops based on input parameters such as soil nutrient levels and environmental conditions. This ensemble learning method builds multiple decision trees and merges them for a more accurate and stable prediction.

3. **Naive Bayes:** 
   - Used alongside Random Forest for crop recommendation due to its effectiveness in handling categorical data and providing high accuracy in predicting suitable crops based on the user's input data.
