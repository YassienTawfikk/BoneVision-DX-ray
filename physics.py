import numpy as np
from scipy.ndimage import gaussian_filter

SZ = 128

def mu(E, mat_type):
    x = E / 50.0
    if mat_type == 'bone':
        return 1.8 * (x ** -3) + 0.22 * (x ** -0.5)
    else:
        return 0.38 * (x ** -3) + 0.185 * (x ** -0.5)

def generate_phantom(phantom_type):
    bone = np.zeros((SZ, SZ), dtype=np.float32)
    tissue = np.zeros((SZ, SZ), dtype=np.float32)
    
    y, x = np.ogrid[0:SZ, 0:SZ]
    cx, cy = SZ / 2.0, SZ / 2.0
    dx = x - cx
    dy = y - cy
    
    if phantom_type == 'ribcage':
        in_body = (dx**2)/(52**2) + (dy**2)/(44**2) < 1
        tissue[in_body] = 2.2
        tissue[~in_body] = 0.05
        
        mask1 = (np.abs(dx) < 7) & (np.abs(dy) < 36)
        bone[mask1] = 0.7
        
        rib_ys = [-26, -13, 0, 13, 26]
        for ry in rib_ys:
            ldy = dy - ry
            arcR = np.sqrt(np.maximum(0, 38**2 - ldy**2))
            mask2 = (np.abs(np.abs(dx) - arcR) < 3.5) & (np.abs(ldy) < 11)
            bone[mask2] = 0.45
            
    elif phantom_type == 'simple':
        r = np.sqrt(dx**2 + dy**2)
        tissue[r < 50] = 2.0
        tissue[r >= 50] = 0.1
        
        mask1 = (dx**2)/(20**2) + (dy**2)/(32**2) < 1
        bone[mask1] = 0.65
        mask2 = (dx**2)/(9**2) + (dy**2)/(9**2) < 1
        bone[mask2] = 0.35
        
    else: # layers
        tissue[:] = 1.8
        
        mask1 = np.broadcast_to(((y >= 28) & (y < 44)) | ((y >= 82) & (y < 98)), bone.shape)
        bone[mask1] = 0.55
        
        mask2 = (np.abs(dx) < 12) & (y >= 18) & (y < 110)
        bone[mask2] = np.maximum(bone[mask2], 0.38)
        
    return {'bone': bone, 'tissue': tissue}

def simulate_projection(phantom, E, noise_sigma, scatter):
    bone = phantom['bone']
    tissue = phantom['tissue']
    muB = mu(E, 'bone')
    muT = mu(E, 'tissue')
    
    proj = muB * bone + muT * tissue
    
    if scatter > 0.002:
        blr = gaussian_filter(proj, sigma=8)
        proj += scatter * blr
        
    if noise_sigma > 0.001:
        seed = 12345 + int(round(E * 1000))
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, noise_sigma, proj.shape).astype(np.float32)
        proj += noise
        
    return proj

def decompose(pL, pH, eL, eH):
    muBL = mu(eL, 'bone')
    muTL = mu(eL, 'tissue')
    muBH = mu(eH, 'bone')
    muTH = mu(eH, 'tissue')
    
    det = muBL * muTH - muTL * muBH
    
    boneMap = np.maximum(0, (muTH * pL - muTL * pH) / det)
    tissueMap = np.maximum(0, (-muBH * pL + muBL * pH) / det)
    
    return {
        'boneMap': boneMap,
        'tissueMap': tissueMap,
        'muBL': muBL,
        'muTL': muTL,
        'muBH': muBH,
        'muTH': muTH,
        'det': det
    }

def compute_metrics(boneMap, tissueMap, phantom, pL):
    p_bone = phantom['bone']
    p_tissue = phantom['tissue']
    
    maeBone = np.mean(np.abs(boneMap - p_bone))
    maeTissue = np.mean(np.abs(tissueMap - p_tissue))
    
    mask_bone = p_bone > 0.3
    mask_bg = (p_tissue > 1.5) & (p_bone < 0.05)
    
    boneVals = boneMap[mask_bone]
    bgVals = tissueMap[mask_bg]
    
    mean_bone = np.mean(boneVals) if len(boneVals) > 0 else 0
    mean_bg = np.mean(bgVals) if len(bgVals) > 0 else 0
    std_bg = np.std(bgVals) if len(bgVals) > 0 else 0
    
    cnr = np.abs(mean_bone - mean_bg) / (std_bg + 1e-6)
    snr = np.mean(pL) / (np.std(pL) + 1e-6)
    
    return {
        'maeBone': f"{maeBone:.4f}",
        'maeTissue': f"{maeTissue:.4f}",
        'cnr': f"{cnr:.2f}",
        'snr': f"{snr:.1f}"
    }

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
