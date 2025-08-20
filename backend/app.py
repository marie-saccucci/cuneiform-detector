from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi import Query
import torch
import numpy as np
from PIL import Image
import io
import cv2
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = smp.Unet(encoder_name="mobilenet_v2", encoder_weights="imagenet", classes=1, activation=None)
model.load_state_dict(torch.load("U_net_weights.pth", map_location="cpu"))
model.eval()

# Define transformations
transform = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

PATCH_SIZE = 512
OVERLAP = 128  # 25% overlap


def split_into_patches(img_np, patch_size=PATCH_SIZE, overlap=OVERLAP):
    """Split the image into overlapping patches."""
    h, w = img_np.shape[:2]
    patches = []
    positions = []

    step = patch_size - overlap
    for y in range(0, h, step):
        for x in range(0, w, step):
            patch = img_np[y:y+patch_size, x:x+patch_size]
            pad_h = patch_size - patch.shape[0]
            pad_w = patch_size - patch.shape[1]

            if pad_h > 0 or pad_w > 0:
                patch = cv2.copyMakeBorder(patch, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=0)

            patches.append(patch)
            positions.append((y, x))

    return patches, positions, (h, w)


def apply_model_on_patches(patches):
    """Apply model on each patch and return probability masks."""
    masks = []
    for patch in patches:
        augmented = transform(image=patch)
        img_tensor = augmented['image'].unsqueeze(0)
        with torch.no_grad():
            out = model(img_tensor)
            pred = torch.sigmoid(out).squeeze().numpy()
        masks.append(pred)
    return masks


def reconstruct_mask(masks, positions, full_shape, patch_size=PATCH_SIZE):
    """Reconstruct full image mask from patches."""
    height, width = full_shape
    full_mask = np.zeros((height, width), dtype=np.float32)
    weight = np.zeros((height, width), dtype=np.float32)

    for mask, (y, x) in zip(masks, positions):
        h = min(patch_size, height - y)
        w = min(patch_size, width - x)
        full_mask[y:y+h, x:x+w] += mask[:h, :w]
        weight[y:y+h, x:x+w] += 1.0

    weight[weight == 0] = 1.0
    return full_mask / weight


def process_image(img_np):
    """Process a single image: split, apply model, reconstruct mask."""
    patches, positions, full_shape = split_into_patches(img_np)
    masks = apply_model_on_patches(patches)
    full_mask = reconstruct_mask(masks, positions, full_shape)
    return full_mask


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    """Predict probability map by combining original and blurred images."""
    image = Image.open(file.file).convert("RGB")
    image_np = np.array(image)

    # Create blurred image
    blurred_image = cv2.GaussianBlur(image_np, (5, 5), sigmaX=1.5)

    # Process original and blurred images in parallel
    with ThreadPoolExecutor() as executor:
        future_original = executor.submit(process_image, image_np)
        future_blurred = executor.submit(process_image, blurred_image)
        mask_original = future_original.result()
        mask_blurred = future_blurred.result()

    # Combine masks (average)
    combined_mask = 0.5 * mask_original + 0.5 * mask_blurred
    combined_mask = (combined_mask * 255).astype(np.uint8)
    pil_mask = Image.fromarray(combined_mask)

    buf = io.BytesIO()
    pil_mask.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
