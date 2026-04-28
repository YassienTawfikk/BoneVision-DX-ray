import numpy as np

class PhantomGenerator:
    SZ = 512

    @classmethod
    def generate(cls, phantom_type):
        sz = cls.SZ
        bone = np.zeros((sz, sz), dtype=np.float32)
        tissue = np.zeros((sz, sz), dtype=np.float32)
        
        y, x = np.ogrid[0:sz, 0:sz]
        cx, cy = sz / 2.0, sz / 2.0
        dx = x - cx
        dy = y - cy
        
        scale = sz / 128.0
        
        if phantom_type == 'ribcage':
            in_body = (dx**2)/((52*scale)**2) + (dy**2)/((44*scale)**2) < 1
            tissue[in_body] = 2.2
            tissue[~in_body] = 0.05
            
            mask1 = (np.abs(dx) < 7*scale) & (np.abs(dy) < 36*scale)
            bone[mask1] = 0.7
            
            rib_ys = [-26*scale, -13*scale, 0, 13*scale, 26*scale]
            for ry in rib_ys:
                ldy = dy - ry
                arcR = np.sqrt(np.maximum(0, (38*scale)**2 - ldy**2))
                mask2 = (np.abs(np.abs(dx) - arcR) < 3.5*scale) & (np.abs(ldy) < 11*scale)
                bone[mask2] = 0.45
                
        elif phantom_type == 'simple':
            r = np.sqrt(dx**2 + dy**2)
            tissue[r < 50*scale] = 2.0
            tissue[r >= 50*scale] = 0.1
            
            mask1 = (dx**2)/((20*scale)**2) + (dy**2)/((32*scale)**2) < 1
            bone[mask1] = 0.65
            mask2 = (dx**2)/((9*scale)**2) + (dy**2)/((9*scale)**2) < 1
            bone[mask2] = 0.35
            
        else: # layers
            tissue[:] = 1.8
            mask1 = np.broadcast_to(((y >= 28*scale) & (y < 44*scale)) | ((y >= 82*scale) & (y < 98*scale)), bone.shape)
            bone[mask1] = 0.55
            mask2 = (np.abs(dx) < 12*scale) & (y >= 18*scale) & (y < 110*scale)
            bone[mask2] = np.maximum(bone[mask2], 0.38)
            
        return {'bone': bone, 'tissue': tissue}
