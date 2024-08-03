import streamlit as st
import cv2
import torch
import numpy as np
from huggingface_hub import hf_hub_download
from PIL import Image

# Loading our custom YOLO model
model_path = hf_hub_download(repo_id="Nhyira-EM/Objectdetection", filename="Imgdetec.pt")
with open(model_path, 'rb') as f:
    final_model = torch.load(f)

def run_inference_and_annotate(image, model, confidence_threshold=0.5):
    # Convert BGR to RGB for inference
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Set the model to evaluation mode
    model.eval()

    # Run inference with no gradient calculation
    with torch.no_grad():
        results = model(image_rgb)

    # Process results
    annotated_boxes = []
    for result in results:
        boxes = result.boxes  # Extract bounding boxes and scores
        for box in boxes:
            bbox = box.xyxy[0].tolist()  # Convert bbox tensor to list
            score = box.conf.item()
            class_id = int(box.cls.item())

            label = 'other'
            if score >= confidence_threshold:
                if class_id == 0:
                    label = 'metal'
                elif class_id == 1:
                    label = 'plastic'

            annotated_boxes.append((bbox, label, score))

    # Annotate the image
    for (bbox, label, score) in annotated_boxes:
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f'{label} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return image

# Streamlit application
st.title("Object Detection with YOLO")
st.write("Group 40: Francine Arthur & Emmanuel Nhyira Freduah-Agyemang")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Open and process the image
    image = Image.open(uploaded_file)
    image = np.array(image)  # Convert to numpy array

    # Run inference and annotate the image
    annotated_image = run_inference_and_annotate(image, final_model)

    # Convert annotated image back to PIL format for Streamlit
    annotated_image_pil = Image.fromarray(annotated_image)

    # Display the image
    st.image(annotated_image_pil, caption='Annotated Image', use_column_width=True)