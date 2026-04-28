import numpy as np

class MetricsCalculator:
    @staticmethod
    def compute(boneMap, tissueMap, phantom, pL):
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
