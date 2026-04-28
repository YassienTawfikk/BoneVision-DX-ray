import numpy as np

def apply_colormap(data, cmap_name):
    if data is None:
        return None
    mn = np.min(data)
    mx = np.max(data)
    rng = mx - mn if mx != mn else 1.0
    v = (data - mn) / rng
    v = np.clip(v, 0.0, 1.0)
    
    rgb = np.zeros((*v.shape, 3), dtype=np.uint8)
    
    if cmap_name == 'gray':
        c = (v * 255).astype(np.uint8)
        rgb[..., 0] = c
        rgb[..., 1] = c
        rgb[..., 2] = c
    elif cmap_name == 'xray':
        c = ((1.0 - v) * 255).astype(np.uint8)
        rgb[..., 0] = c
        rgb[..., 1] = c
        rgb[..., 2] = c
    elif cmap_name == 'bone':
        rgb[..., 0] = np.clip(v * 380, 0, 255).astype(np.uint8)
        rgb[..., 1] = np.clip(v * 230 - 40, 0, 255).astype(np.uint8)
        rgb[..., 2] = np.clip(v * 200 - 100, 0, 255).astype(np.uint8)
    elif cmap_name == 'tissue':
        rgb[..., 0] = np.clip(v * 180 - 80, 0, 255).astype(np.uint8)
        rgb[..., 1] = np.clip(v * 230, 0, 255).astype(np.uint8)
        rgb[..., 2] = np.clip(v * 255, 0, 255).astype(np.uint8)
    elif cmap_name == 'hot':
        rgb[..., 0] = (np.clip(v * 3, 0, 1) * 255).astype(np.uint8)
        rgb[..., 1] = (np.clip(v * 3 - 1, 0, 1) * 255).astype(np.uint8)
        rgb[..., 2] = (np.clip(v * 3 - 2, 0, 1) * 255).astype(np.uint8)
    elif cmap_name == 'viridis':
        v2 = v * v
        v3 = v2 * v
        rgb[..., 0] = (np.clip(0.267 - 0.003*v + 1.785*v2 - 1.951*v3, 0, 1) * 255).astype(np.uint8)
        rgb[..., 1] = (np.clip(0.005 + 1.398*v - 0.945*v2 + 0.537*v3, 0, 1) * 255).astype(np.uint8)
        rgb[..., 2] = (np.clip(0.330 + 1.496*v - 2.966*v2 + 1.636*v3, 0, 1) * 255).astype(np.uint8)
    else:
        c = (v * 255).astype(np.uint8)
        rgb[..., 0] = c
        rgb[..., 1] = c
        rgb[..., 2] = c
        
    return rgb
