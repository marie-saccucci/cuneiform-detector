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
import os
import requests

MODEL_URL = "https://huggingface.co/marie-saccucci/cuneiform-segmentation-unet/resolve/main/U_net_weights.pth"
MODEL_PATH = "U_net_weights.pth"

# Download model if not local
if not os.path.exists(MODEL_PATH):
    print("Downloading model weights...")
    response = requests.get(MODEL_URL)
    with open(MODEL_PATH, "wb") as f:
        f.write(response.content)
    print("Model downloaded.")



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = smp.Unet(encoder_name="mobilenet_v2", encoder_weights="imagenet", classes=1, activation=None)
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

transform = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

PATCH_SIZE = 512
OVERLAP = 128  


def split_into_patches(img_np, patch_size=PATCH_SIZE, overlap=OVERLAP):
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


@app.post("/predict/")
async def predict(
    file: UploadFile = File(...),
    threshold: float = Query(0.6, ge=0.3, le=0.9)
):
    image = Image.open(file.file).convert("RGB")
    image_np = np.array(image)
    patches, positions, full_shape = split_into_patches(image_np)
    masks = apply_model_on_patches(patches)
    full_mask = reconstruct_mask(masks, positions, full_shape)

    # Binarisation avec seuil dynamique
    prob_mask = (full_mask * 255).astype(np.uint8)
    pil_mask = Image.fromarray(prob_mask)

    buf = io.BytesIO()
    pil_mask.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

