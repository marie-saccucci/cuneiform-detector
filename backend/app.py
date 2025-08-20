from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import torch
import numpy as np
from PIL import Image
import io
import cv2
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = smp.Unet(encoder_name="mobilenet_v2", encoder_weights="imagenet", classes=1, activation=None)
model.load_state_dict(torch.load("U_net_weights.pth", map_location="cpu"))
model.eval()

transform = A.Compose([
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])


PATCH_SIZE = 1024
OVERLAP = 256  


def weight_map(h, w):
    y = np.linspace(-1, 1, h)
    x = np.linspace(-1, 1, w)
    xv, yv = np.meshgrid(x, y)
    weight = np.exp(-(xv**2 + yv**2))
    return weight


def split_into_patches(img_np, patch_size=PATCH_SIZE, overlap=OVERLAP):
    h, w = img_np.shape[:2]
    patches = []
    positions = []

    step = patch_size - overlap
    for y in range(0, h, step):
        for x in range(0, w, step):
            patch = img_np[y:min(y+patch_size, h), x:min(x+patch_size, w)]
            patches.append(patch)
            positions.append((y, x))
    return patches, positions, (h, w)


def apply_model_on_patches(patches):
    masks = []
    for patch in patches:
        original_h, original_w = patch.shape[:2]

        
        patch_resized = cv2.resize(patch, (PATCH_SIZE, PATCH_SIZE))
        augmented = transform(image=patch_resized)
        img_tensor = augmented['image'].unsqueeze(0)
        with torch.no_grad():
            out = model(img_tensor)
            pred = torch.sigmoid(out).squeeze().numpy()


        mask_resized = cv2.resize(pred, (original_w, original_h))
        masks.append(mask_resized)
    return masks


def reconstruct_mask(masks, positions, full_shape):
    height, width = full_shape
    full_mask = np.zeros((height, width), dtype=np.float32)
    weight_sum = np.zeros((height, width), dtype=np.float32)

    for mask, (y, x) in zip(masks, positions):
        h, w = mask.shape
        w_map = weight_map(h, w)
        full_mask[y:y+h, x:x+w] += mask * w_map
        weight_sum[y:y+h, x:x+w] += w_map

    full_mask /= np.maximum(weight_sum, 1e-6)
    return full_mask


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")
    image_np = np.array(image)

    patches, positions, full_shape = split_into_patches(image_np)
    masks = apply_model_on_patches(patches)
    full_mask = reconstruct_mask(masks, positions, full_shape)


    prob_mask = (full_mask * 255).astype(np.uint8)
    pil_mask = Image.fromarray(prob_mask)

    buf = io.BytesIO()
    pil_mask.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
