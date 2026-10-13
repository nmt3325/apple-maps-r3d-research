
float * quantf(float *param_1,float *param_2,float *param_3,long param_4,long param_5)

{
  uint uVar1;
  float fVar2;
  byte bVar3;
  float *pfVar4;
  float *pfVar5;
  undefined4 uVar6;
  ulong uVar7;
  float *pfVar8;
  long lVar9;
  ulong uVar10;
  float *pfVar11;
  long lVar12;
  byte *pbVar13;
  long lVar14;
  ulong uVar15;
  long lVar16;
  uint uVar17;
  float *pfVar18;
  float *pfVar19;
  float *pfVar20;
  ulong uVar21;
  ushort *puVar22;
  float fVar23;
  float fVar24;
  undefined1 auVar25 [16];
  ulong uStack_188;
  ulong uStack_180;
  uint uStack_178;
  undefined2 uStack_174;
  undefined1 uStack_172;
  float afStack_170 [64];
  long lStack_70;
  
  lStack_70 = *plRam00000001e016af20;
  pfVar4 = param_1;
  pfVar5 = param_3;
  if ((((param_4 == 0) || (param_3 == (float *)0x0)) || (param_1[6] != 0.0)) ||
     (pfVar4 = (float *)func_0x0001b70d8494(param_1,&uStack_180), uVar15 = uStack_180,
     param_1[6] != 0.0)) goto LAB_1b70afcb8;
  if (param_2 != (float *)0x0) {
    puVar22 = *(ushort **)(param_1 + 2);
    uVar7 = param_4 << 2;
    if (uVar7 < 0x101) {
      pfVar4 = afStack_170;
    }
    else {
      pfVar4 = (float *)func_0x0001b8120b80(uVar7,0x100004052888210);
    }
    if (param_4 * (long)param_3 == 0) {
      pfVar20 = (float *)-(ulong)(uVar15 != 0);
    }
    else if (uVar15 < 2) {
      pfVar20 = (float *)0xfffffffffffffffe;
    }
    else {
      pfVar20 = (float *)0xfffffffffffffffe;
      if ((*puVar22 < 0x100) && ((*puVar22 & 0xff) == 0x25)) {
        uStack_172 = 0;
        uStack_174 = 0;
        uStack_178 = 0;
        if (uVar15 == 2) {
LAB_1b70afde0:
          uStack_172 = 0;
          uStack_174 = 0;
          pfVar20 = (float *)0xffffffffffffffff;
          uStack_178 = 0;
        }
        else {
          bVar3 = (byte)puVar22[1];
          if ((ulong)bVar3 == 0xff) {
            uStack_188 = uVar15 - 0xb;
            if (uVar15 - 2 < 9) {
              pfVar20 = (float *)0xffffffffffffffff;
              goto LAB_1b70affb4;
            }
            uStack_178 = (uint)*(uint7 *)(puVar22 + 2);
            uVar21 = (ulong)*(byte *)((long)puVar22 + 3);
            uStack_172 = (undefined1)puVar22[5];
            uVar10 = (ulong)*(uint7 *)(puVar22 + 2);
            uStack_174 = (undefined2)*(undefined3 *)(puVar22 + 4);
            lVar14 = (long)puVar22 + 0xb;
          }
          else {
            uVar17 = 7;
            if ((bVar3 & 0x40) != 0) {
              uVar17 = 8;
            }
            uVar1 = 6;
            if ((bVar3 & 0x20) != 0) {
              uVar1 = uVar17;
            }
            uVar17 = 5;
            if ((bVar3 & 0x10) != 0) {
              uVar17 = uVar1;
            }
            uVar1 = 4;
            if ((bVar3 & 8) != 0) {
              uVar1 = uVar17;
            }
            uVar17 = 3;
            if ((bVar3 & 4) != 0) {
              uVar17 = uVar1;
            }
            uVar1 = 2;
            if ((bVar3 & 2) != 0) {
              uVar1 = uVar17;
            }
            uVar17 = 1;
            if ((bVar3 & 1) != 0) {
              uVar17 = uVar1;
            }
            pfVar20 = (float *)(ulong)(uVar17 - 1);
            uStack_188 = (long)(uVar15 - 3) - (long)pfVar20;
            if ((float *)(uVar15 - 3) < pfVar20) goto LAB_1b70afde0;
            pfVar5 = pfVar20;
            func_0x0001b8120bb0(&uStack_178,(long)puVar22 + 3);
            lVar14 = (long)puVar22 + 3 + (long)pfVar20;
            uVar21 = ((ulong)uStack_178 << 8 | (ulong)CONCAT12(uStack_172,uStack_174) << 0x28 |
                     (ulong)bVar3) >> (ulong)uVar17;
            uVar10 = uVar21 >> 8;
            uStack_178 = (uint)(uVar21 >> 8);
            uStack_174 = (undefined2)(uVar21 >> 0x28);
            uStack_172 = (undefined1)(uVar21 >> 0x38);
          }
          if (pfVar4 != (float *)0x0) {
            pfVar5 = pfVar4;
            lVar9 = byet(lVar14,uVar21 & 0xff | uVar10 << 8,pfVar4,param_4,4);
            if (lVar9 != param_4) {
              pfVar20 = (float *)0xffffffffffffffff;
              goto LAB_1b70affb4;
            }
            uVar10 = (ulong)CONCAT16(uStack_172,CONCAT24(uStack_174,uStack_178));
          }
          uVar21 = uVar21 & 0xff | uVar10 << 8;
          uVar10 = 0;
          if (uVar21 <= uStack_188) {
            uVar10 = uVar21;
          }
          if (uStack_188 < uVar21) {
            pfVar20 = (float *)0xffffffffffffffff;
          }
          else {
            pfVar5 = param_2;
            pfVar20 = (float *)byet(lVar14 + uVar10,(long)puVar22 + (uVar15 - (lVar14 + uVar10)),
                                    param_2,param_3,uVar7);
          }
        }
LAB_1b70affb4:
        if (0 < (long)param_3) {
          pfVar8 = (float *)0x0;
          pfVar18 = param_2;
          do {
            lVar14 = 0;
            pfVar11 = param_2;
            lVar9 = param_4;
            pfVar19 = pfVar18;
            do {
              param_2 = pfVar11 + 1;
              fVar2 = *pfVar11;
              if ((uint)fVar2 < 0xfffffffd) {
                fVar23 = *(float *)(param_5 + lVar14 * 4) *
                         (float)((int)pfVar4[lVar14] + (int)fVar2);
              }
              else {
                fVar24 = -INFINITY;
                if (fVar2 != -NAN) {
                  fVar24 = INFINITY;
                }
                fVar23 = NAN;
                if (fVar2 != -NAN) {
                  fVar23 = fVar24;
                }
              }
              pfVar18 = pfVar19 + 1;
              *pfVar19 = fVar23;
              lVar14 = lVar14 + 1;
              lVar9 = lVar9 + -1;
              pfVar11 = param_2;
              pfVar19 = pfVar18;
            } while (lVar9 != 0);
            pfVar8 = (float *)((long)pfVar8 + 1);
          } while (pfVar8 != param_3);
        }
      }
    }
    if (pfVar4 != afStack_170) {
      pfVar4 = (float *)func_0x0001b81206e0();
    }
    if (pfVar20 != param_3) {
      param_1[6] = -0.0;
      goto LAB_1b70afcb8;
    }
    if (param_1[6] != 0.0) goto LAB_1b70afcb8;
  }
  if (*(ulong *)(param_1 + 4) < uStack_180) {
    param_1[6] = 2.8026e-45;
  }
  else {
    *(ulong *)(param_1 + 2) = *(long *)(param_1 + 2) + uStack_180;
    *(ulong *)(param_1 + 4) = *(ulong *)(param_1 + 4) - uStack_180;
  }
LAB_1b70afcb8:
  if (*plRam00000001e016af20 == lStack_70) {
    return pfVar4;
  }
  auVar25 = func_0x0001b811fac0();
  lVar14 = auVar25._0_8_;
  if ((*(int *)(lVar14 + 0x18) != 0) || (lVar9 = *(long *)(lVar14 + 0x10), lVar9 == 0)) {
    return (float *)0x0;
  }
  lVar12 = 0;
  uVar17 = 0;
  uVar7 = 0;
  uVar15 = 0;
  pbVar13 = *(byte **)(lVar14 + 8);
  while( true ) {
    bVar3 = *pbVar13;
    lVar16 = lVar9 + lVar12 + -1;
    *(byte **)(lVar14 + 8) = pbVar13 + 1;
    *(long *)(lVar14 + 0x10) = lVar16;
    if ((((int)lVar12 == -9) && ((bVar3 & 0x7e) != 0)) || ((8 < uVar17 && ((char)bVar3 < '\0')))) {
      uVar6 = 0x10;
      goto LAB_1b70b00d4;
    }
    uVar7 = ((ulong)bVar3 & 0x7f) << (uVar15 & 0x3f) | uVar7;
    if (-1 < (char)bVar3) break;
    uVar15 = uVar15 + 7;
    lVar12 = lVar12 + -1;
    uVar17 = uVar17 + 1;
    pbVar13 = pbVar13 + 1;
    if (lVar9 + lVar12 == 0) {
      uVar6 = 2;
LAB_1b70b00d4:
      *(undefined4 *)(lVar14 + 0x18) = uVar6;
      *auVar25._8_8_ = 0;
      return (float *)0x0;
    }
  }
  *auVar25._8_8_ = uVar7;
  if (lVar16 == 0) goto LAB_1b70b0150;
  uVar17 = 0;
  uVar7 = 0;
  uVar15 = 0;
  uVar10 = (lVar9 + lVar12) - 2;
  pbVar13 = *(byte **)(lVar14 + 8);
  do {
    bVar3 = *pbVar13;
    *(byte **)(lVar14 + 8) = pbVar13 + 1;
    *(ulong *)(lVar14 + 0x10) = uVar10;
    if (((uVar17 == 9) && ((bVar3 & 0x7e) != 0)) || ((8 < uVar17 && ((char)bVar3 < '\0')))) {
      uVar6 = 0x10;
      goto LAB_1b70b015c;
    }
    uVar7 = ((ulong)bVar3 & 0x7f) << (uVar15 & 0x3f) | uVar7;
    if (-1 < (char)bVar3) {
      if (uVar7 <= uVar10) {
        lVar9 = *(long *)(lVar14 + 8);
        *(long *)pfVar5 = lVar9;
        *(long *)(pfVar5 + 2) = lVar9;
        *(ulong *)(pfVar5 + 4) = uVar7;
        pfVar5[6] = 0.0;
        if (*(int *)(lVar14 + 0x18) != 0) {
          return (float *)0x0;
        }
        if (uVar7 <= *(ulong *)(lVar14 + 0x10)) {
          *(ulong *)(lVar14 + 8) = lVar9 + uVar7;
          *(ulong *)(lVar14 + 0x10) = *(ulong *)(lVar14 + 0x10) - uVar7;
          return (float *)0x1;
        }
      }
      *(undefined4 *)(lVar14 + 0x18) = 2;
      return (float *)0x0;
    }
    uVar15 = uVar15 + 7;
    uVar10 = uVar10 - 1;
    uVar17 = uVar17 + 1;
    pbVar13 = pbVar13 + 1;
  } while (uVar10 != 0xffffffffffffffff);
LAB_1b70b0150:
  uVar6 = 2;
LAB_1b70b015c:
  *(undefined4 *)(lVar14 + 0x18) = uVar6;
  return (float *)0x0;
}

