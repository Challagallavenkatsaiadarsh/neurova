# =========================================
# FILE: backend/ai/image_generator.py
# SAFE + STABLE + NON-BLOCKING VERSION
# =========================================

import os
import uuid
from huggingface_hub import InferenceClient


class ImageGenerator:

    def __init__(self):

        # =========================================
        # TOKEN SAFE LOAD
        # =========================================
        self.token = os.getenv("HF_TOKEN")

        self.client = None

        if self.token:
            try:
                self.client = InferenceClient(token=self.token)
                print("🎨 HuggingFace Image Generator READY")
            except Exception as e:
                print("❌ HF Client init failed:", e)
                self.client = None
        else:
            print("⚠ HF_TOKEN NOT FOUND → Image generation disabled (safe mode)")

        # =========================================
        # MODEL
        # =========================================
        self.model = "stabilityai/stable-diffusion-xl-base-1.0"

        # =========================================
        # OUTPUT DIR
        # =========================================
        self.output_dir = os.path.join("backend", "generated")
        os.makedirs(self.output_dir, exist_ok=True)

        print("🚀 Image Generator initialized (safe mode)")


    # =========================================
    # PROMPT ENHANCER
    # =========================================
    def enhance_prompt(self, prompt: str) -> str:
        return (
            "ultra realistic, cinematic lighting, 8k, highly detailed, "
            "professional photography style, "
            f"{prompt}"
        )


    # =========================================
    # GENERATE MULTIPLE IMAGES (SAFE + TIMEOUT PROTECTION)
    # =========================================
    def generate_multiple(self, prompt: str, num_images: int = 4):

        if not prompt:
            return []

        if not self.client:
            print("⚠ Skipped: HF not configured")
            return []

        enhanced_prompt = self.enhance_prompt(prompt)
        results = []

        try:
            print(f"🖼 Generating {num_images} images...")

            for i in range(min(num_images, 4)):  # LIMIT SAFE

                image = self.client.text_to_image(
                    prompt=enhanced_prompt,
                    model=self.model
                )

                file_name = f"{uuid.uuid4().hex}.png"
                file_path = os.path.join(self.output_dir, file_name)

                image.save(file_path)

                results.append(f"/generated/{file_name}")

            return results

        except Exception as e:
            print("❌ Image generation error:", str(e))
            return []


# =========================================
# SINGLETON
# =========================================
image_generator = ImageGenerator()


def generate_image(prompt: str):
    images = image_generator.generate_multiple(prompt, 1)
    return images[0] if images else None


def generate_images(prompt: str, count: int = 4):
    return image_generator.generate_multiple(prompt, count)
