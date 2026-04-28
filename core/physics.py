import numpy as np
from scipy.ndimage import gaussian_filter

class PhysicsModel:
    @staticmethod
    def mu(E, mat_type):
        x = E / 50.0
        if mat_type == 'bone':
            return 1.8 * (x ** -3) + 0.22 * (x ** -0.5)
        else:
            return 0.38 * (x ** -3) + 0.185 * (x ** -0.5)

    @classmethod
    def simulate_projection(cls, phantom, E, noise_sigma, scatter, base_sz=512):
        bone = phantom['bone']
        tissue = phantom['tissue']
        muB = cls.mu(E, 'bone')
        muT = cls.mu(E, 'tissue')
        
        proj = muB * bone + muT * tissue
        
        if scatter > 0.002:
            blr = gaussian_filter(proj, sigma=8 * (base_sz / 128.0))
            proj += scatter * blr
            
        if noise_sigma > 0.001:
            seed = 12345 + int(round(E * 1000))
            rng = np.random.default_rng(seed)
            noise = rng.normal(0, noise_sigma, proj.shape).astype(np.float32)
            proj += noise
            
        return proj

    @classmethod
    def decompose(cls, pL, pH, eL, eH):
        muBL = cls.mu(eL, 'bone')
        muTL = cls.mu(eL, 'tissue')
        muBH = cls.mu(eH, 'bone')
        muTH = cls.mu(eH, 'tissue')
        
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
