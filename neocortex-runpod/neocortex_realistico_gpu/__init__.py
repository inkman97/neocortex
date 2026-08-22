"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    NEOCORTEX-Omega REALISTICO                                ║
║                                                                              ║
║     Cervello biologicamente realistico                                       ║
║                                                                              ║
║     Backend supportati:                                                      ║
║       - NumPy (CPU)                                                          ║
║       - PyTorch (GPU)                                                        ║
║       - Lava-NC (Intel Loihi)                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .brain import RealisticBrain, create_brain

__all__ = ['RealisticBrain', 'create_brain']
