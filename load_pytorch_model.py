import torch
from torchvision import models, transforms
from PIL import Image
import os

# Path to your image
image_path = 'your_image.jpg'  # Replace with your actual image filename

# Check if image exists
if not os.path.exists(image_path):
    print(f"Image file not found at: {image_path}")
    exit()

# Load a pre-trained ResNet18 model
model = models.resnet18(pretrained=True)
model.eval()  # Set the model to evaluation mode

# Define the image transformation pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to expected input size
    transforms.ToTensor(),          # Convert image to PyTorch tensor
    transforms.Normalize(           # Normalize using ImageNet mean/std
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])

# Load and preprocess the image
image = Image.open(image_path).convert('RGB')  # Ensure 3 channels
input_tensor = transform(image).unsqueeze(0)    # Add batch dimension

# Run the image through the model
with torch.no_grad():
    output = model(input_tensor)
    predicted_class = output.argmax(dim=1).item()

print("✅ Inference complete.")
print("Predicted class index:", predicted_class)
