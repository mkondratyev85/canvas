"""
Page sizes
"""

SIZE_A3 = (420,297)
SIZE_A2 = (594, 420)
SIZE_A1 = (841, 594)
SIZE_A0 = (1189, 841)

SIZES = {
    "A3": SIZE_A3,
    "A2": SIZE_A2,
    "A1": SIZE_A1,
    "A0": SIZE_A0,
    "A3_": (SIZE_A3[1], SIZE_A3[0]),
    "A2_": (SIZE_A2[1], SIZE_A2[0]),
    "A1_": (SIZE_A1[1], SIZE_A1[0]),
    "A0_": (SIZE_A0[1], SIZE_A0[0]),
}
