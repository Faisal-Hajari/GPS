

I tried to postprocess the tiles coming form the COG. this postporcess did not help with enhancing the images visually. 

```python 
from PIL import Image, ImageOps
def percentile_stretch(data, low=2, high=98):
    """Stretch each band independently between low/high percentiles."""
    result = np.zeros_like(data, dtype=np.uint8)
    for i in range(data.shape[0]):  # per band
        band = data[i].astype(np.float32)
        lo, hi = np.percentile(band, (low, high))
        stretched = (band - lo) / (hi - lo + 1e-6) * 255
        result[i] = np.clip(stretched, 0, 255).astype(np.uint8)
    return result

def gamma_stretch(data, gamma=1.5):
    normalized = data.astype(np.float32) / 255.0
    corrected = np.power(normalized, 1.0 / gamma) * 255
    return np.clip(corrected, 0, 255).astype(np.uint8)

img = Image.fromarray(data.transpose(1, 2, 0))  # (H, W, 3)
img.save("image.png")

img = ImageOps.autocontrast(img, cutoff=2)
img.save("autocontrast_image.png")

data_stretched = percentile_stretch(data, low=2, high=98)
img = Image.fromarray(data_stretched.transpose(1, 2, 0))
img.save("percentile_stretch_image.png")

data_stretched = gamma_stretch(data, gamma=1.5)
img = Image.fromarray(data_stretched.transpose(1, 2, 0))
img.save("gamma_stretch_image.png")

data_stretched = percentile_stretch(data, low=2, high=98)
data_stretched = gamma_stretch(data_stretched, gamma=1.5)
img = Image.fromarray(data_stretched.transpose(1, 2, 0))
img.save("percentile_stretch_and_gamma_stretch_image.png")

print("Saved actual_image.png")
``` 

each collection and provider do thier own structure. for example one can see the image in `item.assets['visual']` and in another you will find it in `item.assets['image']`. mabe we should have different readers for different collections. abstracting this seems like a good idea for the long run.